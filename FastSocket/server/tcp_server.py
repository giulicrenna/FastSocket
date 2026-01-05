"""
TCP Server module for FastSocket.

This module provides a multi-threaded TCP server implementation
with support for multiple concurrent client connections.
"""

import socket
from threading import Thread
from typing import List, Callable

from FastSocket.core.config import SocketConfig
from FastSocket.core.client_handler import ClientType
from FastSocket.utils.logger import Logger
from FastSocket.utils.exceptions import InvalidMessageType
from FastSocket.utils.types import Types


class FastSocketServer(Thread):
    """
    Multi-threaded TCP server with concurrent client handling.

    This server can handle multiple client connections simultaneously,
    with each client running in its own thread. Messages from clients
    are processed by registered message handlers.

    Attributes:
        _config: Socket configuration
        _client_buffer: List of connected client handlers
        _new_message_handler: List of message handler functions
        sock: Server socket

    Example:
        >>> def handle_msg(queue):
        ...     while not queue.empty():
        ...         msg, addr = queue.get()
        ...         print(f"From {addr}: {msg}")
        ...
        >>> config = SocketConfig(host='localhost', port=8080)
        >>> server = FastSocketServer(config)
        >>> server.on_new_message(handle_msg)
        >>> server.start()
    """

    def __init__(self,
                 config: SocketConfig) -> None:
        """
        Initialize TCP server.

        Args:
            config: Socket configuration object
        """
        super().__init__()
        self._config = config
        self._client_buffer: List[ClientType] = []
        self._new_message_handler: List[Callable] = []

    def run(self) -> None:
        """
        Start the server.

        Creates the server socket, binds to the configured address,
        and starts threads for listening to clients and handling messages.
        """
        Logger.print_log_normal(f'Running server on {self._config.host}:{self._config.port}', 'Server')
        self.sock: socket.socket = self._config._create_socket()
        self.sock.bind((self._config.host, self._config.port))

        task_wait_for_client = Thread(target=self._listen_for_new_clients)
        task_wait_for_client.start()
        for _message_handler in self._new_message_handler:
            message_thread = Thread(target=self._run_new_message_handler, args=(_message_handler,))
            message_thread.start()

    def _listen_for_new_clients(self) -> None:
        """
        Listen for and accept new client connections.

        Runs in a separate thread, accepting new connections and
        creating ClientType handlers for each. Also removes
        disconnected clients from the buffer.
        """
        while True:
            self.sock.settimeout(5)
            self.sock.listen()

            try:
                for idx, client in enumerate(self._client_buffer):
                    if not client.connected:
                        del self._client_buffer[idx]

                conn, addr = self.sock.accept()

                client_handler = ClientType(conn, addr)
                client_handler.start()

                self._client_buffer.append(client_handler)
            except socket.timeout:
                pass

    def on_new_message(self, func: Callable) -> None:
        """
        Register a message handler function.

        The handler will be called with a Queue containing messages
        from connected clients. Multiple handlers can be registered.

        Args:
            func: Callable that accepts a Queue parameter

        Example:
            >>> def my_handler(msg_queue):
            ...     while not msg_queue.empty():
            ...         msg, addr = msg_queue.get()
            ...         print(msg)
            >>> server.on_new_message(my_handler)
        """
        self._new_message_handler.append(func)

    def _run_new_message_handler(self, _func: Callable) -> None:
        """
        Execute a message handler in a loop.

        Args:
            _func: Message handler function
        """
        while True:
            for client in self._client_buffer:
                if client.connected:
                    _func(client.message_queue)

    def send_msg_stream(self, message: str | bytes) -> None:
        """
        Broadcast a message to all connected clients.

        Args:
            message: Message to send (string or bytes)

        Raises:
            InvalidMessageType: If message is not str or bytes

        Example:
            >>> server.send_msg_stream("Hello all clients!")
        """
        if type(message) not in [str, bytes]:
            raise InvalidMessageType
        for idx, client in enumerate(self._client_buffer):
            try:
                if type(message) == bytes:
                    client.connection.sendall(message)
                elif type(message) == str:
                    client.connection.sendall(message.encode())
            except OSError:
                del self._client_buffer[idx]
