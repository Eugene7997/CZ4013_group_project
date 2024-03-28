import time
from ipaddress import IPv4Address
from socket import socket, AF_INET, SOCK_DGRAM
from typing import Dict, Tuple
from uuid import uuid4, UUID

from loguru import logger

from remote_file_system.communications import send_message
from remote_file_system.message import (
    Message,
    ReadFileRequest,
    WriteFileRequest,
    ReadFileResponse,
    WriteFileResponse,
    UpdateNotification,
    SubscribeToUpdatesRequest,
    SubscribeToUpdatesResponse,
    ModifiedTimestampRequest,
    ModifiedTimestampResponse,
    DeleteFileRequest,
    DeleteFileResponse,
    AppendFileRequest,
    AppendFileResponse,
)
from remote_file_system.server_file_system import ServerFileSystem


class Server:
    def __init__(self, server_ip_address: IPv4Address, server_port_number: int, file_system: ServerFileSystem):
        self.server_ip_address: IPv4Address = server_ip_address
        self.server_port_number: int = server_port_number
        self.server_file_system: ServerFileSystem = file_system
        # store request id as key. value is the Message
        self.message_history: Dict[UUID, Message] = {}

    def listen_for_messages(self) -> None:
        sock = socket(AF_INET, SOCK_DGRAM)
        server_address: Tuple[str, int] = (str(self.server_ip_address), self.server_port_number)
        sock.bind(server_address)

        try:
            while True:
                logger.info(f"Socket is listening for messages at {self.server_ip_address}:{self.server_port_number}.")

                incoming_bytes, sender_address = sock.recvfrom(4096)  # TODO review fixed buffer size
                sender_ip_address, sender_port_number = sender_address
                logger.info(f"Received {len(incoming_bytes)} bytes from {sender_ip_address}:{sender_port_number}.")

                if incoming_bytes:
                    incoming_message: Message = Message.unmarshall(incoming_bytes)
                    logger.debug(f"Received {incoming_message}.")
                    self._dispatch_message(
                        message=incoming_message,
                        client_ip_address=IPv4Address(sender_ip_address),
                        client_port_number=sender_port_number,
                    )
        finally:
            sock.close()

    def _dispatch_message(self, message: Message, client_ip_address: IPv4Address, client_port_number: int) -> None:
        if self._check_for_duplicate_request_message(message):
            logger.info(f"Duplicate request message detected: {message}")
            reply = self._get_message_from_history(message.request_id)
            logger.info(f"Sending message from history: {reply}")
            send_message(
                reply, client_ip_address, client_port_number, max_attempts_to_send_message=1, timeout_in_seconds=5
            )
            return

        if isinstance(message, ReadFileRequest):
            content: bytes = self.server_file_system.read_file(relative_file_path=message.file_name)
            is_successful, modification_timestamp = self.server_file_system.get_modified_timestamp(message.file_name)
            reply: ReadFileResponse = ReadFileResponse(
                reply_id=uuid4(), content=content, modification_timestamp=modification_timestamp
            )
            self._add_message_to_history(message.request_id, reply)
            send_message(
                reply, client_ip_address, client_port_number, max_attempts_to_send_message=1, timeout_in_seconds=5
            )
        elif isinstance(message, WriteFileRequest):
            is_successful, subscribed_clients = self.server_file_system.write_file(
                relative_file_path=message.file_name, offset=message.offset, file_content=message.content
            )
            is_successful, modification_timestamp = self.server_file_system.get_modified_timestamp(message.file_name)
            reply: WriteFileResponse = WriteFileResponse(
                reply_id=uuid4(), is_successful=is_successful, modification_timestamp=modification_timestamp
            )
            self._add_message_to_history(message.request_id, reply)
            send_message(
                reply, client_ip_address, client_port_number, max_attempts_to_send_message=1, timeout_in_seconds=5
            )
            if is_successful:
                curr_time = int(time.time())
                for subscribed_client in subscribed_clients:
                    # TODO: send update notification below only if
                    #       current time is before monitoring_expiration_timestamp
                    #       I am not sure about the delays between each subscribed client, so just put a curr time

                    # TODO: I am not sure if at most one invocation semantics applies here.
                    #       I will skip the implementation of it for now.

                    if subscribed_client.monitoring_expiration_timestamp > curr_time:
                        update_notification = UpdateNotification(
                            file_name=message.file_name,
                            content=message.content,
                            modification_timestamp=modification_timestamp,
                        )
                        send_message(
                            message=update_notification,
                            recipient_ip_address=subscribed_client.ip_address,
                            recipient_port_number=subscribed_client.port_number,
                            max_attempts_to_send_message=1,
                            timeout_in_seconds=5,
                        )
        elif isinstance(message, SubscribeToUpdatesRequest):
            isSuccessful: bool = self.server_file_system.subscribe_to_updates(
                client_ip_address=message.client_ip_address,
                client_port_number=message.client_port_number,
                monitoring_interval_in_seconds=message.monitoring_interval,
                relative_file_path=message.file_name,
            )
            reply: SubscribeToUpdatesResponse = SubscribeToUpdatesResponse(is_successful=isSuccessful, reply_id=uuid4())
            self._add_message_to_history(message.request_id, reply)
            send_message(
                message=reply,
                recipient_ip_address=client_ip_address,
                recipient_port_number=client_port_number,
                max_attempts_to_send_message=1,
                timeout_in_seconds=5,
            )
        elif isinstance(message, ModifiedTimestampRequest):
            is_successful, modification_timestamp = self.server_file_system.get_modified_timestamp(
                relative_file_path=message.file_path
            )
            reply: ModifiedTimestampResponse = ModifiedTimestampResponse(
                reply_id=uuid4(), modification_timestamp=modification_timestamp, is_successful=is_successful
            )
            self._add_message_to_history(message.request_id, reply)
            if not is_successful:
                logger.error(f"Server failed to check modification timestamp as {message.file_path} does not exist.")
            send_message(
                message=reply,
                recipient_ip_address=client_ip_address,
                recipient_port_number=client_port_number,
                max_attempts_to_send_message=1,
                timeout_in_seconds=5,
            )

        elif isinstance(message, DeleteFileRequest):
            is_successful = self.server_file_system.delete_file(file_name=message.file_name)
            reply: DeleteFileResponse = DeleteFileResponse(reply_id=uuid4(), is_successful=is_successful)
            self._add_message_to_history(message.request_id, reply)
            send_message(
                message=reply,
                recipient_ip_address=client_ip_address,
                recipient_port_number=client_port_number,
                max_attempts_to_send_message=1,
                timeout_in_seconds=5,
            )
        elif isinstance(message, AppendFileRequest):
            is_successful, subscribed_clients = self.server_file_system.append_file(
                relative_file_path=message.file_name, file_content=message.content
            )
            is_successful, modification_timestamp = self.server_file_system.get_modified_timestamp(message.file_name)

            reply: AppendFileResponse = AppendFileResponse(
                reply_id=uuid4(), is_successful=is_successful, modification_timestamp=modification_timestamp
            )
            self._add_message_to_history(message.request_id, reply)
            send_message(
                reply, client_ip_address, client_port_number, max_attempts_to_send_message=1, timeout_in_seconds=5
            )
            if is_successful:
                curr_time = int(time.time())
                for subscribed_client in subscribed_clients:
                    # TODO send update notification below only if current time is before monitoring_expiration_timestamp
                    # I am not sure about the delays between each subscribed client, so just put a curr time

                    # TODO: I am not sure if at most one invocation semantics applies here.
                    #       I will skip the implementation of it for now.

                    if subscribed_client.monitoring_expiration_timestamp > curr_time:
                        update_notification = UpdateNotification(
                            file_name=message.file_name,
                            content=message.content,
                            modification_timestamp=modification_timestamp,
                        )
                        send_message(
                            message=update_notification,
                            recipient_ip_address=subscribed_client.ip_address,
                            recipient_port_number=subscribed_client.port_number,
                            max_attempts_to_send_message=1,
                            timeout_in_seconds=5,
                        )

    def _check_for_duplicate_request_message(self, request_message: Message) -> bool:
        if request_message.request_id in self.message_history:
            return True
        return False

    def _add_message_to_history(self, request_id: uuid4, response_message: Message) -> None:
        self.message_history[request_id] = response_message

    def _remove_message_from_history(self, request_id: uuid4) -> None:
        del self.message_history[request_id]

    def _get_message_from_history(self, request_id: uuid4) -> Message:
        return self.message_history[request_id]
