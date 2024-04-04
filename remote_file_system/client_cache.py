import time
import os
from pathlib import Path
from typing import Dict


class Cache:
    def __init__(self, cache_working_directory: Path):
        self.cache_working_directory: Path = cache_working_directory
        self.validation_timestamps: Dict[Path, int] = {}
        self.modification_timestamps: Dict[Path, int] = {}

    def is_in_cache(self, file_path: Path) -> bool:
        return file_path in self.validation_timestamps

    def put_in_cache(
        self, file_path: Path, file_content: bytes, validation_timestamp: int, modification_timestamp: int
    ) -> None:
        full_file_path = self.cache_working_directory.joinpath(file_path)
        full_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_file_path, "wb") as file:
            file.write(file_content)

        self.validation_timestamps[file_path] = validation_timestamp
        self.modification_timestamps[file_path] = modification_timestamp

    def remove_from_cache(self, file_path: Path) -> None:
        full_file_path = self.cache_working_directory.joinpath(file_path)
        full_file_path.parent.mkdir(parents=True, exist_ok=True)
        os.remove(full_file_path)

        del self.validation_timestamps[file_path]
        del self.modification_timestamps[file_path]

    def update_cache_after_write(self, file_path: Path, offset: int, file_content: bytes) -> None:
        full_file_path = self.cache_working_directory.joinpath(file_path)
        full_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_file_path, "r+b") as file:
            file.seek(offset)
            file.write(file_content)

    def update_cache_after_append(self, file_path: Path, file_content: bytes) -> None:
        full_file_path = self.cache_working_directory.joinpath(file_path)
        full_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_file_path, "ab") as file:
            file.write(file_content)

    def get_file_content(self, file_path: Path) -> bytes:
        full_file_path = self.cache_working_directory.joinpath(file_path)
        with open(full_file_path, "rb") as file:
            return file.read()

    def get_validation_timestamp(self, file_path: Path) -> int:
        return self.validation_timestamps[file_path]

    def validate_cache_for(self, file_path: Path) -> None:
        self.validation_timestamps[file_path] = int(time.time())

    def get_modification_timestamp(self, file_path: Path) -> int:
        return self.modification_timestamps[file_path]
