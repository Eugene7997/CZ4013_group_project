import socket
from abc import ABC, abstractmethod


class Message(ABC):
    class_id_to_class_ref = {}
    class_ref_to_class_id = {}

    @classmethod
    def register_subclass(cls, class_id):
        def decorator(subclass):
            cls.class_id_to_class_ref[class_id] = subclass
            cls.class_ref_to_class_id[subclass] = class_id
            return subclass

        return decorator

    def marshall(self) -> bytes:
        if self.__class__ not in self.class_ref_to_class_id:
            raise RuntimeError(f"{self.__class__} has not been registered as a subclass")
        class_id: bytes = self.class_ref_to_class_id[self.__class__].to_bytes(4, "big")
        return class_id + self._marshall_without_type_info()

    @classmethod
    def unmarshall(cls, content: bytes) -> "Message":
        class_id: int = int.from_bytes(content[0:4], "big")
        if class_id not in cls.class_id_to_class_ref:
            raise RuntimeError(f"Unsupported class identifier: {class_id}")
        return cls.class_id_to_class_ref[class_id]._unmarshall_without_type_info(content[4:])

    @abstractmethod
    def _marshall_without_type_info(self) -> bytes:
        pass

    @staticmethod
    @abstractmethod
    def _unmarshall_without_type_info(content: bytes) -> "Message":
        pass


# Client
@Message.register_subclass(class_id=1)
class ReadFileRequest(Message):
    def __init__(self, request_id: int, offset: int, read_bytes: int, filename: str):
        self.request_id: int = request_id
        self.offset: int = offset
        self.read_bytes: int = read_bytes
        self.file_name: str = filename

    def _marshall_without_type_info(self) -> bytes:
        file_name: bytearray = bytearray(self.file_name, encoding="utf-8")
        file_name_length: bytes = len(file_name).to_bytes(4, "big")
        request_id: bytes = self.request_id.to_bytes(4, "big")
        offset: bytes = self.offset.to_bytes(4, "big")
        read_bytes: bytes = self.read_bytes.to_bytes(4, "big")

        return request_id + offset + read_bytes + file_name_length + file_name

    @staticmethod
    def _unmarshall_without_type_info(content: bytes) -> "ReadFileRequest":
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


@Message.register_subclass(class_id=2)
class WriteFileRequest(Message):
    def __init__(self, request_id: int, offset: int, file_name: str, content: bytes):
        self.request_id: int = request_id
        self.offset: int = offset
        self.file_name: str = file_name
        self.content: bytes = content

    def _marshall_without_type_info(self) -> bytes:
        byte_id: bytes = self.request_id.to_bytes(4, "big")
        byte_offset: bytes = self.offset.to_bytes(4, "big")
        byte_filename: bytearray = bytearray(self.file_name, encoding="utf-8")
        byte_filename_length: bytes = (len(byte_filename)).to_bytes(4, "big")
        byte_content: bytes = self.content
        byte_content_length: bytes = (len(byte_content)).to_bytes(4, "big")

        marshalled_content = (
            byte_id + byte_offset + byte_filename_length + byte_content_length + byte_filename + byte_content
        )
        return marshalled_content

    @staticmethod
    def _unmarshall_without_type_info(content: bytes) -> "WriteFileRequest":
        request_id = int.from_bytes(content[0:4], "big")
        offset = int.from_bytes(content[4:8], "big")
        filename_length = int.from_bytes(content[8:12], "big")
        content_length = int.from_bytes(content[12:16], "big")
        filename = content[16 : 16 + filename_length].decode("utf-8")
        file_content = content[16 + filename_length : 16 + filename_length + content_length]

        return WriteFileRequest(request_id, offset, filename, file_content)

    def __eq__(self, other):
        return (
            isinstance(other, WriteFileRequest)
            and self.request_id == other.request_id
            and self.offset == other.offset
            and self.file_name == other.file_name
            and self.content == other.content
        )


@Message.register_subclass(class_id=3)
class SubscribeToUpdatesRequest(Message):
    def __init__(self, client_ip_address, client_port_number, monitoring_interval, file_name_length, file_name):
        self.client_ip_address: str = client_ip_address
        self.client_port_number: int = client_port_number
        self.monitoring_interval: int = monitoring_interval
        self.file_name_length: int = file_name_length
        self.file_name: str = file_name

    def _marshall_without_type_info(self) -> bytes:
        client_ip_address: bytes = socket.inet_aton(self.client_ip_address)
        client_port_number: bytes = self.client_port_number.to_bytes(4, "big")
        monitoring_interval: bytes = self.monitoring_interval.to_bytes(4, "big")
        file_name_length: bytes = self.file_name_length.to_bytes(4, "big")
        file_name: bytearray = bytearray(self.file_name, encoding="utf-8")

        return client_ip_address + client_port_number + monitoring_interval + file_name_length + file_name

    @staticmethod
    def _unmarshall_without_type_info(content: bytes) -> "SubscribeToUpdatesRequest":
        client_ip_address: str = socket.inet_ntoa(content[0:4])
        client_port_number: int = int.from_bytes(content[4:8], "big")
        monitoring_interval: int = int.from_bytes(content[8:12], "big")
        filename_length: int = int.from_bytes(content[12:16], "big")
        file_name: str = content[16 : 16 + filename_length].decode("utf-8")

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
@Message.register_subclass(class_id=4)
class ReadFileResponse(Message):
    def __init__(self, reply_id, content):
        self.reply_id: int = reply_id
        self.content: str = content

    def _marshall_without_type_info(self) -> bytes:
        byte_id: bytes = self.reply_id.to_bytes(4, "big")
        byte_content: bytearray = bytearray(self.content, encoding="utf-8")
        marshalled_content: bytes = byte_id + byte_content
        return marshalled_content

    @staticmethod
    def _unmarshall_without_type_info(content: bytes) -> "ReadFileResponse":
        reply_id = int.from_bytes(content[0:4], "big")
        content = content[4:].decode("utf-8")
        return ReadFileResponse(reply_id, content)


@Message.register_subclass(class_id=5)
class WriteFileResponse(Message):
    def __init__(self, reply_id, is_successful):
        self.reply_id: int = reply_id
        self.is_successful: bool = is_successful

    def _marshall_without_type_info(self) -> bytes:
        byte_id: bytes = self.reply_id.to_bytes(4, "big")
        byte_success: bytes = int(self.is_successful).to_bytes(1, "big")
        marshalled_content = byte_id + byte_success
        return marshalled_content

    @staticmethod
    def _unmarshall_without_type_info(content: bytes) -> "WriteFileResponse":
        reply_id = int.from_bytes(content[0:4], "big")
        is_successful = content[4:].decode("utf-8")
        return WriteFileResponse(reply_id, is_successful)


# TODO: complete marshalling and unmarshalling and create test
class SubscribeToUpdatesResponse(Message):
    def __init__(self):
        self.reply_id: int
        self.is_successful: bool

    def _marshall_without_type_info(self) -> bytes:
        pass

    @staticmethod
    def _unmarshall_without_type_info(content: bytes) -> "SubscribeToUpdatesResponse":
        pass


# TODO: complete marshalling and unmarshalling and create test
class UpdateNotification(Message):
    def __init__(self):
        self.file_name: str
        self.content: bytes

    def _marshall_without_type_info(self) -> bytes:
        pass

    @staticmethod
    def _unmarshall_without_type_info(content: bytes) -> "UpdateNotification":
        pass
