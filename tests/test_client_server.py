import multiprocessing
import os
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
        server = Server(file_storage_location=os.getcwd())
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
            cache_working_directory=Path("cache"),
            freshness_interval_in_seconds=5,
        )
        expected = "EFGH".encode("utf-8")
        actual = client.read_file(file_path="./tests/mock_data/english_alphabets.txt", offset=4, number_of_bytes=4)
        assert actual == expected
