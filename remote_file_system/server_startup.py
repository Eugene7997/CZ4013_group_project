#!/usr/bin/env python3
import argparse
from ipaddress import IPv4Address
from pathlib import Path

from remote_file_system.server import Server
from remote_file_system.server_file_system import ServerFileSystem
from remote_file_system.server import InvocationSemantics


parser = argparse.ArgumentParser(prog="server_menu", description="Create server with given arguments")
parser.add_argument(
    "-i", "--invocation_method", type=int, help="Invocation number, 0 for at least once, 1 for at most once", default=0
)
parser.add_argument("-ip", "--ip_address", type=str, help="specifies ip number for server")
parser.add_argument("-port", "--port_number", type=int, help="sets port number for server")
parser.add_argument(
    "-dir",
    "--directory",
    type=str,
    help="specify the root directory of the server file system. This "
    "will be the name of the directory in the project root "
    "folder",
    default="server_dir",
)

args = parser.parse_args()

invocation_method = args.invocation_method
SERVER_IP_ADDRESS = IPv4Address(args.ip_address)
SERVER_PORT_NUMBER = args.port_number
server_root_directory = Path.cwd() / args.directory


server_file_system = ServerFileSystem(server_root_directory=server_root_directory)

if invocation_method == 0:
    server = Server(
        server_ip_address=SERVER_IP_ADDRESS,
        server_port_number=SERVER_PORT_NUMBER,
        file_system=server_file_system,
        invocation_semantics=InvocationSemantics.AT_LEAST_ONCE,
    )
    server.listen_for_messages()
else:
    server = Server(
        server_ip_address=SERVER_IP_ADDRESS,
        server_port_number=SERVER_PORT_NUMBER,
        file_system=server_file_system,
        invocation_semantics=InvocationSemantics.AT_MOST_ONCE,
    )
    server.listen_for_messages()
