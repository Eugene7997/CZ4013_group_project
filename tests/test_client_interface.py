import time
from ipaddress import IPv4Address
from pathlib import Path

import pytest

from remote_file_system.client_interface import Client


class TestClient:
    @pytest.fixture()
    def client(self):
        cache_working_directory = Path("test_client_server---test_read_file_from_valid_cache")
        client = Client(
            client_port_number=9999,
            server_ip_address=IPv4Address("127.0.0.1"),
            server_port_number=1000,
            cache_working_directory=cache_working_directory,
            freshness_interval_in_seconds=10,
        )
        yield client

    @staticmethod
    def test_read_file_from_valid_cache(client: Client):
        current_timestamp: int = int(time.time())
        relative_mock_file_path = Path("mock_file_path")
        client.cache.validation_timestamps[relative_mock_file_path] = current_timestamp
        client.cache.modification_timestamps[relative_mock_file_path] = current_timestamp
        full_mock_file_path = client.cache.cache_working_directory / relative_mock_file_path
        full_mock_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_mock_file_path, "w") as f:
            f.write("mock_file_content>>>>>target<<<<<")

        expected = "target"
        actual = client.read_file(
            file_path=relative_mock_file_path,
            offset=22,
            number_of_bytes=6,
        ).decode("utf-8")
        assert actual == expected
