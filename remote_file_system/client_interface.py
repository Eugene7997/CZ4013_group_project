import time
from socket import socket, AF_INET, SOCK_DGRAM, gethostbyname, gethostname
from ipaddress import IPv4Address
from uuid import uuid4
from loguru import logger
from typing import Tuple

from remote_file_system.message import (
    Message,
    ReadFileRequest,
    ReadFileResponse,
    WriteFileRequest,
    WriteFileResponse,
    SubscribeToUpdatesRequest,
    SubscribeToUpdatesResponse,
    UpdateNotification,
    ModifiedTimestampRequest,
    ModifiedTimestampResponse
)
from remote_file_system.communications import send_message


class Client:
    def __init__(self, client_port_number: int, server_ip_address: IPv4Address, server_port_number: int):
        self.client_ip_address: IPv4Address = gethostbyname(gethostname())
        self.client_port_number: int = client_port_number
        self.server_ip_address: IPv4Address = server_ip_address
        self.server_port_number: int = server_port_number

    def read_file(self, file_name: str, offset: int, number_of_bytes: int) -> bytes:
        # TODO: check cache if file_name exists in cache + within freshness, if yes, return immediately

        outgoing_message: Message = ReadFileRequest(request_id=uuid4(), filename=file_name)
        incoming_message: ReadFileResponse = send_message(
            message=outgoing_message,
            recipient_ip_address=self.server_ip_address,
            recipient_port_number=self.server_port_number,
            max_attempts_to_send_message=3,
            timeout_in_seconds=5,
        )
        entire_file_content: bytes = incoming_message.content
        # TODO cache entire file
        desired_file_content = entire_file_content[offset : offset + number_of_bytes]
        return desired_file_content

    def write_file(self, file_name: str, offset: int, number_of_bytes: int, content: bytes):
        outgoing_message: Message = WriteFileRequest(
            request_id=uuid4(), offset=offset, file_name=file_name, content=content
        )
        incoming_message: WriteFileResponse = send_message(
            message=outgoing_message,
            recipient_ip_address=self.server_ip_address,
            recipient_port_number=self.server_port_number,
            max_attempts_to_send_message=3,
            timeout_in_seconds=5,
        )
        is_successful = incoming_message.is_successful
        if is_successful is not True:
            logger.error("Write Failed. hehe")
        return is_successful

    def subscribe_to_updates(self, file_name: str, monitoring_interval_in_seconds: int, file_name_length: int) -> None:
        outgoing_message: Message = SubscribeToUpdatesRequest(
            client_ip_address=self.client_ip_address,
            # Port number of client
            client_port_number=self.client_port_number,
            file_name_length=file_name_length,
            file_name=file_name,
            monitoring_interval_in_seconds=monitoring_interval_in_seconds,
        )
        incoming_bytes: bytes = send_message(
            message=outgoing_message,
            recipient_ip_address=self.server_ip_address,
            recipient_port_number=self.server_port_number,
            max_attempts_to_send_message=3,
            timeout_in_seconds=5,
        )

        incoming_message: SubscribeToUpdatesResponse = Message.unmarshall(incoming_bytes)
        if incoming_message.is_successful:
            self.listen_for_updates(monitoring_interval_in_seconds)
        else:
            logger.error("Subscribe Failed. hehe")

    def listen_for_updates(self, monitoring_interval_in_seconds: int):
        sock = socket(AF_INET, SOCK_DGRAM)
        client_address: Tuple[str, int] = (str(self.client_ip_address), int(self.client_port_number))
        sock.bind(client_address)

        current_timestamp: int = int(time.time())
        monitoring_expiration_timestamp: int = current_timestamp + monitoring_interval_in_seconds

        try:
            while int(time.time()) <= monitoring_expiration_timestamp:
                logger.info(f"Socket is listening for messages at {self.client_ip_address}:{self.client_port_number}.")
                incoming_bytes, sender_address = sock.recvfrom(4096)
                sender_ip_address, sender_port_number = sender_address
                logger.info(f"Received {len(incoming_bytes)} bytes from {sender_ip_address}:{sender_port_number}.")

                if incoming_bytes:
                    incoming_message: UpdateNotification = Message.unmarshall(incoming_bytes)
                    logger.debug(f"Received {incoming_message.content}.")
        finally:
            sock.close()

    def get_modified_timestamp(self, file_name: str) -> int:
        outgoing_message: Message = ModifiedTimestampRequest(
            request_id=uuid4(),
            file_name=file_name
        )
        incoming_message: ModifiedTimestampResponse = send_message(
            message=outgoing_message,
            recipient_ip_address=self.server_ip_address,
            recipient_port_number=self.server_port_number,
            max_attempts_to_send_message=3,
            timeout_in_seconds=5,
        )
        # TODO: add is_successful check
        return incoming_message.modification_timestamp
