import os

from remote_file_system.server_interface import Server


class TestServerInterface:
    # TODO write additional unit tests for other methods of server interface

    @staticmethod
    def test_read_file_file_exists():
        server = Server(file_storage_location=os.getcwd())
        actual = server.read_file("tests/mock_data/mock_data_a.txt")
        expected = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".encode("UTF-8")
        assert actual == expected
