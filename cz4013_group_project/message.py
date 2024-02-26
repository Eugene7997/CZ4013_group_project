import socket


class Message:
    def __init__(self, message_type_identifier: int):
        self.message_type_identifier: int = message_type_identifier

    def marshall(self) -> bytes:
        message_type_identifier = self.message_type_identifier.to_bytes(4, "big")
        return message_type_identifier

    @staticmethod
    def unmarshall(content: bytes) -> "Message":
        class_identifier = int.from_bytes(content[0:4])
        if class_identifier == 1:
            return ReadFileRequest.unmarshall(content[4:])
        elif class_identifier == 2:
            return WriteFileRequest.unmarshall(content[4:])
        elif class_identifier == 3:
            return SubscribeToUpdatesRequest.unmarshall(content[4:])
        elif class_identifier == 4:
            return ReadFileResponse.unmarshall(content[4:])
        elif class_identifier == 5:
            return WriteFileResponse.unmarshall(content[4:])


# Client
class ReadFileRequest(Message):
    def __init__(self, request_id: int, offset: int, read_bytes: int, filename: str):
        super().__init__(1)
        self.request_id: int = request_id
        self.offset: int = offset
        self.read_bytes: int = read_bytes
        self.file_name: str = filename

    def marshall(self) -> bytes:
        file_name: bytearray = bytearray(self.file_name, encoding="utf-8")
        file_name_length: bytes = len(file_name).to_bytes(4, "big")
        request_id: bytes = self.request_id.to_bytes(4, "big")
        offset: bytes = self.offset.to_bytes(4, "big")
        read_bytes: bytes = self.read_bytes.to_bytes(4, "big")
        # return request_id + offset + read_bytes + file_name_length + file_name
        return super().marshall() + request_id + offset + read_bytes + file_name_length + file_name

    @staticmethod
    def unmarshall(content: bytes) -> "ReadFileRequest":
        request_id: int = int.from_bytes(content[0:4], "big")
        offset: int = int.from_bytes(content[4:8], "big")
        read_bytes: int = int.from_bytes(content[8:12], "big")
        file_name: str = content[16:].decode("utf-8")

        return ReadFileRequest(request_id, offset, read_bytes, file_name)

    def __eq__(self, other):
        return (
            isinstance(other, ReadFileRequest)
            and self.request_id == other.request_id
            and self.offset == other.offset
            and self.read_bytes == other.read_bytes
            and self.file_name == other.file_name
        )


class WriteFileRequest(Message):
    message_type_identifier: int = 2

    def __init__(self, request_id: int, offset: int, file_name: str, content: bytes):
        super().__init__(2)
        self.request_id: int = request_id
        self.offset: int = offset
        self.file_name: str = file_name
        self.content: bytes = content

    def marshall(self) -> bytes:
        byte_id: bytes = self.request_id.to_bytes(4, "big")
        byte_offset: bytes = self.offset.to_bytes(4, "big")
        byte_filename: bytearray = bytearray(self.file_name, encoding="utf-8")
        byte_filename_length: bytes = (len(byte_filename)).to_bytes(4, "big")
        byte_content: bytes = self.content
        byte_content_length: bytes = (len(byte_content)).to_bytes(4, "big")

        marshalled_content = (
            byte_id + byte_offset + byte_filename_length + byte_content_length + byte_filename + byte_content
        )
        return super().marshall() + marshalled_content

    @staticmethod
    def unmarshall(content: bytes) -> "WriteFileRequest":
        request_id = int.from_bytes(content[0:4], "big")
        offset = int.from_bytes(content[4:8], "big")
        filename_length = int.from_bytes(content[8:12], "big")
        content_length = int.from_bytes(content[12:16], "big")
        filename = content[16: 16 + filename_length].decode("utf-8")
        file_content = content[16 + filename_length: 16 + filename_length + content_length]

        return WriteFileRequest(request_id, offset, filename, file_content)

    def __eq__(self, other):
        return (
            isinstance(other, WriteFileRequest)
            and self.request_id == other.request_id
            and self.offset == other.offset
            and self.file_name == other.file_name
            and self.content == other.content
        )


