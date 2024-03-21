import os

from remote_file_system.server_interface import Server


class TestServerInterface:
    # TODO write additional unit tests for other methods of server interface

    @staticmethod
    def test_read_file_file_exists():
        server = Server(file_storage_location=os.getcwd())
        actual = server.read_file("tests/mock_data/english_alphabets.txt")
        expected = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".encode("UTF-8")
        assert actual == expected
    
    def test_delete_file():
        server_file_directory = os.getcwd()
        f = open(f"{server_file_directory}/deleteme.txt", "w")
        server = Server(file_storage_location=server_file_directory)
        actual = server.delete_file("deleteme.txt")
        expected = True
        assert actual == expected
