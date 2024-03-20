import multiprocessing
from ipaddress import IPv4Address
from pathlib import Path

import pytest

from remote_file_system.client_interface import Client
from remote_file_system.server_dispatcher import listen_and_respond_to_messages
from remote_file_system.server_interface import Server


class TestClientServer:
    SERVER_IP_ADDRESS = IPv4Address("127.0.0.1")
    SERVER_PORT_NUMBER = 12345

    @pytest.fixture(autouse=True)
    def start_server(self):
        server = Server(server_root_directory=Path.cwd() / "tests" / "server")
        server_process = multiprocessing.Process(
            target=listen_and_respond_to_messages, args=(server, self.SERVER_IP_ADDRESS, self.SERVER_PORT_NUMBER)
        )
        server_process.start()
        yield
        server_process.terminate()

    def test_read_file(self):
        CLIENT_PORT_NUMBER = 9999

        client = Client(
            client_port_number=CLIENT_PORT_NUMBER,
            server_ip_address=self.SERVER_IP_ADDRESS,
            server_port_number=self.SERVER_PORT_NUMBER,
            cache_working_directory=Path("tests/client_1_cache"),
            freshness_interval_in_seconds=5,
        )
        expected = "EFGH".encode("utf-8")
        actual = client.read_file(file_path="english_alphabets.txt", offset=4, number_of_bytes=4)
        assert actual == expected

    def test_write_file(self):
        CLIENT_PORT_NUMBER = 9999

        client = Client(
            client_port_number=CLIENT_PORT_NUMBER,
            server_ip_address=self.SERVER_IP_ADDRESS,
            server_port_number=self.SERVER_PORT_NUMBER,
            cache_working_directory=Path("tests/client_2_cache"),
            freshness_interval_in_seconds=5,
        )

        assert client.write_file(file_path="digits.txt", offset=1, number_of_bytes=10, content=b"1234567890")
