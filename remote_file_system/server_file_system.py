import os
import time
from collections import defaultdict
from ipaddress import IPv4Address
from pathlib import Path
from typing import Dict, Tuple, List
from typing import Optional

from loguru import logger


class SubscribedClient:
    def __init__(self, monitoring_expiration_timestamp: int, ip_address: IPv4Address, port_number: int):
        self.monitoring_expiration_timestamp = monitoring_expiration_timestamp
        self.ip_address = ip_address
        self.port_number = port_number


class ServerFileSystem:
    def __init__(self, server_root_directory: Path):
        self.subscribed_clients: Dict[str, List[SubscribedClient]] = defaultdict(list)
        self.server_root_directory: Path = server_root_directory

    def read_file(self, relative_file_path: str) -> Optional[bytes]:
        full_file_path = os.path.join(self.server_root_directory, relative_file_path)

        if not os.path.exists(full_file_path):
            logger.warning(f"Server failed to perform a read file operation as no file exists at {full_file_path}")
            return None

        with open(full_file_path, "rb") as file:
            file_contents = file.read()
            return file_contents

    def write_file(
        self, relative_file_path: str, offset: int, file_content: bytes
    ) -> Tuple[bool, Optional[List[SubscribedClient]]]:
        full_file_path = os.path.join(self.server_root_directory, relative_file_path)

        if not os.path.exists(full_file_path):
            logger.warning(f"Server failed to perform a write file operation as no file exists at {full_file_path}")
            return False, None

        with open(full_file_path, "r+b") as file:
            file.seek(offset)
            file.write(file_content)

        return True, self.subscribed_clients[relative_file_path]

    def get_modified_timestamp(self, relative_file_path: str) -> Tuple[bool, Optional[int]]:
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

        subscribed_client: SubscribedClient = SubscribedClient(
            monitoring_expiration_timestamp=monitoring_expiration_timestamp,
            ip_address=client_ip_address,
            port_number=client_port_number,
        )
        logger.info(f"subscribed_client: {self.subscribed_clients}")
        self.subscribed_clients[relative_file_path].append(subscribed_client)
        return True

    def delete_file(self, file_name: str) -> bool:
        file_path = os.path.join(self.server_root_directory, file_name)
        if not os.path.exists(file_path):
            return False
        os.remove(file_path)
        return True
