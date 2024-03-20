from ipaddress import IPv4Address
from uuid import uuid4
import time
from remote_file_system.message import (
    Message,
    ReadFileRequest,
    WriteFileRequest,
    SubscribeToUpdatesRequest,
    ReadFileResponse,
    WriteFileResponse,
    SubscribeToUpdatesResponse,
    UpdateNotification,
    ModifiedTimestampRequest,
    ModifiedTimestampResponse,
)


class TestReadFileRequest:
    @staticmethod
    def test_marshall_unmarshall():
        read_file_request: ReadFileRequest = ReadFileRequest(request_id=uuid4(), filename="random_file_name")
        marshalled_data: bytes = read_file_request.marshall()
        unmarshalled_obj: Message = Message.unmarshall(marshalled_data)
        assert unmarshalled_obj == read_file_request

    @staticmethod
    def test_marshall_unmarshall_without_type_info():
        read_file_request: ReadFileRequest = ReadFileRequest(request_id=uuid4(), filename="random_file_name")
        marshalled_data: bytes = read_file_request._marshall_without_type_info()
        unmarshalled_obj: ReadFileRequest = ReadFileRequest._unmarshall_without_type_info(marshalled_data)
        assert unmarshalled_obj == read_file_request


class TestWriteFileRequest:
    @staticmethod
    def test_marshall_unmarshall():
        write_file_request: WriteFileRequest = WriteFileRequest(
            request_id=uuid4(), offset=456, file_name="random_file", content=b"random_file_content"
        )
        marshalled_data: bytes = write_file_request.marshall()
        unmarshalled_obj: Message = Message.unmarshall(marshalled_data)
        assert unmarshalled_obj == write_file_request

    @staticmethod
    def test_marshall_unmarshall_without_type_info():
        write_file_request: WriteFileRequest = WriteFileRequest(
            request_id=uuid4(), offset=456, file_name="random_file", content=b"random_file_content"
        )
        marshalled_data: bytes = write_file_request._marshall_without_type_info()
        unmarshalled_obj: WriteFileRequest = WriteFileRequest._unmarshall_without_type_info(marshalled_data)
        assert unmarshalled_obj == write_file_request


class TestSubscribeToUpdatesRequest:
    @staticmethod
    def test_marshall_unmarshall():
        subscribe_request: SubscribeToUpdatesRequest = SubscribeToUpdatesRequest(
            client_ip_address=IPv4Address("192.168.255.255"),
            client_port_number=123,
            monitoring_interval_in_seconds=15,
            file_name="random_file_name",
            file_name_length=len("random_file_name"),
        )
        marshalled_data: bytes = subscribe_request.marshall()
        unmarshalled_obj: Message = Message.unmarshall(marshalled_data)
        assert unmarshalled_obj == subscribe_request

    @staticmethod
    def test_marshall_unmarshall_without_type_info():
        subscribe_request: SubscribeToUpdatesRequest = SubscribeToUpdatesRequest(
            client_ip_address=IPv4Address("192.168.255.255"),
            client_port_number=123,
            monitoring_interval_in_seconds=15,
            file_name="random_file_name",
            file_name_length=len("random_file_name"),
        )
        marshalled_data: bytes = subscribe_request._marshall_without_type_info()
        unmarshalled_obj: SubscribeToUpdatesRequest = SubscribeToUpdatesRequest._unmarshall_without_type_info(
            marshalled_data
        )
        assert unmarshalled_obj == subscribe_request


class TestReadFileResponse:
    @staticmethod
    def test_marshall_unmarshall():
        read_file_response: ReadFileResponse = ReadFileResponse(reply_id=uuid4(), content=b"random content")
        marshalled_data: bytes = read_file_response.marshall()
        unmarshalled_obj: Message = Message.unmarshall(marshalled_data)
        assert unmarshalled_obj == read_file_response

    @staticmethod
    def test_marshall_unmarshall_without_type_info():
        read_file_response: ReadFileResponse = ReadFileResponse(reply_id=uuid4(), content=b"random content")
        marshalled_data: bytes = read_file_response._marshall_without_type_info()
        unmarshalled_obj: ReadFileResponse = ReadFileResponse._unmarshall_without_type_info(marshalled_data)
        assert unmarshalled_obj == read_file_response


