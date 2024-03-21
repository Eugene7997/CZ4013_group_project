import os
from pathlib import Path

from remote_file_system.server_interface import Server


class TestServerInterface:
    # TODO write additional unit tests for other methods of server interface

    @staticmethod
    def test_read_file_file_exists():
        server = Server(server_root_directory=Path.cwd() / "tests" / "server")
        actual = server.read_file("english_alphabets.txt")
        expected = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".encode("UTF-8")
        assert actual == expected

    @staticmethod
    def test_delete_file():
        server_file_directory = os.getcwd()
        f = open(f"{server_file_directory}/deleteme.txt", "w")
        f.close()

        server = Server(server_root_directory=server_file_directory)
        assert server.delete_file("deleteme.txt")
