import time
from ipaddress import IPv4Address
from pathlib import Path
from socket import socket, AF_INET, SOCK_DGRAM, gethostbyname, gethostname, timeout
from typing import Tuple
from uuid import uuid4
from loguru import logger

from remote_file_system.client_cache import Cache
from remote_file_system.communications import send_message_and_wait_for_reply
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
    ModifiedTimestampResponse,
    DeleteFileRequest,
    DeleteFileResponse,
    AppendFileRequest,
    AppendFileResponse,
)


class Client:
    def __init__(
        self,
        client_port_number: int,
        server_ip_address: IPv4Address,
        server_port_number: int,
        cache_working_directory: Path,
        freshness_interval_in_seconds: int,
    ):
        self.client_ip_address: IPv4Address = IPv4Address(gethostbyname(gethostname()))
        self.client_port_number: int = client_port_number
        self.server_ip_address: IPv4Address = server_ip_address
        self.server_port_number: int = server_port_number
        self.cache: Cache = Cache(cache_working_directory)
        self.freshness_interval_in_seconds: int = freshness_interval_in_seconds

    def read_file(self, file_path: Path, offset: int, number_of_bytes: int) -> bytes:
        logger.debug(f"Reading {number_of_bytes} bytes from {file_path} at an offset of {offset}.")

        if not self.cache.is_in_cache(file_path):
            logger.debug(f"No cache entry exists for {file_path}.")
            entire_file_content: bytes = self._get_file_from_server(file_path)
            desired_file_content = entire_file_content[offset : offset + number_of_bytes]
            return desired_file_content

        if self._check_validity_on_client(file_path):
            return self.cache.get_file_content(file_path)[offset : offset + number_of_bytes]

        if self._check_validity_on_server(file_path):
            self.cache.validate_cache_for(file_path)
            return self.cache.get_file_content(file_path)[offset : offset + number_of_bytes]

        entire_file_content: bytes = self._get_file_from_server(file_path)
        desired_file_content = entire_file_content[offset : offset + number_of_bytes]
        return desired_file_content

    def _check_validity_on_client(self, file_path: Path) -> bool:
        logger.debug(f"Checking validation timestamp on cache entry for {file_path}.")
        current_timestamp: int = int(time.time())
        validation_timestamp: int = self.cache.get_validation_timestamp(file_path)
        return current_timestamp - validation_timestamp < self.freshness_interval_in_seconds

    def _check_validity_on_server(self, file_path: Path) -> bool:
        logger.debug(f"Checking server modification timestamp on cache entry for {file_path}.")
        cache_modification_timestamp: int = self.cache.get_modification_timestamp(file_path)
        server_modification_timestamp: int = self._get_modification_timestamp_from_server(file_path)
        return cache_modification_timestamp == server_modification_timestamp

    def _get_file_from_server(self, file_path: Path) -> bytes:
        logger.debug(f"Client retrieving {file_path} from server.")
        outgoing_message: Message = ReadFileRequest(request_id=uuid4(), filename=str(file_path))
        incoming_message: ReadFileResponse | None = send_message_and_wait_for_reply(
            message=outgoing_message,
            recipient_ip_address=self.server_ip_address,
            recipient_port_number=self.server_port_number,
            max_attempts_to_send_message=3,
            timeout_in_seconds=5,
        )
        # TODO: Error handling for NoneType for incoming_message
        entire_file_content: bytes = incoming_message.content
        server_modification_timestamp: int = incoming_message.modification_timestamp
        self.cache.put_in_cache(
            file_path=Path(file_path),
            file_content=entire_file_content,
            validation_timestamp=int(time.time()),
            modification_timestamp=server_modification_timestamp,
        )
        return entire_file_content

    def _get_modification_timestamp_from_server(self, file_path: Path) -> int:
        outgoing_message: Message = ModifiedTimestampRequest(request_id=uuid4(), file_path=str(file_path))
        incoming_message: ModifiedTimestampResponse | None = send_message_and_wait_for_reply(
            message=outgoing_message,
            recipient_ip_address=self.server_ip_address,
            recipient_port_number=self.server_port_number,
            max_attempts_to_send_message=3,
            timeout_in_seconds=5,
        )
        if incoming_message.is_successful:
            return incoming_message.modification_timestamp
        else:
            logger.warning("Couldn't get modification timestamp")
            return incoming_message.modification_timestamp

    def write_file(self, file_path: Path, offset: int, content: bytes):
        logger.debug(f"Writing {len(content)} bytes of {content} to {file_path} at an offset of {offset}.")
        outgoing_message: Message = WriteFileRequest(
            request_id=uuid4(), offset=offset, file_name=str(file_path), content=content
        )
        incoming_message: WriteFileResponse | None = send_message_and_wait_for_reply(
            message=outgoing_message,
            recipient_ip_address=self.server_ip_address,
            recipient_port_number=self.server_port_number,
            max_attempts_to_send_message=3,
            timeout_in_seconds=5,
        )
        if not incoming_message:
            logger.warning("Server did not respond to a Write File operation.")
            return
        if not incoming_message.is_successful:
            logger.warning("Server responded that the Write File operation is not successful.")
            return

        if self.cache.is_in_cache(file_path=file_path):
            self.cache.update_cache_after_write(
                file_path=Path(file_path),
                offset=offset,
                file_content=content,
            )

        return incoming_message.is_successful

    def append_file(self, file_path: Path, content: bytes):
        logger.debug(f"Appending {content} to {file_path}.")
        outgoing_message: Message = AppendFileRequest(request_id=uuid4(), file_name=str(file_path), content=content)
        incoming_message: AppendFileResponse | None = send_message_and_wait_for_reply(
            message=outgoing_message,
            recipient_ip_address=self.server_ip_address,
            recipient_port_number=self.server_port_number,
            max_attempts_to_send_message=3,
            timeout_in_seconds=5,
        )
        if not incoming_message:
            logger.warning("Server did not respond to a Append File operation.")
            return
        if not incoming_message.is_successful:
            logger.warning("Server responded that the Append File operation is not successful.")
            return

        if self.cache.is_in_cache(file_path=file_path):
            self.cache.update_cache_after_append(
                file_path=Path(file_path),
                file_content=content,
            )

        return incoming_message.is_successful

    def delete_file_in_server(self, file_path: Path) -> bytes:
        logger.debug(f"Deleting {file_path}.")
        # TODO: Implement delete file in client cache

        outgoing_message: Message = DeleteFileRequest(request_id=uuid4(), filename=str(file_path))
        incoming_message: DeleteFileResponse | None = send_message_and_wait_for_reply(
            message=outgoing_message,
            recipient_ip_address=self.server_ip_address,
            recipient_port_number=self.server_port_number,
            max_attempts_to_send_message=3,
            timeout_in_seconds=5,
        )
        is_successful = incoming_message.is_successful
        if not is_successful:
            logger.warning("Delete Failed. hehe")
        return is_successful

    def subscribe_to_updates(self, file_path: Path, monitoring_interval_in_seconds: int) -> None:
        logger.debug(f"Subscribing to updates to {file_path} for {monitoring_interval_in_seconds} seconds.")
        outgoing_message: Message = SubscribeToUpdatesRequest(
            client_ip_address=self.client_ip_address,
            client_port_number=self.client_port_number,
            file_name_length=len(str(file_path)),
            file_name=str(file_path),
            monitoring_interval_in_seconds=monitoring_interval_in_seconds,
        )
        incoming_message: SubscribeToUpdatesResponse | None = send_message_and_wait_for_reply(
            message=outgoing_message,
            recipient_ip_address=self.server_ip_address,
            recipient_port_number=self.server_port_number,
            max_attempts_to_send_message=3,
            timeout_in_seconds=5,
        )

        if not incoming_message.is_successful:
            logger.warning(f"Client failed to subscribe to updates for {file_path}.")
            return
        self.listen_for_updates(monitoring_interval_in_seconds)

    def listen_for_updates(self, monitoring_interval_in_seconds: int) -> bool:
        sock = socket(AF_INET, SOCK_DGRAM)
        client_address: Tuple[str, int] = (str(self.client_ip_address), int(self.client_port_number))
        sock.bind(client_address)
        sock.settimeout(monitoring_interval_in_seconds)

        try:
            while True:
                logger.info(
                    f"Client is subscribed for updates and waiting at "
                    f"{self.client_ip_address}:{self.client_port_number}."
                )
                incoming_bytes, sender_address = sock.recvfrom(4096)
                sender_ip_address, sender_port_number = sender_address
                logger.info(f"Received {len(incoming_bytes)} bytes from {sender_ip_address}:{sender_port_number}.")

                if incoming_bytes:
                    incoming_message: UpdateNotification = Message.unmarshall(incoming_bytes)
                    logger.debug(f"Received {incoming_message.content}.")
                    server_modification_timestamp: int = incoming_message.modification_timestamp
                    self.cache.put_in_cache(
                        file_path=Path(incoming_message.file_name),
                        file_content=incoming_message.content,
                        validation_timestamp=int(time.time()),
                        modification_timestamp=server_modification_timestamp,
                    )
        except timeout:
            logger.info(
                f"Client has waited for {monitoring_interval_in_seconds} seconds and will no longer listen for updates."
            )
        finally:
            sock.close()
