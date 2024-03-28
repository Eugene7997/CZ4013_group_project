import time
from ipaddress import IPv4Address
from pathlib import Path
from uuid import uuid4

import pytest

from remote_file_system.client_interface import Client
from unittest.mock import Mock, patch

from remote_file_system.message import ModifiedTimestampResponse, ReadFileResponse, WriteFileResponse


class TestClient:
    """
    Unit tests for the client interface. No messages are sent over the network and calls to the server should be mocked.
    """

    @pytest.fixture()
    def client(self):
        cache_working_directory = Path("test_artifacts---test_client_server")
        client = Client(
            client_port_number=9999,
            server_ip_address=IPv4Address("127.0.0.1"),
            server_port_number=1000,
            cache_working_directory=cache_working_directory,
            freshness_interval_in_seconds=10,
        )
        yield client

    @staticmethod
    @patch("remote_file_system.client_interface.send_message")
    def test_read_file_not_in_cache(mock_send_message: Mock, client: Client):
        """
        Expected: No cache entry. Client makes a request to the mock server.
        """
        relative_mock_file_path = Path("mock_file_path")
        client.cache.validation_timestamps = {}
        client.cache.modification_timestamps = {}
        mock_send_message.return_value = ReadFileResponse(
            reply_id=uuid4(),
            content=b"mock_file_content_testing_testing_>>>>>target<<<<<_testing",
            modification_timestamp=3,
        )
        expected = "target"
        actual = client.read_file(
            file_path=relative_mock_file_path,
            offset=39,
            number_of_bytes=6,
        ).decode("utf-8")
        assert actual == expected

    @staticmethod
    @patch("remote_file_system.client_interface.send_message")
    def test_read_file_from_valid_cache_validation_within_freshness_interval(mock_send_message: Mock, client: Client):
        """
        Expected: Validation timestamp is within freshness interval. Client reads from cache directly.
        """
        relative_mock_file_path = Path("mock_file_path")

        current_timestamp: int = int(time.time())
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
        # TODO: work on fixing assert_not_called error.
        # assert mock_send_message.assert_not_called(), "Expected client not to communicate with the server"
        assert actual == expected, "Expected client to read from the valid cache entry"

    @staticmethod
    @patch("remote_file_system.client_interface.Client._get_modification_timestamp_from_server")
    def test_read_file_from_valid_cache_validation_not_within_freshness_interval(
        mock_get_modification_timestamp_from_server: Mock, client: Client
    ):
        relative_mock_file_path = Path("mock_file_path")
        """
        Expected: Validation timestamp is not within freshness interval. Client gets the modification timestamp from the
        mock server. The client's cache copy is still updated and the client reads from the cache.
        """
        ancient_timestamp: int = 1_072_915_200
        client.cache.validation_timestamps[relative_mock_file_path] = ancient_timestamp
        client.cache.modification_timestamps[relative_mock_file_path] = ancient_timestamp

        full_mock_file_path = client.cache.cache_working_directory / relative_mock_file_path
        full_mock_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_mock_file_path, "w") as f:
            f.write("mock_file_content>>>>>target<<<<<")

        mock_get_modification_timestamp_from_server.return_value = ancient_timestamp

        expected = "target"
        actual = client.read_file(
            relative_mock_file_path,
            offset=22,
            number_of_bytes=6,
        ).decode("utf-8")

        assert actual == expected

    @staticmethod
    @patch("remote_file_system.client_interface.send_message")
    def test_read_file_outdated_cache(mock_send_message: Mock, client: Client):
        """
        Expected: Validation timestamp is not within freshness interval. Client gets the modification timestamp from the
        mock server. The client's cache copy is outdated and the client requests a new copy from the server.
        """
        relative_mock_file_path = Path("mock_file_path")
        ancient_timestamp: int = 1_072_915_200
        client.cache.validation_timestamps[relative_mock_file_path] = ancient_timestamp
        client.cache.modification_timestamps[relative_mock_file_path] = ancient_timestamp

        very_recent_timestamp: int = 1_704_067_200
        mock_send_message.side_effect = [
            ModifiedTimestampResponse(
                reply_id=uuid4(),
                is_successful=True,
                modification_timestamp=very_recent_timestamp,
            ),
            ReadFileResponse(
                reply_id=uuid4(),
                content=b"mock_file_content_testing_testing_>>>>>target<<<<<_testing",
                modification_timestamp=very_recent_timestamp,
            ),
        ]

        expected = "target"
        actual = client.read_file(
            file_path=relative_mock_file_path,
            offset=39,
            number_of_bytes=6,
        ).decode("utf-8")

        # TODO: work on fixing assert_not_called error.
        # assert mock_send_message.called == 2, (
        #     "Expected client to check server modification timestamp and" "retrieve the file"
        # )
        assert actual == expected, "Expected client to return updated file just retrieved from server"

    @staticmethod
    @patch("remote_file_system.client_interface.send_message")
    def test_write_file_update_cache(mock_send_message, client: Client):
        relative_mock_file_path = Path("mock_file_path")
        ancient_timestamp: int = 1_072_915_200
        client.cache.validation_timestamps[relative_mock_file_path] = ancient_timestamp
        client.cache.modification_timestamps[relative_mock_file_path] = ancient_timestamp

        full_mock_file_path = client.cache.cache_working_directory / relative_mock_file_path
        full_mock_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_mock_file_path, "wb") as f:
            f.write(b"mock_file_content>>>>>___target<<<<<")

        current_timestamp = int(time.time())
        mock_send_message.return_value = WriteFileResponse(
            reply_id=uuid4(), is_successful=True, modification_timestamp=current_timestamp
        )

        expected = b"mock_file_content>>>>>newtarget<<<<<"
        client.write_file(file_path=relative_mock_file_path, offset=22, number_of_bytes=9, content=b"newtarget")
        with open(full_mock_file_path, "rb") as f:
            actual = f.read()

        assert client.cache.validation_timestamps[relative_mock_file_path] == ancient_timestamp
        assert client.cache.modification_timestamps[relative_mock_file_path] == ancient_timestamp
        assert actual == expected