class SubscribeToUpdatesRequest(Message):
    def __init__(self, client_ip_address, client_port_number, monitoring_interval, file_name_length, file_name):
        super().__init__(3)
        self.client_ip_address: str = client_ip_address
        self.client_port_number: int = client_port_number
        self.monitoring_interval: int = monitoring_interval
        self.file_name_length: int = file_name_length
        self.file_name: str = file_name

    def marshall(self) -> bytes:
        client_ip_address: bytes = socket.inet_aton(self.client_ip_address)
        client_port_number: bytes = self.client_port_number.to_bytes(4, "big")
        monitoring_interval: bytes = self.monitoring_interval.to_bytes(4, "big")
        file_name_length: bytes = self.file_name_length.to_bytes(4, "big")
        file_name: bytearray = bytearray(self.file_name, encoding="utf-8")

        return (
            super().marshall()
            + client_ip_address
            + client_port_number
            + monitoring_interval
            + file_name_length
            + file_name
        )

    @staticmethod
    def unmarshall(content: bytes) -> "SubscribeToUpdatesRequest":
        client_ip_address: str = socket.inet_ntoa(content[0:4])
        client_port_number: int = int.from_bytes(content[4:8], "big")
        monitoring_interval: int = int.from_bytes(content[8:12], "big")
        filename_length: int = int.from_bytes(content[12:16], "big")
        file_name: str = content[16: 16 + filename_length].decode("utf-8")

        return SubscribeToUpdatesRequest(
            client_ip_address, client_port_number, monitoring_interval, filename_length, file_name
        )

    def __eq__(self, other):
        return (
            isinstance(other, SubscribeToUpdatesRequest)
            and self.client_ip_address == other.client_ip_address
            and self.client_port_number == other.client_port_number
            and self.monitoring_interval == other.monitoring_interval
            and self.file_name_length == other.file_name_length
            and self.file_name == other.file_name
        )


# Server
class ReadFileResponse(Message):
    def __init__(self, reply_id, content):
        super().__init__(4)
        self.reply_id: int = reply_id
        self.content: str = content

    def marshall(self) -> bytes:
        byte_id: bytes = self.reply_id.to_bytes(4, "big")
        byte_content: bytearray = bytearray(self.content, encoding="utf-8")
        marshalled_content: bytes = byte_id + byte_content

        return super().marshall() + marshalled_content

    @staticmethod
    def unmarshall(content: bytes) -> "ReadFileResponse":
        reply_id = int.from_bytes(content[0:4], "big")
        content = content[4:].decode("utf-8")
        return ReadFileResponse(reply_id, content)


class WriteFileResponse(Message):
    def __init__(self, reply_id, is_successful):
        super().__init__(5)
        self.reply_id: int = reply_id
        self.is_successful: bool = is_successful

    def marshall(self) -> bytes:
        byte_id: bytes = self.reply_id.to_bytes(4, "big")
        byte_success: bytes = int(self.is_successful).to_bytes(1, "big")
        marshalled_content = byte_id + byte_success
        return super().marshall() + marshalled_content

    @staticmethod
    def unmarshall(content: bytes) -> "WriteFileResponse":
        reply_id = int.from_bytes(content[0:4], "big")
        is_successful = content[4:].decode("utf-8")
        return WriteFileResponse(reply_id, is_successful)


# TODO: complete marshalling and unmarshalling and create test
class SubscribeToUpdatesResponse:
    def __init__(self):
        self.reply_id: int
        self.is_successful: bool

    def marshall(self) -> bytearray:
        pass

    def unmarshall(self, content: bytearray) -> "SubscribeToUpdatesResponse":
        pass


# TODO: complete marshalling and unmarshalling and create test
class UpdateNotification:
    def __init__(self):
        self.file_name: str
        self.content: bytearray

    def marshall(self) -> bytearray:
        pass

    def unmarshall(self, content: bytearray) -> "UpdateNotification":
        pass
