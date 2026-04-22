"""
UDP Server module for FastSocket.

This module provides a UDP server implementation with support for
multiple concurrent datagram sources and optional broadcast.
"""

import socket
from threading import Thread, Lock
from typing import Dict, List, Callable, Tuple
from time import time

from FastSocket.core.config import SocketConfig
from FastSocket.core.udp_handler import UDPClientHandler
from FastSocket.utils.logger import Logger
from FastSocket.utils.exceptions import InvalidMessageType


class FastSocketUDPServer(Thread):
    """
    Multi-threaded UDP server with datagram handling.

    This server handles UDP datagrams from multiple sources, tracking
    active sources and processing messages with registered handlers.

    Attributes:
        _config: Socket configuration
        _client_buffer: Dictionary of active UDP sources
        _new_message_handler: List of message handler functions
        _recv_size: Maximum datagram size
        _timeout: Client timeout in seconds
        _enable_broadcast: Enable broadcast support
        sock: Server socket

    Example:
        >>> def handle_msg(queue):
        ...     while not queue.empty():
        ...         msg, addr = queue.get()
        ...         print(f"From {addr}: {msg}")
        ...
        >>> config = SocketConfig(host='0.0.0.0', port=8080,
        ...                       type=socket.SOCK_DGRAM)
        >>> server = FastSocketUDPServer(config)
        >>> server.on_new_message(handle_msg)
        >>> server.start()
    """

    def __init__(self,
                 config: SocketConfig,
                 recv_size: int = 65507,  # Max UDP packet size
                 client_timeout: float = 30.0,
                 enable_broadcast: bool = False) -> None:
        """
        Initialize UDP server.

        Args:
            config: Socket configuration (should use SOCK_DGRAM)
            recv_size: Maximum datagram size (default: 65507 bytes)
            client_timeout: Timeout for inactive sources in seconds
            enable_broadcast: Enable UDP broadcast support
        """
        super().__init__()
        self.daemon = True
        self._config = config
        self._client_buffer: Dict[Tuple[str, int], UDPClientHandler] = {}
        self._client_lock = Lock()
        self._new_message_handler: List[Callable] = []
        self._recv_size = recv_size
        self._timeout = client_timeout
        self._enable_broadcast = enable_broadcast
        self._running = True

    def run(self) -> None:
        """
        Start the UDP server.

        Creates the server socket, binds to the configured address,
        and starts threads for receiving datagrams and handling messages.
        """
        Logger.print_log_normal(
            f'Running UDP server on {self._config.host}:{self._config.port}',
            'UDPServer'
        )

        self.sock: socket.socket = self._config._create_socket()

        # Enable broadcast if requested
        if self._enable_broadcast:
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            Logger.print_log_debug('UDP broadcast enabled')

        self.sock.bind((self._config.host, self._config.port))

        # Start receiver thread
        receiver_thread = Thread(target=self._receive_datagrams)
        receiver_thread.daemon = True
        receiver_thread.start()

        # Start message handler threads
        for _message_handler in self._new_message_handler:
            message_thread = Thread(
                target=self._run_new_message_handler,
                args=(_message_handler,)
            )
            message_thread.daemon = True
            message_thread.start()

        # Start cleanup thread
        cleanup_thread = Thread(target=self._cleanup_inactive_clients)
        cleanup_thread.daemon = True
        cleanup_thread.start()

        while self._running:
            receiver_thread.join(timeout=1)

    def stop(self) -> None:
        """Gracefully stop the server."""
        self._running = False
        try:
            self.sock.close()
        except Exception:
            pass

    def _receive_datagrams(self) -> None:
        while self._running:
            try:
                data, addr = self.sock.recvfrom(self._recv_size)

                if data:
                    message = data.decode('utf-8')

                    with self._client_lock:
                        if addr not in self._client_buffer:
                            self._client_buffer[addr] = UDPClientHandler(addr)
                            Logger.print_log_debug(f'New UDP source: {addr}')
                        self._client_buffer[addr].add_message(message)

            except OSError:
                break
            except Exception as e:
                Logger.print_log_error(f'Error receiving datagram: {e}', 'UDPServer')

    def _cleanup_inactive_clients(self) -> None:
        import time
        while self._running:
            time.sleep(10)

            with self._client_lock:
                to_remove = [
                    addr for addr, handler in self._client_buffer.items()
                    if handler.is_timeout(self._timeout)
                ]
                for addr in to_remove:
                    del self._client_buffer[addr]
                    Logger.print_log_debug(f'Removed inactive UDP source: {addr}')

    def on_new_message(self, func: Callable) -> None:
        """
        Register a message handler function.

        The handler will be called with a Queue containing messages
        from datagram sources.

        Args:
            func: Callable that accepts a Queue parameter

        Example:
            >>> def my_handler(msg_queue):
            ...     while not msg_queue.empty():
            ...         msg, addr = msg_queue.get()
            ...         print(f"{addr}: {msg}")
            >>> server.on_new_message(my_handler)
        """
        self._new_message_handler.append(func)

    def _run_new_message_handler(self, _func: Callable) -> None:
        import time
        while self._running:
            with self._client_lock:
                handlers = list(self._client_buffer.values())
            found = False
            for handler in handlers:
                if handler.active and not handler.message_queue.empty():
                    _func(handler.message_queue)
                    found = True
            if not found:
                time.sleep(0.005)

    def send_to(self, address: Tuple[str, int], message: str | bytes) -> int:
        """
        Send a message to a specific address.

        Args:
            address: Destination address (host, port)
            message: Message to send (string or bytes)

        Returns:
            int: Number of bytes sent

        Raises:
            InvalidMessageType: If message is not str or bytes

        Example:
            >>> server.send_to(('192.168.1.100', 9000), "Hello!")
        """
        if type(message) not in [str, bytes]:
            raise InvalidMessageType

        if isinstance(message, str):
            message = message.encode('utf-8')

        return self.sock.sendto(message, address)

    def broadcast(self, message: str | bytes, port: int = None) -> List[int]:
        """
        Broadcast a message to all known sources.

        Args:
            message: Message to broadcast
            port: Optional port override (uses source ports if None)

        Returns:
            List[int]: Bytes sent to each destination

        Raises:
            InvalidMessageType: If message is not str or bytes

        Example:
            >>> server.broadcast("Hello everyone!")
        """
        if type(message) not in [str, bytes]:
            raise InvalidMessageType

        results = []
        with self._client_lock:
            addrs = list(self._client_buffer.keys())
        for addr in addrs:
            target_addr = (addr[0], port if port else addr[1])
            try:
                bytes_sent = self.send_to(target_addr, message)
                results.append(bytes_sent)
            except Exception as e:
                Logger.print_log_error(f'Failed to send to {addr}: {e}', 'UDPServer')

        return results

    def get_active_sources(self) -> List[Tuple[str, int]]:
        """
        Get list of active UDP sources.

        Returns:
            List of (host, port) tuples

        Example:
            >>> sources = server.get_active_sources()
            >>> print(f"Active sources: {len(sources)}")
        """
        with self._client_lock:
            return [addr for addr, handler in self._client_buffer.items() if handler.active]
