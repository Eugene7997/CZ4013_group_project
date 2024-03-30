import threading
import time
from ipaddress import IPv4Address
from pathlib import Path
from unittest.mock import Mock
from uuid import uuid4, UUID

from remote_file_system.communications import send_message
from remote_file_system.message import ReadFileRequest
from remote_file_system.server import Server
from remote_file_system.server_file_system import ServerFileSystem


class TestNetworkExperiment1:
    """
    Network experiment 1: Simulate network failure.
    """

    SERVER_IP_ADDRESS = IPv4Address("127.0.0.1")
    SERVER_PORT_NUMBER = 12345

    def test_network_failure(self):
        server_root_directory: Path = Path.cwd() / "tests" / "server"
        server_file_system = ServerFileSystem(server_root_directory=server_root_directory)
        mock_server_file_system = Mock(wraps=server_file_system)
        server = Server(
            server_ip_address=self.SERVER_IP_ADDRESS,
            server_port_number=self.SERVER_PORT_NUMBER,
            file_system=mock_server_file_system,
        )
        server_thread = threading.Thread(target=server.listen_for_messages)
        server_thread.start()

        fixed_uuid: UUID = uuid4()
        response_1 = send_message(
            message=ReadFileRequest(request_id=fixed_uuid, filename="english_alphabets.txt"),
            recipient_ip_address=self.SERVER_IP_ADDRESS,
            recipient_port_number=self.SERVER_PORT_NUMBER,
            max_attempts_to_send_message=3,
            timeout_in_seconds=5,
        )
        time.sleep(3)
        response_2 = send_message(
            message=ReadFileRequest(request_id=fixed_uuid, filename="english_alphabets.txt"),
            recipient_ip_address=self.SERVER_IP_ADDRESS,
            recipient_port_number=self.SERVER_PORT_NUMBER,
            max_attempts_to_send_message=3,
            timeout_in_seconds=3,
        )
        mock_read_file: Mock = mock_server_file_system.read_file
        mock_read_file.assert_called_once()
        server.stop_listening()
        server_thread.join()
        assert response_1, "Expected server to respond to first message"
        assert response_1 == response_2, "Expected server to use cached reply to respond to the second message"
