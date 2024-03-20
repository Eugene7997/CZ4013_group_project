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
