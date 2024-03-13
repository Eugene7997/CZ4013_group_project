import os
import time


class Cache:
    def __init__(self, cache_location: str, freshness_interval_in_seconds: int):
        self.cache_location: str = cache_location
        self.freshness_interval_in_seconds: int = freshness_interval_in_seconds
        self.last_validated: dict = {}

    def is_in_cache(self, file_name: str) -> bool:
        file_path: str = self.cache_location + file_name
        if os.path.exists(file_path):
            return True
        else:
            return False

    def put_in_cache(self, file_name: str, content: str) -> None:
        file_path: str = self.cache_location + file_name
        with open(file_path, "x") as file:
            file.write(content)

    def get_from_cache(self, file_name: str) -> bytes:
        file_path: str = self.cache_location + file_name
        with open(file_path, "rb") as file:
            return file.read()

    def get_file_modification_timestamp(self, file_name: str) -> int:
        file_path: str = self.cache_location + file_name
        timestamp_of_modifications_to_file_in_seconds: int = int(os.path.getmtime(file_path))
        return timestamp_of_modifications_to_file_in_seconds

    def request_file_modification_timestamp(self, file_name: str):
        if self.is_in_cache(file_name):
            return self.get_file_modification_timestamp(file_name)
        else:
            return None

    def validity_check_without_server(self, file_name: str):
        file_path: str = self.cache_location + file_name

        T = self.request_file_modification_timestamp(file_name)

        if abs(T - self.last_validated[file_path]) < self.freshness_interval_in_seconds:
            return True
        else:
            return False

    def request_server(self):
        pass

    def validity_check_with_server(self, file_name: str):
        pass

    def validity_check(self, file_name):
        if self.validity_check_without_server(file_name) is True:
            if self.validity_check_with_server(file_name) is True:
                return True
        return False

    def update_file_validation_timestamp(self, file_name: str):
        file_path: str = self.cache_location + file_name
        self.last_validated[file_path] = time.time()

    def validate_file(self, file_name: str):
        pass
