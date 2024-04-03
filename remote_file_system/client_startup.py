#!/usr/bin/env python3
import argparse
from ipaddress import IPv4Address
from pathlib import Path

from remote_file_system.client_command_line_interface import ClientCommandLineInterface
from remote_file_system.client_interface import Client


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="server_menu", description="Create server with given arguments"
    )
    parser.add_argument("-cp", "--client-port-number", type=int, required=True, help="specifies client's port number")
    parser.add_argument("-sip", "--server-ip-address", type=str, required=True, help="specifies server's IP address")
    parser.add_argument("-sp", "--server-port-number", type=int, required=True, help="specifies server's port number")
    parser.add_argument(
        "-c", "--cache-working-directory", type=str, required=True, help="specifies client's cache " "working directory"
    )
    parser.add_argument(
        "-m",
        "--freshness-interval-in-seconds",
        type=int,
        default=60,
        help="specifies client's " "freshness interval in " "seconds",
    )
    args: argparse.Namespace = parser.parse_args()

    client = Client(
        client_port_number=args.client_port_number,
        server_ip_address=IPv4Address(args.server_ip_address),
        server_port_number=args.server_port_number,
        cache_working_directory=Path(args.cache_working_directory),
        freshness_interval_in_seconds=args.freshness_interval_in_seconds,
    )
    client_command_line_interface: ClientCommandLineInterface = ClientCommandLineInterface(client=client)
    client_command_line_interface.start()


if __name__ == "__main__":
    main()
