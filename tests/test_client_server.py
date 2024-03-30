import threading
from ipaddress import IPv4Address
from pathlib import Path

import pytest

from remote_file_system.client_interface import Client
from remote_file_system.server import Server
from remote_file_system.server_file_system import ServerFileSystem


class TestClientServer:
    """
    Integration tests between the client and server. Messages are expected to be sent over the network.
    """

    SERVER_IP_ADDRESS = IPv4Address("127.0.0.1")
    SERVER_PORT_NUMBER = 12345

    @pytest.fixture(autouse=True)
    def start_server(self):
        server_root_directory: Path = Path.cwd() / "tests" / "server"
        server_file_system = ServerFileSystem(server_root_directory=server_root_directory)
        server = Server(
            server_ip_address=self.SERVER_IP_ADDRESS,
            server_port_number=self.SERVER_PORT_NUMBER,
            file_system=server_file_system,
        )
        server_thread = threading.Thread(target=server.listen_for_messages)
        server_thread.start()
        yield
        server.stop_listening()
        server_thread.join()

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
        actual = client.read_file(file_path=Path("english_alphabets.txt"), offset=4, number_of_bytes=4)

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

        assert client.write_file(file_path=Path("digits.txt"), offset=1, number_of_bytes=10, content=b"1234567890")
