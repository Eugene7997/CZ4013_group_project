from pathlib import Path

from remote_file_system.server_file_system import ServerFileSystem


class TestServerFileSystem:
    # TODO write additional unit tests for other methods of server interface

    @staticmethod
    def test_read_file_file_exists():
        server_root_directory: Path = Path.cwd() / "tests" / "server"
        server_file_system = ServerFileSystem(server_root_directory=server_root_directory)
        actual = server_file_system.read_file("english_alphabets.txt")
        expected = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".encode("UTF-8")
        assert actual == expected

    @staticmethod
    def test_delete_file():
        server_root_directory: Path = Path.cwd() / "tests" / "server"
        server = ServerFileSystem(server_root_directory=server_root_directory)
        f = open(f"{server_root_directory}/deleteme.txt", "w")
        f.close()
        assert server.delete_file("deleteme.txt")
