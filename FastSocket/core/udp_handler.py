"""
UDP client handler module for FastSocket.

This module contains handler classes for managing UDP datagram sources.
"""

import socket
from threading import Thread
from queue import Queue
from typing import Tuple, Dict
from time import time

from FastSocket.utils.logger import Logger


class UDPClientHandler:
    """
    Handler for tracking UDP datagram sources.

    Unlike TCP, UDP is connectionless, so this class tracks active
    sources based on their address and recent activity.

    Attributes:
        address: Source address (host, port)
        message_queue: Queue for storing received datagrams
        last_seen: Timestamp of last received datagram
        active: Whether this source is considered active
    """

    def __init__(self, address: Tuple[str, int]):
        """
        Initialize UDP client handler.

        Args:
            address: Source address (host, port)
        """
        self.address: Tuple[str, int] = address
        self.message_queue: Queue = Queue()
        self.last_seen: float = time()
        self.active: bool = True

    def update_activity(self):
        """Update the last seen timestamp."""
        self.last_seen = time()
        self.active = True

    def is_timeout(self, timeout: float = 30.0) -> bool:
        """
        Check if this source has timed out.

        Args:
            timeout: Timeout in seconds (default: 30)

        Returns:
            bool: True if timed out
        """
        return (time() - self.last_seen) > timeout

    def add_message(self, message: str):
        """
        Add a message to the queue.

        Args:
            message: Message to add
        """
        self.message_queue.put((message, self.address))
        self.update_activity()
