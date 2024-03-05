import socket
from ipaddress import IPv4Address
from typing import Optional, Tuple
from loguru import logger

from remote_file_system.message import Message


def send_message(
    message: Message,
    recipient_ip_address: IPv4Address,
    recipient_port_number: int,
    max_attempts_to_send_message: int,
    timeout_in_seconds: int,
) -> Optional[Message]:

    outgoing_bytes: bytes = message.marshall()
    incoming_bytes: bytes = None

    recipient_address: Tuple[str, int] = str(recipient_ip_address), recipient_port_number

    for attempt_number in range(max_attempts_to_send_message):
        sock: socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout_in_seconds)

        try:
            number_of_bytes_sent: int = sock.sendto(outgoing_bytes, recipient_address)
            logger.debug(f"{number_of_bytes_sent} bytes sent to {recipient_ip_address}:{recipient_port_number}.")

            incoming_bytes: bytes = sock.recv(4096)  # TODO review fixed buffer size
            break
        except socket.timeout:
            logger.warning(f"Attempt {attempt_number} timed out while waiting for a response.")
        finally:
            sock.close()

    if not incoming_bytes:
        logger.warning(f"No responses received after {max_attempts_to_send_message} attempts.")
        return None

    reply_message: Message = Message.unmarshall(incoming_bytes)
    return reply_message


def listen_for_message(server_ip_address: IPv4Address, server_port_number: int) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address: Tuple[str, int] = (str(server_ip_address), server_port_number)
    sock.bind(server_address)

    try:
        while True:
            logger.info(f"Socket is listening for messages at {server_ip_address}:{server_port_number}.")

            incoming_bytes, sender_address = sock.recvfrom(4096)  # TODO review fixed buffer size
            sender_ip_address, sender_port_number = sender_address
            logger.info(f"Received {len(incoming_bytes)} bytes from {sender_ip_address}:{sender_port_number}.")

            if incoming_bytes:
                incoming_message: Message = Message.unmarshall(incoming_bytes)
                logger.debug(f"Received {incoming_message}.")
                # TODO use the server dispatcher module to process the inbound message

                number_of_bytes_sent: int = sock.sendto(incoming_bytes, sender_address)  # TODO change server reply
                logger.debug(f"{number_of_bytes_sent} bytes sent to {sender_ip_address}:{sender_port_number}.")
    finally:
        sock.close()
