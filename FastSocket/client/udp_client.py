"""
UDP Client module for FastSocket.

This module provides a UDP client implementation with support for
sending and receiving datagrams, including broadcast capability.
"""

import socket
import time
from threading import Thread
from typing import List, Callable, Tuple

from fastsocket.core.config import SocketConfig
from fastsocket.utils.logger import Logger


class FastSocketUDPClient(Thread):
    """
    Multi-threaded UDP client.

    This client can send datagrams to a server, receive responses,
    and handle incoming datagrams asynchronously with registered handlers.

    Attributes:
        _config: Socket configuration
        _new_message_handler: List of message handler functions
        _recv_size: Maximum datagram size
        _enable_broadcast: Enable broadcast support
        sock: Client socket

    Example:
        >>> def handle_msg(msg, addr):
        ...     print(f"From {addr}: {msg}")
        ...
        >>> config = SocketConfig(host='localhost', port=8080,
        ...                       type=socket.SOCK_DGRAM)
        >>> client = FastSocketUDPClient(config)
        >>> client.on_new_message(handle_msg)
        >>> client.start()
        >>> client.send_to_server("Hello server!")
    """

    def __init__(self,
                 config: SocketConfig,
                 recv_size: int = 65507,
                 enable_broadcast: bool = False) -> None:
        """
        Initialize UDP client.

        Args:
            config: Socket configuration (should use SOCK_DGRAM)
            recv_size: Maximum datagram size (default: 65507 bytes)
            enable_broadcast: Enable UDP broadcast support
        """
        super().__init__()
        self.daemon = True
        self._config = config
        self._new_message_handler: List[Callable] = []
        self._recv_size = recv_size
        self._enable_broadcast = enable_broadcast
        self._running = True

        self.sock: socket.socket = self._config._create_socket()

        # Enable broadcast if requested
        if self._enable_broadcast:
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            Logger.print_log_debug('UDP broadcast enabled')

    def run(self) -> None:
        """
        Start message handlers.

        Unlike TCP, UDP doesn't require a connection, so this just
        starts threads for each registered message handler.
        """
        for _message_handler in self._new_message_handler:
            message_thread = Thread(
                target=self._run_new_message_handler,
                args=(_message_handler,)
            )
            message_thread.daemon = True
            message_thread.start()

        if self._new_message_handler:
            while self._running:
                time.sleep(1)

    def send_to_server(self, msg: str | bytes,
                      server_address: Tuple[str, int] = None) -> int:
        """
        Send a datagram to the server.

        Args:
            msg: Message to send (string or bytes)
            server_address: Override server address (uses config if None)

        Returns:
            int: Number of bytes sent

        Raises:
            Exception: If sending fails

        Example:
            >>> client.send_to_server("Hello!")
            >>> client.send_to_server(b"Data", ('192.168.1.100', 9000))
        """
        if server_address is None:
            server_address = (self._config.host, self._config.port)

        try:
            if isinstance(msg, str):
                msg = msg.encode('utf-8')

            bytes_sent = self.sock.sendto(msg, server_address)
            return bytes_sent

        except Exception as e:
            Logger.print_log_error(e, 'FastSocketUDPClient')
            raise e

    def broadcast_message(self, msg: str | bytes,
                         port: int = None,
                         broadcast_addr: str = '255.255.255.255') -> int:
        """
        Broadcast a message.

        Requires enable_broadcast=True in constructor.

        Args:
            msg: Message to broadcast
            port: Destination port (uses config port if None)
            broadcast_addr: Broadcast address (default: 255.255.255.255)

        Returns:
            int: Number of bytes sent

        Example:
            >>> client = FastSocketUDPClient(config, enable_broadcast=True)
            >>> client.broadcast_message("Discovery request")
        """
        if not self._enable_broadcast:
            Logger.print_log_error(
                'Broadcast not enabled. Set enable_broadcast=True',
                'FastSocketUDPClient'
            )
            raise RuntimeError('Broadcast not enabled')

        if port is None:
            port = self._config.port

        return self.send_to_server(msg, (broadcast_addr, port))

    def on_new_message(self, func: Callable) -> None:
        """
        Register a message handler function.

        The handler will be called with (message, address) for each
        received datagram.

        Args:
            func: Callable that accepts (str, Tuple[str, int]) parameters

        Example:
            >>> def my_handler(msg, addr):
            ...     print(f"Got: {msg} from {addr}")
            >>> client.on_new_message(my_handler)
        """
        self._new_message_handler.append(func)

    def _run_new_message_handler(self, _func: Callable) -> None:
        """
        Execute a message handler in a loop.

        Continuously receives datagrams and passes them to the
        handler function with their source address.

        Args:
            _func: Message handler function
        """
        while True:
            try:
                data, addr = self.sock.recvfrom(self._recv_size)
                message = data.decode('utf-8')
                _func(message, addr)

            except Exception as e:
                Logger.print_log_error(e, 'FastSocketUDPClient')
                raise e

    def bind(self, address: Tuple[str, int] = None) -> None:
        """
        Bind the socket to a local address.

        Useful for receiving datagrams on a specific port.

        Args:
            address: Local address to bind to (uses config if None)

        Example:
            >>> client.bind(('0.0.0.0', 9000))
        """
        if address is None:
            address = ('0.0.0.0', self._config.port)

        self.sock.bind(address)
        Logger.print_log_debug(f'UDP client bound to {address}')

    def close(self) -> None:
        """
        Close the UDP socket and stop receive loops.

        Example:
            >>> client.close()
        """
        self._running = False
        self.sock.close()
        Logger.print_log_debug('UDP client socket closed')
