from ipaddress import IPv4Address

from cz4013_group_project.message import (
    Message,
    ReadFileRequest,
    WriteFileRequest,
    SubscribeToUpdatesRequest,
    ReadFileResponse,
    WriteFileResponse,
    SubscribeToUpdatesResponse,
    UpdateNotification,
)


class TestReadFileRequest:
    @staticmethod
    def test_marshall_unmarshall():
        read_file_request: ReadFileRequest = ReadFileRequest(
            request_id=123, offset=456, read_bytes=15, filename="random_file_name"
        )
        marshalled_data: bytes = read_file_request.marshall()
        unmarshalled_obj: Message = Message.unmarshall(marshalled_data)
        assert unmarshalled_obj == read_file_request

    @staticmethod
    def test_marshall_unmarshall_without_type_info():
        read_file_request: ReadFileRequest = ReadFileRequest(
            request_id=123, offset=456, read_bytes=15, filename="random_file_name"
        )
        marshalled_data: bytes = read_file_request._marshall_without_type_info()
        unmarshalled_obj: ReadFileRequest = ReadFileRequest._unmarshall_without_type_info(marshalled_data)
        assert unmarshalled_obj == read_file_request


class TestWriteFileRequest:
    @staticmethod
    def test_marshall_unmarshall():
        write_file_request: WriteFileRequest = WriteFileRequest(
            request_id=123, offset=456, file_name="random_file", content=b"random_file_content"
        )
        marshalled_data: bytes = write_file_request.marshall()
        unmarshalled_obj: Message = Message.unmarshall(marshalled_data)
        assert unmarshalled_obj == write_file_request

    @staticmethod
    def test_marshall_unmarshall_without_type_info():
        write_file_request: WriteFileRequest = WriteFileRequest(
            request_id=123, offset=456, file_name="random_file", content=b"random_file_content"
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
            monitoring_interval=15,
            file_name="random_file_name",
            file_name_length=len("random_file_name"),
        )
        marshalled_data: bytes = subscribe_request.marshall()
        unmarshalled_obj: Message = Message.unmarshall(
            marshalled_data
        )
        assert unmarshalled_obj == subscribe_request

    @staticmethod
    def test_marshall_unmarshall_without_type_info():
        subscribe_request: SubscribeToUpdatesRequest = SubscribeToUpdatesRequest(
            client_ip_address=IPv4Address("192.168.255.255"),
            client_port_number=123,
            monitoring_interval=15,
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
        read_file_response: ReadFileResponse = ReadFileResponse(reply_id=123, content="random content")
        marshalled_data: bytes = read_file_response.marshall()
        unmarshalled_obj: Message = Message.unmarshall(marshalled_data)
        assert unmarshalled_obj == read_file_response

    @staticmethod
    def test_marshall_unmarshall_without_type_info():
        read_file_response: ReadFileResponse = ReadFileResponse(reply_id=123, content="random content")
        marshalled_data: bytes = read_file_response._marshall_without_type_info()
        unmarshalled_obj: ReadFileResponse = ReadFileResponse._unmarshall_without_type_info(marshalled_data)
        assert unmarshalled_obj == read_file_response


class TestWriteFileResponse:
    @staticmethod
    def test_marshall_unmarshall():
        write_file_response: WriteFileResponse = WriteFileResponse(reply_id=123, is_successful=False)
        marshalled_data: bytes = write_file_response.marshall()
        unmarshalled_obj: Message = Message.unmarshall(marshalled_data)
        assert unmarshalled_obj == write_file_response

    @staticmethod
    def test_marshall_unmarshall_without_type_info():
        write_file_response: WriteFileResponse = WriteFileResponse(reply_id=123, is_successful=False)
        marshalled_data: bytes = write_file_response._marshall_without_type_info()
        unmarshalled_obj: WriteFileResponse = WriteFileResponse._unmarshall_without_type_info(marshalled_data)
        assert unmarshalled_obj == write_file_response


class TestSubscribeToUpdatesResponse:
    @staticmethod
    def test_marshall_unmarshall():
        subscribe_response: SubscribeToUpdatesResponse = SubscribeToUpdatesResponse(reply_id=123, is_successful=False)
        marshalled_data: bytes = subscribe_response.marshall()
        unmarshalled_obj: Message = Message.unmarshall(
            marshalled_data
        )
        assert unmarshalled_obj == subscribe_response

    @staticmethod
    def test_marshall_unmarshall_without_type_info():
        subscribe_response: SubscribeToUpdatesResponse = SubscribeToUpdatesResponse(reply_id=123, is_successful=False)
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
