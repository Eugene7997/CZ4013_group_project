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

args = parser.parse_args()

invocation_method = args.invocation_method
SERVER_IP_ADDRESS = IPv4Address(args.ip_address)
SERVER_PORT_NUMBER = args.port_number

# TODO Add server root directory default
server_root_directory: Path = Path.cwd() / "tests" / "server"

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
