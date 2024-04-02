import socket
import time
from ipaddress import IPv4Address
from typing import Optional, Tuple

from loguru import logger

from remote_file_system.message import Message
import remote_file_system.config


def send_message_and_wait_for_reply(
    message: Message,
    recipient_ip_address: IPv4Address,
    recipient_port_number: int,
    max_attempts_to_send_message: int,
    timeout_in_seconds: int,
) -> Optional[Message]:
    """
    For client to send message to server
    """
    if remote_file_system.config.CLIENT_DROP_MESSAGE:
        logger.info("Simulating loss of request message from client.")
        max_attempts_to_send_message -= 1
        time.sleep(timeout_in_seconds)
        remote_file_system.config.CLIENT_DROP_MESSAGE = False

    sock: socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # TODO: do more testing for sock.bind with different computers.
    sock.bind(("", 0))
    sock.settimeout(timeout_in_seconds)

    sender_ip_address, sender_port_number = sock.getsockname()
    logger.debug(f"Socket opened at {sender_ip_address}:{sender_port_number}.")

    outgoing_bytes: bytes = message.marshall()
    incoming_bytes: Optional[bytes] = None

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


def send_message(
    message: Message,
    recipient_ip_address: IPv4Address,
    recipient_port_number: int,
) -> None:
    """
    For server to send message to client
    """
    if remote_file_system.config.SERVER_DROP_MESSAGE:
        logger.info("Simulating loss of reply message from server.")
        remote_file_system.config.SERVER_DROP_MESSAGE = False
        return

    sock: socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # TODO: do more testing for sock.bind with different computers.
    sock.bind(("", 0))

    sender_ip_address, sender_port_number = sock.getsockname()
    logger.debug(f"Socket opened at {sender_ip_address}:{sender_port_number}.")

    outgoing_bytes: bytes = message.marshall()
    recipient_address: Tuple[str, int] = str(recipient_ip_address), recipient_port_number

    # TODO: test binding to the same port number instead of maintaining socket throughout attempts
    try:
        sock.sendto(outgoing_bytes, recipient_address)
        logger.debug(f"{message} sent to {recipient_ip_address}:{recipient_port_number}.")
    except Exception as e:
        logger.warning(f"Error: {e} occurred.")

    sock.close()
