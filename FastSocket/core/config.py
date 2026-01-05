"""
Configuration module for FastSocket.

This module contains configuration classes for socket connections.
"""

import socket
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from FastSocket.utils.types import Types


class SocketConfig:
    """
    Configuration class for socket connections.

    Attributes:
        host (str): The hostname or IP address to bind/connect to
        port (int): The port number
        family: Address family (AF_INET for IPv4, AF_INET6 for IPv6)
        type: Socket type (SOCK_STREAM for TCP, SOCK_DGRAM for UDP)
        reuse_address (bool): Whether to set SO_REUSEADDR option

    Example:
        >>> config = SocketConfig(host='localhost', port=8080)
        >>> server = FastSocketServer(config)
    """

    def __init__(self,
                 host: str = 'localhost',
                 port: int = 7654,
                 family: socket.AddressFamily = socket.AF_INET,
                 type: socket.SocketKind = socket.SOCK_STREAM,
                 reuse_address: bool = True) -> None:
        """
        Initialize socket configuration.

        Args:
            host: Hostname or IP address (default: 'localhost')
            port: Port number (default: 7654)
            family: Address family (default: AF_INET for IPv4)
            type: Socket type (default: SOCK_STREAM for TCP)
            reuse_address: Enable SO_REUSEADDR (default: True)
        """
        self.host = host
        self.port = port
        self.family = family
        self.type = type
        self.reuse_address: bool = reuse_address

    def _create_socket(self) -> socket.socket:
        """
        Create a socket with the configured parameters.

        Returns:
            socket.socket: Configured socket instance
        """
        sock: socket.socket = socket.socket(self.family, self.type)

        if self.reuse_address:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        return sock


# Backward compatibility alias (deprecated)
SockerConfig = SocketConfig
