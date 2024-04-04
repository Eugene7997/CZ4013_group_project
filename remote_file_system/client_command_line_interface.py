from pathlib import Path
from typing import List, Optional

from colorama import init, Fore

from remote_file_system.client_interface import Client


class ClientCommandLineInterface:
    WELCOME_MESSAGE = Fore.BLUE + "Welcome to the Remote File System Client CLI!"
    COMMAND_LINE_INTERFACE_OPTIONS = """Available commands:
    read [file_path] [offset] [number_of_bytes]
    write [file_path] [offset] [content]
    append [file_path] [content]
    delete [file_path]
    subscribe [file_path] [monitoring_interval_in_seconds]
    help
    exit"""

    def __init__(self, client: Client):
        self.client: Client = client
        init(autoreset=True)

    def start(self):
        print(self.WELCOME_MESSAGE)
        print(self.COMMAND_LINE_INTERFACE_OPTIONS)
        while True:
            command = input("Command for remote file system client: ")
            if "exit" in command:
                break
            self._parse_command(command)

    def _parse_command(self, command: str) -> None:
        command_tokens = command.split(" ")
        command_type = command_tokens[0]
        command_args = command_tokens[1:]
        if command_type == "help":
            print(self.COMMAND_LINE_INTERFACE_OPTIONS)
        elif command_type == "read":
            self._parse_read_command(command_args)
        elif command_type == "write":
            self._parse_write_command(command_args)
        elif command_type == "append":
            self._parse_append_command(command_args)
        elif command_type == "delete":
            self._parse_delete_command(command_args)
        elif command_type == "subscribe":
            self._parse_subscribe_command(command_args)
        else:
            print(Fore.RED + f"Unrecognised command: {command}")

    def _parse_read_command(self, command_args: List[str]) -> None:
        EXPECTED_NUMBER_OF_ARGUMENTS_FOR_READ_COMMAND = 3

        if len(command_args) != EXPECTED_NUMBER_OF_ARGUMENTS_FOR_READ_COMMAND:
            print(
                Fore.RED + f"Read command requires "
                f"exactly {EXPECTED_NUMBER_OF_ARGUMENTS_FOR_READ_COMMAND} arguments."
            )
            return

        try:
            input_file_path: str = command_args[0]
            file_path: Path = Path(input_file_path)

            input_offset: str = command_args[1]
            offset: int = self._parse_offset(input_offset)

            input_number_of_bytes: str = command_args[2]
            number_of_bytes: int = self._parse_number_of_bytes(input_number_of_bytes)
        except ValueError as e:
            print(Fore.RED + f"Invalid arguments were received for read command: {e}")
            return

        raw_file_content: Optional[bytes] = self.client.read_file(
            file_path=file_path,
            offset=offset,
            number_of_bytes=number_of_bytes,
        )
        if not raw_file_content:
            print("File does not exist")
            return
        try:
            file_content_decoded: str = raw_file_content.decode("utf-8")
            print(file_content_decoded)
        except UnicodeDecodeError as e:
            print("Read command was successful but the file content could not be decoded with UTF-8.")

    def _parse_write_command(self, command_args: List[str]) -> None:
        EXPECTED_NUMBER_OF_ARGUMENTS_FOR_WRITE_COMMAND = 3

        if len(command_args) != EXPECTED_NUMBER_OF_ARGUMENTS_FOR_WRITE_COMMAND:
            print(
                Fore.RED + f"Write command requires "
                f"exactly {EXPECTED_NUMBER_OF_ARGUMENTS_FOR_WRITE_COMMAND} arguments."
            )
            return

        try:
            input_file_path: str = command_args[0]
            file_path: Path = Path(input_file_path)

            input_offset: str = command_args[1]
            offset: int = self._parse_offset(input_offset)

            input_content: str = command_args[2]
            content: bytes = input_content.encode("utf-8")
        except ValueError:
            print(Fore.RED + "Invalid arguments were received for write command. The command was not executed.")
            return

        if self.client.write_file(file_path=file_path, offset=offset, content=content):
            print("Write command was successful.")
        else:
            print("Write command was unsuccessful.")

    def _parse_append_command(self, command_args: List[str]) -> None:
        EXPECTED_NUMBER_OF_ARGUMENTS_FOR_APPEND_COMMAND = 2

        if len(command_args) != EXPECTED_NUMBER_OF_ARGUMENTS_FOR_APPEND_COMMAND:
            print(
                Fore.RED + f"Append command requires "
                f"exactly {EXPECTED_NUMBER_OF_ARGUMENTS_FOR_APPEND_COMMAND} arguments."
            )
            return

        try:
            input_file_path: str = command_args[0]
            file_path: Path = Path(input_file_path)

            input_content: str = command_args[1]
            content: bytes = input_content.encode("utf-8")
        except ValueError as e:
            print(Fore.RED + f"Invalid arguments were received for append command: {e}")
            return

        if self.client.append_file(file_path=file_path, content=content):
            print("Append command was successful.")
        else:
            print("Append command was unsuccessful")

    def _parse_delete_command(self, command_args: List[str]) -> None:
        EXPECTED_NUMBER_OF_ARGUMENTS_FOR_DELETE_COMMAND = 1

        if len(command_args) != EXPECTED_NUMBER_OF_ARGUMENTS_FOR_DELETE_COMMAND:
            print(
                Fore.RED + f"Delete command requires "
                f"exactly {EXPECTED_NUMBER_OF_ARGUMENTS_FOR_DELETE_COMMAND} arguments."
            )
            return

        try:
            input_file_path: str = command_args[0]
            file_path: Path = Path(input_file_path)
        except ValueError as e:
            print(Fore.RED + f"Invalid arguments were received for delete command: {e}")
            return

        if self.client.delete_file_in_server(file_path=file_path):
            print("Delete command was successful.")
        else:
            print("Delete command was unsuccessful.")

    def _parse_subscribe_command(self, command_args: List[str]) -> None:
        EXPECTED_NUMBER_OF_ARGUMENTS_FOR_SUBSCRIBE_COMMAND = 2

        if len(command_args) != EXPECTED_NUMBER_OF_ARGUMENTS_FOR_SUBSCRIBE_COMMAND:
            print(
                Fore.RED + f"Subscribe command requires "
                f"exactly {EXPECTED_NUMBER_OF_ARGUMENTS_FOR_SUBSCRIBE_COMMAND} arguments."
            )
            return

        try:
            input_file_path: str = command_args[0]
            file_path: Path = Path(input_file_path)

            input_monitoring_interval_in_seconds: str = command_args[1]
            monitoring_interval_in_seconds: int = self._parse_monitoring_interval_in_seconds(
                input_monitoring_interval_in_seconds
            )
        except ValueError as e:
            print(Fore.RED + f"Invalid arguments were received for subscribe command: {e}")
            return

        self.client.subscribe_to_updates(
            file_path=file_path, monitoring_interval_in_seconds=monitoring_interval_in_seconds
        )

    @staticmethod
    def _parse_offset(offset: str) -> int:
        try:
            return int(offset)
        except ValueError as e:
            raise ValueError(
                Fore.RED + f"{offset} is not valid input for offset. " f"Please enter an integer instead."
            ) from e

    @staticmethod
    def _parse_number_of_bytes(number_of_bytes: str) -> int:
        try:
            return int(number_of_bytes)
        except ValueError as e:
            raise ValueError(
                Fore.RED + f"{number_of_bytes} is not valid input for number_of_bytes. "
                f"Please enter an integer instead."
            ) from e

    @staticmethod
    def _parse_monitoring_interval_in_seconds(monitoring_interval_in_seconds: str) -> int:
        try:
            return int(monitoring_interval_in_seconds)
        except ValueError as e:
            raise ValueError(
                Fore.RED + f"{monitoring_interval_in_seconds} is not valid input for monitoring_interval_in_seconds. "
                f"Please enter an integer instead."
            ) from e
