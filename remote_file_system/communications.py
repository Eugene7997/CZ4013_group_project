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

    sock: socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", 0))
    sock.settimeout(timeout_in_seconds)

    sender_ip_address, sender_port_number = sock.getsockname()
    logger.debug(f"Socket opened at {sender_ip_address}:{sender_port_number}.")

    outgoing_bytes: bytes = message.marshall()
    incoming_bytes: bytes = None

    recipient_address: Tuple[str, int] = str(recipient_ip_address), recipient_port_number

    # TODO: test binding to the same port number instead of maintaining socket throughout attempts
    for attempt_number in range(max_attempts_to_send_message):
        try:
            sock.sendto(outgoing_bytes, recipient_address)
            logger.debug(f"{message} sent to {recipient_ip_address}:{recipient_port_number}.")

            incoming_bytes: bytes = sock.recv(4096)  # TODO review fixed buffer size
            break
        except socket.timeout:
            logger.warning(f"Attempt {attempt_number + 1} timed out while waiting for a response.")

    sock.close()

    if not incoming_bytes:
        logger.warning(f"No responses received after {max_attempts_to_send_message} attempts.")
        return None

    incoming_message: Message = Message.unmarshall(incoming_bytes)
    logger.debug(f"{message} reply received from {recipient_ip_address}:{recipient_port_number}.")
    return incoming_message
