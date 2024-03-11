import os
import time
from collections import defaultdict
from ipaddress import IPv4Address
from typing import Dict, Tuple, List


class Server:
    def __init__(self, file_storage_location: str):
        self.subscribed_clients: Dict[str, List[Tuple[int, IPv4Address, int]]] = defaultdict(list)
        self.root_directory: str = file_storage_location
        pass

    def read_file(self, file_name: str) -> bytes:
        file_path = os.path.join(self.root_directory, file_name)

        if not os.path.exists(file_path):
            return None

        with open(file_path, "rb") as file:
            file_contents = file.read()
            return file_contents

    def write_file(self, file_name: str, offset: int, file_content: bytes) -> List[Tuple[IPv4Address, int]]:
        file_path = os.path.join(self.root_directory, file_name)

        if not os.path.exists(file_path):
            return False, None

        with open(file_path, "r+b") as file:
            file.seek(offset)
            file.write(file_content)

        return True, self.subscribed_clients[file_name]

    def subscribe_to_updates(
        self,
        client_ip_address: IPv4Address,
        client_port_number: int,
        monitoring_interval_in_seconds: int,
        file_name: str,
    ) -> bool:
        current_timestamp: int = int(time.time())
        monitoring_expiration_timestamp: int = current_timestamp + monitoring_interval_in_seconds
        subscribed_client: Tuple[int, IPv4Address, int] = (
            monitoring_expiration_timestamp,
            client_ip_address,
            client_port_number,
        )
        self.subscribed_clients[file_name].append(subscribed_client)
        return True
