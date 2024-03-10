from ipaddress import IPv4Address
from socket import socket, AF_INET, SOCK_DGRAM
from typing import Tuple, List
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
)
from remote_file_system.server_interface import Server


def listen_and_respond_to_messages(server: Server, server_ip_address: IPv4Address, server_port_number: int) -> None:
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
                reply: Message = dispatch_message(server=server, message=incoming_message)
                outgoing_bytes: bytes = reply.marshall()
                number_of_bytes_sent: int = sock.sendto(outgoing_bytes, sender_address)
                logger.debug(f"{number_of_bytes_sent} bytes sent to {sender_ip_address}:{sender_port_number}.")
    finally:
        sock.close()


def dispatch_message(server: Server, message: Message) -> Message:
    # client-initiated requests
    if isinstance(message, ReadFileRequest):
        content: bytes = server.read_file(file_name=message.file_name)
        return ReadFileResponse(
            reply_id=uuid4(),
            content=content,
        )
    elif isinstance(message, WriteFileRequest):
        is_successful, subscribed_clients = server.write_file(
            file_name=message.file_name, offset=message.offset, file_content=message.content
        )
        if is_successful:
            for subscribed_client in subscribed_clients:
                client_ip_address, client_port_number = subscribed_client
                send_update_notification(
                    client_ip_address=client_ip_address, client_port_number=client_port_number, content=message.content
                )
            return WriteFileResponse(reply_id=uuid4(), is_successful=is_successful)
        else:
            return WriteFileResponse(reply_id=uuid4(), is_succesful=False)
    elif isinstance(message, SubscribeToUpdatesRequest):
        isSuccessful: bool = server.subscribe_to_updates(
            client_ip_address=message.client_ip_address,
            client_port_number=message.client_port_number,
            monitoring_interval_in_seconds=message.monitoring_interval,
            file_name=message.file_name,
        )
        return SubscribeToUpdatesResponse(
            is_successful=isSuccessful,
            reply_id=uuid4()
        )
    logger.error("Server received an unrecognised message.")


def send_update_notification(client_ip_address: IPv4Address, client_port_number: int, content: bytes):
    update_notification = UpdateNotification(
        client_ip_address=client_ip_address, client_port_number=client_port_number, content=content
    )
    send_message(
        message=update_notification,
        recipient_ip_address=client_ip_address,
        recipient_port_number=client_port_number,
        max_attempts_to_send_message=3,
        timeout_in_seconds=5,
    )
