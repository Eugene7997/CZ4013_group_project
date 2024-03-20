import os
import time
from collections import defaultdict
from ipaddress import IPv4Address
from typing import Dict, Tuple, List

from loguru import logger


class Server:
    def __init__(self, server_root_directory: str):
        # TODO change subscribed_client into a class or named tuple
        self.subscribed_clients: Dict[str, List[Tuple[int, IPv4Address, int]]] = defaultdict(list)
        self.server_root_directory: str = server_root_directory

    def read_file(self, relative_file_path: str) -> bytes:
        full_file_path = os.path.join(self.server_root_directory, relative_file_path)

        if not os.path.exists(full_file_path):
            logger.warning(f"Server failed to perform a read file operation as no file exists at {full_file_path}")
            return None

        with open(full_file_path, "rb") as file:
            file_contents = file.read()
            return file_contents

    def write_file(self, relative_file_path: str, offset: int, file_content: bytes) -> List[Tuple[IPv4Address, int]]:
        full_file_path = os.path.join(self.server_root_directory, relative_file_path)

        if not os.path.exists(full_file_path):
            logger.warning(f"Server failed to perform a write file operation as no file exists at {full_file_path}")
            return False, None

        with open(full_file_path, "r+b") as file:
            file.seek(offset)
            file.write(file_content)

        return True, self.subscribed_clients[relative_file_path]

    def get_modified_timestamp(self, relative_file_path: str) -> Tuple[bool, int]:
        full_file_path = os.path.join(self.server_root_directory, relative_file_path)

        if not os.path.exists(full_file_path):
            logger.warning(
                f"Server failed to check a file modification timestamp as no file exists at {full_file_path}"
            )
            return False, None

        modification_timestamp: int = int(os.path.getmtime(full_file_path))
        return True, modification_timestamp

    def subscribe_to_updates(
        self,
        client_ip_address: IPv4Address,
        client_port_number: int,
        monitoring_interval_in_seconds: int,
        relative_file_path: str,
    ) -> bool:
        current_timestamp: int = int(time.time())
        monitoring_expiration_timestamp: int = current_timestamp + monitoring_interval_in_seconds
        subscribed_client: Tuple[int, IPv4Address, int] = (
            monitoring_expiration_timestamp,
            client_ip_address,
            client_port_number,
        )
        self.subscribed_clients[relative_file_path].append(subscribed_client)
        return True
