import time
from enum import Enum
from ipaddress import IPv4Address
import socket
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


class InvocationSemantics(Enum):
    AT_LEAST_ONCE = 0
    AT_MOST_ONCE = 1


class Server:
    def __init__(
        self,
        server_ip_address: IPv4Address,
        server_port_number: int,
        file_system: ServerFileSystem,
        invocation_semantics: InvocationSemantics = InvocationSemantics.AT_LEAST_ONCE,
    ):
        self.server_ip_address: IPv4Address = server_ip_address
        self.server_port_number: int = server_port_number
        self.server_file_system: ServerFileSystem = file_system
        # store request id as key. value is the Message
        self.message_history: Dict[UUID, Message] = {}
        self.invocation_semantics = invocation_semantics
        self.keep_listening = True

    def stop_listening(self) -> None:
        self.keep_listening = False

    def listen_for_messages(self) -> None:
        sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            server_address: Tuple[str, int] = (str(self.server_ip_address), self.server_port_number)
            sock.bind(server_address)

            SERVER_TIMEOUT_IN_SECONDS = 5
            sock.settimeout(SERVER_TIMEOUT_IN_SECONDS)

            while self.keep_listening:
                try:
                    logger.info(
                        f"Socket is listening for messages at {self.server_ip_address}:{self.server_port_number}."
                    )
                    incoming_bytes, sender_address = sock.recvfrom(4096)
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
                except TimeoutError as e:
                    logger.debug(f"Server did not receive messages after {SERVER_TIMEOUT_IN_SECONDS} seconds: {e}")
                    pass

        finally:
            sock.close()

    def _dispatch_message(self, message: Message, client_ip_address: IPv4Address, client_port_number: int) -> None:
        if self.invocation_semantics == InvocationSemantics.AT_MOST_ONCE:
            if self._check_for_duplicate_request_message(message):
                logger.info(f"Duplicate request message detected: {message}")
                reply: Message = self._get_message_from_history(message.request_id)
                logger.info(f"Sending message from history: {reply}")
                send_message(reply, client_ip_address, client_port_number)
                return

        if isinstance(message, ReadFileRequest):
            content: bytes | None = self.server_file_system.read_file(relative_file_path=message.file_name)
            is_successful, modification_timestamp = self.server_file_system.get_modified_timestamp(message.file_name)
            if not content or not is_successful:
                reply: ReadFileResponse = ReadFileResponse(reply_id=uuid4(), content=b"", modification_timestamp=0)
                self._add_message_to_history(message.request_id, reply)
                send_message(reply, client_ip_address, client_port_number)
                return
            reply: ReadFileResponse = ReadFileResponse(
                reply_id=uuid4(), content=content, modification_timestamp=modification_timestamp
            )
            self._add_message_to_history(message.request_id, reply)
            send_message(reply, client_ip_address, client_port_number)
        elif isinstance(message, WriteFileRequest):
            write_is_successful, subscribed_clients = self.server_file_system.write_file(
                relative_file_path=message.file_name, offset=message.offset, file_content=message.content
            )
            get_modification_timestamp_is_successful, modification_timestamp = (
                self.server_file_system.get_modified_timestamp(message.file_name)
            )
            if not write_is_successful or not get_modification_timestamp_is_successful:
                reply: WriteFileResponse = WriteFileResponse(
                    reply_id=uuid4(), is_successful=False, modification_timestamp=0
                )
                self._add_message_to_history(message.request_id, reply)
                send_message(reply, client_ip_address, client_port_number)
                return
            reply: WriteFileResponse = WriteFileResponse(
                reply_id=uuid4(), is_successful=True, modification_timestamp=modification_timestamp
            )
            self._add_message_to_history(message.request_id, reply)
            send_message(reply, client_ip_address, client_port_number)
            if write_is_successful:
                curr_time = int(time.time())
                for subscribed_client in subscribed_clients:
                    if subscribed_client.monitoring_expiration_timestamp > curr_time:
                        update_notification = UpdateNotification(
                            file_name=message.file_name,
                            # content=message.content,
                            content=self.server_file_system.read_file(relative_file_path=message.file_name),
                            modification_timestamp=modification_timestamp,
                        )
                        send_message(
                            message=update_notification,
                            recipient_ip_address=subscribed_client.ip_address,
                            recipient_port_number=subscribed_client.port_number,
                        )
        elif isinstance(message, SubscribeToUpdatesRequest):
            is_successful: bool = self.server_file_system.subscribe_to_updates(
                client_ip_address=message.client_ip_address,
                client_port_number=message.client_port_number,
                monitoring_interval_in_seconds=message.monitoring_interval,
                relative_file_path=message.file_name,
            )
            reply: SubscribeToUpdatesResponse = SubscribeToUpdatesResponse(
                is_successful=is_successful, reply_id=uuid4()
            )
            self._add_message_to_history(message.request_id, reply)
            send_message(
                message=reply,
                recipient_ip_address=client_ip_address,
                recipient_port_number=client_port_number,
            )
        elif isinstance(message, ModifiedTimestampRequest):
            is_successful, modification_timestamp = self.server_file_system.get_modified_timestamp(
                relative_file_path=message.file_path
            )
            if not is_successful:
                logger.warning(f"Server failed to check modification timestamp as {message.file_path} does not exist.")
                reply: ModifiedTimestampResponse = ModifiedTimestampResponse(
                    reply_id=uuid4(), modification_timestamp=0, is_successful=False
                )
                self._add_message_to_history(message.request_id, reply)
                send_message(
                    message=reply, recipient_ip_address=client_ip_address, recipient_port_number=client_port_number
                )

            reply: ModifiedTimestampResponse = ModifiedTimestampResponse(
                reply_id=uuid4(), modification_timestamp=modification_timestamp, is_successful=is_successful
            )
            self._add_message_to_history(message.request_id, reply)
            send_message(
                message=reply, recipient_ip_address=client_ip_address, recipient_port_number=client_port_number
            )
        elif isinstance(message, DeleteFileRequest):
            is_successful = self.server_file_system.delete_file(file_name=message.file_name)
            reply: DeleteFileResponse = DeleteFileResponse(reply_id=uuid4(), is_successful=is_successful)
            self._add_message_to_history(message.request_id, reply)
            send_message(
                message=reply,
                recipient_ip_address=client_ip_address,
                recipient_port_number=client_port_number,
            )
        elif isinstance(message, AppendFileRequest):
            append_is_successful, subscribed_clients = self.server_file_system.append_file(
                relative_file_path=message.file_name, file_content=message.content
            )
            get_modification_timestamp_is_successful, modification_timestamp = (
                self.server_file_system.get_modified_timestamp(message.file_name)
            )
            if not append_is_successful or not get_modification_timestamp_is_successful:
                reply: AppendFileResponse = AppendFileResponse(
                    reply_id=uuid4(), is_successful=False, modification_timestamp=0
                )
                self._add_message_to_history(message.request_id, reply)
                send_message(reply, client_ip_address, client_port_number)
                return
            reply: AppendFileResponse = AppendFileResponse(
                reply_id=uuid4(), is_successful=True, modification_timestamp=modification_timestamp
            )
            self._add_message_to_history(message.request_id, reply)
            send_message(reply, client_ip_address, client_port_number)
            if append_is_successful:
                curr_time = int(time.time())
                for subscribed_client in subscribed_clients:
                    if subscribed_client.monitoring_expiration_timestamp > curr_time:
                        update_notification = UpdateNotification(
                            file_name=message.file_name,
                            # content=message.content,
                            content=self.server_file_system.read_file(relative_file_path=message.file_name),
                            modification_timestamp=modification_timestamp,
                        )
                        send_message(
                            message=update_notification,
                            recipient_ip_address=subscribed_client.ip_address,
                            recipient_port_number=subscribed_client.port_number,
                        )

    def _check_for_duplicate_request_message(self, request_message: Message) -> bool:
        return request_message.request_id in self.message_history

    def _add_message_to_history(self, request_id: UUID, response_message: Message) -> None:
        self.message_history[request_id] = response_message

    def _remove_message_from_history(self, request_id: UUID) -> None:
        del self.message_history[request_id]

    def _get_message_from_history(self, request_id: UUID) -> Message:
        return self.message_history[request_id]
