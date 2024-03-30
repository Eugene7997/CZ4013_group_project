import time
import pytest
import multiprocessing
from ipaddress import IPv4Address
from pathlib import Path
from uuid import uuid4
from unittest.mock import Mock, patch
from loguru import logger

from remote_file_system.client_interface import Client
from remote_file_system.server import Server
from remote_file_system.server_file_system import ServerFileSystem
from remote_file_system.communications import send_message
from remote_file_system.message import (
    ModifiedTimestampResponse,
    ReadFileRequest,
    ReadFileResponse,
    WriteFileRequest,
    WriteFileResponse,
)

class TestNetworkExperiment1:
    """
    Network experiment 1: Simulate network failure.
    """
    SERVER_IP_ADDRESS = IPv4Address("127.0.0.1")
    SERVER_PORT_NUMBER = 12345
    CLIENT_PORT_NUMBER = 9999

    @pytest.fixture()
    def client(self):
        cache_working_directory = Path("test_artifacts---test_client_server")
        client = Client(
            client_port_number=self.CLIENT_PORT_NUMBER,
            server_ip_address=self.SERVER_IP_ADDRESS,
            server_port_number=self.SERVER_PORT_NUMBER,
            cache_working_directory=cache_working_directory,
            freshness_interval_in_seconds=10,
        )
        yield client

    @pytest.fixture(autouse=True)
    def start_server(self):
        server_root_directory: Path = Path.cwd() / "tests" / "server"
        server_file_system = ServerFileSystem(server_root_directory=server_root_directory)
        server = Server(
            server_ip_address=self.SERVER_IP_ADDRESS,
            server_port_number=self.SERVER_PORT_NUMBER,
            file_system=server_file_system,
        )
        server_process = multiprocessing.Process(target=server.listen_for_messages)
        server_process.start()
        yield
        server_process.terminate()

    def test_network_failure(self, server: Server):
        # message 1
        response_1 = send_message(
            message=ReadFileRequest(
                request_id=uuid4(),
                filename="english_alphabets.txt"
            ),
            recipient_ip_address=self.SERVER_IP_ADDRESS,
            recipient_port_number=self.SERVER_PORT_NUMBER,
            max_attempts_to_send_message=3,
            timeout_in_seconds=5
        )
        logger.info("baby baby")
        time.sleep(10)
        # message 2
        response_2 = send_message(
            message=ReadFileRequest(
                request_id=uuid4(),
                filename="english_alphabets.txt"
            ),
            recipient_ip_address=self.SERVER_IP_ADDRESS,
            recipient_port_number=self.SERVER_PORT_NUMBER,
            max_attempts_to_send_message=3,
            timeout_in_seconds=3
        )

        with patch.object(server, 'server_file_system.read_file', wraps=server.server_file_system.read_file) as mock:
            response_1 = send_message(
                message=ReadFileRequest(
                    request_id=uuid4(),
                    filename="english_alphabets.txt"
                ),
                recipient_ip_address=self.SERVER_IP_ADDRESS,
                recipient_port_number=self.SERVER_PORT_NUMBER,
                max_attempts_to_send_message=3,
                timeout_in_seconds=5
            )
            mock.assert_called_once()

        assert response_1 == response_2
