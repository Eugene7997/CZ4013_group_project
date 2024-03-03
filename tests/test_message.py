from cz4013_group_project.message import Message, ReadFileRequest, WriteFileRequest, SubscribeToUpdatesRequest


class TestMessage:
    @staticmethod
    def test_marshall_unmarshall_read_file_request():
        read_file_request: ReadFileRequest = ReadFileRequest(
            request_id=155, offset=777, read_bytes=15, filename="random_file_name"
        )
        marshalled_data: bytes = read_file_request.marshall()
        unmarshalled_obj: Message = Message.unmarshall(marshalled_data)
        assert unmarshalled_obj == read_file_request

    @staticmethod
    def test_marshall_unmarshall_write_file_request():
        write_file_request: WriteFileRequest = WriteFileRequest(
            request_id=123, offset=456, file_name="random_file", content=b"random_file_content"
        )
        marshalled_data: bytes = write_file_request.marshall()
        unmarshalled_obj: Message = Message.unmarshall(marshalled_data)
        assert unmarshalled_obj == write_file_request


class TestReadFileRequest:
    @staticmethod
    def test_marshall_unmarshall():
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
        marshalled_data: bytes = write_file_request._marshall_without_type_info()
        unmarshalled_obj: WriteFileRequest = WriteFileRequest._unmarshall_without_type_info(marshalled_data)
        assert unmarshalled_obj == write_file_request


class TestSubscribeToUpdatesRequest:
    @staticmethod
    def test_marshall_unmarshall():
        subscribe_request: SubscribeToUpdatesRequest = SubscribeToUpdatesRequest(
            client_ip_address="192.168.255.255",
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
        # TODO write unit test
        assert True


class TestWriteFileResponse:
    @staticmethod
    def test_marshall_unmarshall():
        # TODO write unit test
        assert True