class TestWriteFileResponse:
    @staticmethod
    def test_marshall_unmarshall():
        write_file_response: WriteFileResponse = WriteFileResponse(reply_id=uuid4(), is_successful=False)
        marshalled_data: bytes = write_file_response.marshall()
        unmarshalled_obj: Message = Message.unmarshall(marshalled_data)
        assert unmarshalled_obj == write_file_response

    @staticmethod
    def test_marshall_unmarshall_without_type_info():
        write_file_response: WriteFileResponse = WriteFileResponse(reply_id=uuid4(), is_successful=False)
        marshalled_data: bytes = write_file_response._marshall_without_type_info()
        unmarshalled_obj: WriteFileResponse = WriteFileResponse._unmarshall_without_type_info(marshalled_data)
        assert unmarshalled_obj == write_file_response


class TestSubscribeToUpdatesResponse:
    @staticmethod
    def test_marshall_unmarshall():
        subscribe_response: SubscribeToUpdatesResponse = SubscribeToUpdatesResponse(
            reply_id=uuid4(), is_successful=False
        )
        marshalled_data: bytes = subscribe_response.marshall()
        unmarshalled_obj: Message = Message.unmarshall(marshalled_data)
        assert unmarshalled_obj == subscribe_response

    @staticmethod
    def test_marshall_unmarshall_without_type_info():
        subscribe_response: SubscribeToUpdatesResponse = SubscribeToUpdatesResponse(
            reply_id=uuid4(), is_successful=False
        )
        marshalled_data: bytes = subscribe_response._marshall_without_type_info()
        unmarshalled_obj: SubscribeToUpdatesResponse = SubscribeToUpdatesResponse._unmarshall_without_type_info(
            marshalled_data
        )
        assert unmarshalled_obj == subscribe_response


class TestUpdateNotification:
    @staticmethod
    def test_marshall_unmarshall():
        update_notification: UpdateNotification = UpdateNotification(
            file_name="random_file.txt", content=b"hello world"
        )
        marshalled_data: bytes = update_notification.marshall()
        unmarshalled_obj: Message = Message.unmarshall(marshalled_data)
        assert unmarshalled_obj == update_notification

    @staticmethod
    def test_marshall_unmarshall_without_type_info():
        update_notification: UpdateNotification = UpdateNotification(
            file_name="random_file.txt", content=b"hello world"
        )
        marshalled_data: bytes = update_notification._marshall_without_type_info()
        unmarshalled_obj: UpdateNotification = UpdateNotification._unmarshall_without_type_info(marshalled_data)
        assert unmarshalled_obj == update_notification


class TestModifiedTimestampRequest:
    @staticmethod
    def test_marshall_unmarshall():
        modified_timestamp_request = ModifiedTimestampRequest(file_path="/test/path", request_id=uuid4())
        marshalled_data: bytes = modified_timestamp_request.marshall()
        unmarshalled_data: Message = Message.unmarshall(marshalled_data)
        assert modified_timestamp_request == unmarshalled_data

    @staticmethod
    def test_marshall_unmarshall_without_type_info():
        modified_timestamp_request: ModifiedTimestampRequest = ModifiedTimestampRequest(
            file_path="/test/path", request_id=uuid4()
        )
        marshalled_data: bytes = modified_timestamp_request._marshall_without_type_info()
        unmarshalled_obj: ModifiedTimestampRequest = ModifiedTimestampRequest._unmarshall_without_type_info(
            marshalled_data
        )
        assert unmarshalled_obj == modified_timestamp_request


class TestModifiedTimestampResponse:
    @staticmethod
    def test_marshall_unmarshall():
        modified_timestamp_response: ModifiedTimestampResponse = ModifiedTimestampResponse(
            reply_id=uuid4(), modification_timestamp=int(time.time()), is_successful=False
        )
        marshalled_data: bytes = modified_timestamp_response.marshall()
        unmarshalled_obj: Message = Message.unmarshall(marshalled_data)
        assert unmarshalled_obj == modified_timestamp_response

    @staticmethod
    def test_marshall_unmarshall_without_type_info():
        modified_timestamp_response: ModifiedTimestampResponse = ModifiedTimestampResponse(
            reply_id=uuid4(), modification_timestamp=int(time.time()), is_successful=False
        )
        marshalled_data: bytes = modified_timestamp_response._marshall_without_type_info()
        unmarshalled_obj: ModifiedTimestampResponse = ModifiedTimestampResponse._unmarshall_without_type_info(
            marshalled_data
        )
        assert unmarshalled_obj == modified_timestamp_response
