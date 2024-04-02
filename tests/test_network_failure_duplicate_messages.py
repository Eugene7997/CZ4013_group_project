import threading
import time
import pytest

from ipaddress import IPv4Address
from pathlib import Path
from unittest.mock import Mock, patch
from uuid import uuid4, UUID
from loguru import logger

from remote_file_system.communications import send_message_and_wait_for_reply
from remote_file_system.server import Server, InvocationSemantics
from remote_file_system.server_file_system import ServerFileSystem
from remote_file_system.client_interface import Client
from remote_file_system.message import (
    ReadFileRequest,
    AppendFileRequest,
)

class TestNetworkExperimentDuplicateMessages:

    SERVER_IP_ADDRESS = IPv4Address("127.0.0.1")
    SERVER_PORT_NUMBER = 12345

    def test_network_failure_experiment_1(self):
        """
        Network experiment 1: simulate duplicate of read request message.

        Things to test:
        - Server should invoke the read_file method only once for the first message.
        - Server should use the message history to respond to the second message.

        innovcation     : at least once
        operation type  : idempotent

        """
        server_root_directory: Path = Path.cwd() / "tests" / "server"
        server_file_system = ServerFileSystem(server_root_directory=server_root_directory)
        mock_server_file_system = Mock(wraps=server_file_system)
        server = Server(
            server_ip_address=self.SERVER_IP_ADDRESS,
            server_port_number=self.SERVER_PORT_NUMBER,
            file_system=mock_server_file_system,
            invocation_semantics=InvocationSemantics.AT_LEAST_ONCE
        )
        logger.info("SERVER START")
        server_thread = threading.Thread(target=server.listen_for_messages)
        server_thread.start()

        fixed_uuid: UUID = uuid4()
        logger.info("Sending the first message")
        response_1 = send_message_and_wait_for_reply(
            message=ReadFileRequest(request_id=fixed_uuid, filename="english_alphabets.txt"),
            recipient_ip_address=self.SERVER_IP_ADDRESS,
            recipient_port_number=self.SERVER_PORT_NUMBER,
            max_attempts_to_send_message=3,
            timeout_in_seconds=5,
        )
        time.sleep(2)
        logger.info("Sending the second message")
        response_2 = send_message_and_wait_for_reply(
            message=ReadFileRequest(request_id=fixed_uuid, filename="english_alphabets.txt"),
            recipient_ip_address=self.SERVER_IP_ADDRESS,
            recipient_port_number=self.SERVER_PORT_NUMBER,
            max_attempts_to_send_message=3,
            timeout_in_seconds=3,
        )
        mock_read_file: Mock = mock_server_file_system.read_file
        server.stop_listening()
        server_thread.join()
        assert 2 == mock_read_file.call_count, "Expected server to invoke read_file method twice"
        assert response_1, "Expected server to respond to first message"
        assert response_2, "Expected server to respond to second message"

    def test_network_failure_experiment_2(self):
        """
        Network experiment 2: simulate duplicate of read request message.

        Things to test:
        - Server should invoke the read_file method only once for the first message.
        - Server should use the message history to respond to the second message.

        innovcation     : at most once
        operation type  : idempotent

        """
        server_root_directory: Path = Path.cwd() / "tests" / "server"
        server_file_system = ServerFileSystem(server_root_directory=server_root_directory)
        mock_server_file_system = Mock(wraps=server_file_system)
        server = Server(
            server_ip_address=self.SERVER_IP_ADDRESS,
            server_port_number=self.SERVER_PORT_NUMBER,
            file_system=mock_server_file_system,
            invocation_semantics=InvocationSemantics.AT_MOST_ONCE
        )
        logger.info("SERVER START")
        server_thread = threading.Thread(target=server.listen_for_messages)
        server_thread.start()

        fixed_uuid: UUID = uuid4()
        logger.info("Sending the first message")
        response_1 = send_message_and_wait_for_reply(
            message=ReadFileRequest(request_id=fixed_uuid, filename="english_alphabets.txt"),
            recipient_ip_address=self.SERVER_IP_ADDRESS,
            recipient_port_number=self.SERVER_PORT_NUMBER,
            max_attempts_to_send_message=3,
            timeout_in_seconds=5,
        )
        time.sleep(2)
        logger.info("Sending the second message")
        response_2 = send_message_and_wait_for_reply(
            message=ReadFileRequest(request_id=fixed_uuid, filename="english_alphabets.txt"),
            recipient_ip_address=self.SERVER_IP_ADDRESS,
            recipient_port_number=self.SERVER_PORT_NUMBER,
            max_attempts_to_send_message=3,
            timeout_in_seconds=3,
        )
        mock_read_file: Mock = mock_server_file_system.read_file
        server.stop_listening()
        server_thread.join()
        mock_read_file.assert_called_once(), "Expected server to invoke read_file method only once"
        assert response_1, "Expected server to respond to first message"
        assert response_1 == response_2, "Expected server to use cached reply to respond to the second message"

    def test_network_failure_experiment_5(self):
        """
        Network experiment 5: simulate duplicate of append request message.

        Things to test:
        - Server should invoke the read_file method only once for the first message.
        - Server should use the message history to respond to the second message.

        innovcation     : at most once
        operation type  : non-idempotent

        """
        with open("tests/server/appendme.txt", "w") as file:
            file.write("Hello? Is it me you're looking for?")
        
        with open("tests/server/appendme_appended_once.txt", "w") as file:
            file.write("Hello? Is it me you're looking for?a")

        server_root_directory: Path = Path.cwd() / "tests" / "server"
        server_file_system = ServerFileSystem(server_root_directory=server_root_directory)
        mock_server_file_system = Mock(wraps=server_file_system)
        server = Server(
            server_ip_address=self.SERVER_IP_ADDRESS,
            server_port_number=self.SERVER_PORT_NUMBER,
            file_system=mock_server_file_system,
            invocation_semantics=InvocationSemantics.AT_LEAST_ONCE
        )
        logger.info("SERVER START")
        server_thread = threading.Thread(target=server.listen_for_messages)
        server_thread.start()

        fixed_uuid: UUID = uuid4()
        logger.info("Sending the first message")
        response_1 = send_message_and_wait_for_reply(
            message=AppendFileRequest(request_id=fixed_uuid, file_name="appendme.txt", content=b"a"),
            recipient_ip_address=self.SERVER_IP_ADDRESS,
            recipient_port_number=self.SERVER_PORT_NUMBER,
            max_attempts_to_send_message=3,
            timeout_in_seconds=5,
        )
        time.sleep(1)
        logger.info("Sending the second message")
        response_2 = send_message_and_wait_for_reply(
            message=AppendFileRequest(request_id=fixed_uuid, file_name="appendme.txt", content=b"a"),
            recipient_ip_address=self.SERVER_IP_ADDRESS,
            recipient_port_number=self.SERVER_PORT_NUMBER,
            max_attempts_to_send_message=3,
            timeout_in_seconds=5,
        )
        mock_append_file: Mock = mock_server_file_system.append_file
        server.stop_listening()
        server_thread.join()
        assert 2 == mock_append_file.call_count , "Expected server to invoke append file operation twice"
        assert response_1, "Expected server to respond to first message"
        assert response_2, "Expected server to respond to second message"
        same = open("tests/server/appendme.txt", "rb").read() == open("tests/server/appendme_appended_once.txt", "rb").read() + b"a"
        assert same is True, "Expected original file to be different from the appended file"

    def test_network_failure_experiment_6(self):
        """
        Network experiment 6: simulate duplicate of append request message.

        Things to test:
        - Server should invoke the read_file method only once for the first message.
        - Server should use the message history to respond to the second message.

        innovcation     : at most once
        operation type  : non-idempotent

        """
        with open("tests/server/appendme.txt", "w") as file:
            file.write("Hello? Is it me you're looking for?")

        with open("tests/server/appendme_appended_once.txt", "w") as file:
            file.write("Hello? Is it me you're looking for?a")

        server_root_directory: Path = Path.cwd() / "tests" / "server"
        server_file_system = ServerFileSystem(server_root_directory=server_root_directory)
        mock_server_file_system = Mock(wraps=server_file_system)
        server = Server(
            server_ip_address=self.SERVER_IP_ADDRESS,
            server_port_number=self.SERVER_PORT_NUMBER,
            file_system=mock_server_file_system,
            invocation_semantics=InvocationSemantics.AT_MOST_ONCE
        )
        logger.info("SERVER START")
        server_thread = threading.Thread(target=server.listen_for_messages)
        server_thread.start()

        fixed_uuid: UUID = uuid4()
        logger.info("Sending the first message")
        response_1 = send_message_and_wait_for_reply(
            message=AppendFileRequest(request_id=fixed_uuid, file_name="appendme.txt", content=b"a"),
            recipient_ip_address=self.SERVER_IP_ADDRESS,
            recipient_port_number=self.SERVER_PORT_NUMBER,
            max_attempts_to_send_message=3,
            timeout_in_seconds=5,
        )
        time.sleep(1)
        logger.info("Sending the second message")
        response_2 = send_message_and_wait_for_reply(
            message=AppendFileRequest(request_id=fixed_uuid, file_name="appendme.txt", content=b"a"),
            recipient_ip_address=self.SERVER_IP_ADDRESS,
            recipient_port_number=self.SERVER_PORT_NUMBER,
            max_attempts_to_send_message=3,
            timeout_in_seconds=5,
        )

        mock_append_file: Mock = mock_server_file_system.append_file
        server.stop_listening()
        server_thread.join()
        print(mock_append_file.call_count)
        mock_append_file.assert_called_once() , "Expected server to invoke read_file method only once"
        assert response_1, "Expected server to respond to first message"
        assert response_2, "Expected server to respond to second message"
        assert response_1 == response_2, "Expected server to use cached reply to respond to the second message"
        same = open("tests/server/appendme.txt", "rb").read() == open("tests/server/appendme_appended_once.txt", "rb").read()
        assert same is True, "Expected original file to be the same from the appended file"
