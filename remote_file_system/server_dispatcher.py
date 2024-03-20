from ipaddress import IPv4Address
from socket import socket, AF_INET, SOCK_DGRAM
from typing import Tuple
from uuid import uuid4

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
)
from remote_file_system.server_interface import Server


def listen_for_messages(server: Server, server_ip_address: IPv4Address, server_port_number: int) -> None:
    sock = socket(AF_INET, SOCK_DGRAM)
    server_address: Tuple[str, int] = (str(server_ip_address), server_port_number)
    sock.bind(server_address)

    try:
        while True:
            logger.info(f"Socket is listening for messages at {server_ip_address}:{server_port_number}.")

            incoming_bytes, sender_address = sock.recvfrom(4096)  # TODO review fixed buffer size
            sender_ip_address, sender_port_number = sender_address
            logger.info(f"Received {len(incoming_bytes)} bytes from {sender_ip_address}:{sender_port_number}.")

            if incoming_bytes:
                incoming_message: Message = Message.unmarshall(incoming_bytes)
                logger.debug(f"Received {incoming_message}.")
                dispatch_message(
                    server=server,
                    message=incoming_message,
                    client_ip_address=IPv4Address(sender_ip_address),
                    client_port_number=sender_port_number,
                )
    finally:
        sock.close()


def dispatch_message(server: Server, message: Message, client_ip_address: IPv4Address, client_port_number: int) -> None:
    # client-initiated requests
    if isinstance(message, ReadFileRequest):
        content: bytes = server.read_file(relative_file_path=message.file_name)
        is_successful, modification_timestamp = server.get_modified_timestamp(message.file_name)
        reply: ReadFileResponse = ReadFileResponse(
            reply_id=uuid4(), content=content, modification_timestamp=modification_timestamp
        )
        send_message(reply, client_ip_address, client_port_number, max_attempts_to_send_message=1, timeout_in_seconds=5)
    elif isinstance(message, WriteFileRequest):
        is_successful, subscribed_clients = server.write_file(
            relative_file_path=message.file_name, offset=message.offset, file_content=message.content
        )
        is_successful, modification_timestamp = server.get_modified_timestamp(message.file_name)

        reply: WriteFileResponse = WriteFileResponse(
            reply_id=uuid4(), is_successful=is_successful, modification_timestamp=modification_timestamp
        )
        send_message(reply, client_ip_address, client_port_number, max_attempts_to_send_message=1, timeout_in_seconds=5)

        if is_successful:
            for subscribed_client in subscribed_clients:
                monitoring_expiration_timestamp, client_ip_address, client_port_number = subscribed_client
                # TODO send update notification below only if current time is before monitoring_expiration_timestamp

                update_notification = UpdateNotification(
                    file_name=message.file_name, content=message.content, modification_timestamp=modification_timestamp
                )
                send_message(
                    message=update_notification,
                    recipient_ip_address=client_ip_address,
                    recipient_port_number=client_port_number,
                    max_attempts_to_send_message=1,
                    timeout_in_seconds=5,
                )
    elif isinstance(message, SubscribeToUpdatesRequest):
        isSuccessful: bool = server.subscribe_to_updates(
            client_ip_address=message.client_ip_address,
            client_port_number=message.client_port_number,
            monitoring_interval_in_seconds=message.monitoring_interval,
            relative_file_path=message.file_name,
        )
        reply: SubscribeToUpdatesResponse = SubscribeToUpdatesResponse(is_successful=isSuccessful, reply_id=uuid4())
        send_message(
            message=reply,
            recipient_ip_address=client_ip_address,
            recipient_port_number=client_port_number,
            max_attempts_to_send_message=1,
            timeout_in_seconds=5,
        )
        return
    elif isinstance(message, ModifiedTimestampRequest):
        is_successful, modification_timestamp = server.get_modified_timestamp(relative_file_path=message.file_path)
        reply: ModifiedTimestampResponse = ModifiedTimestampResponse(
            reply_id=uuid4(), modification_timestamp=modification_timestamp, is_successful=is_successful
        )
        send_message(
            message=reply,
            recipient_ip_address=client_ip_address,
            recipient_port_number=client_port_number,
            max_attempts_to_send_message=1,
            timeout_in_seconds=5,
        )
        if not is_successful:
            logger.error(f"Server failed to check modification timestamp as {message.file_path} does not exist.")
