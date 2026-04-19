"""
TCP Client module for FastSocket.

This module provides a TCP client implementation with support for
sending and receiving messages from a server.
"""

import socket
from threading import Thread
from typing import List, Callable

from FastSocket.core.config import SocketConfig
from FastSocket.utils.framing import send_framed, recv_framed
from FastSocket.utils.logger import Logger
from FastSocket.utils.types import Types


class FastSocketClient(Thread):
    """
    Multi-threaded TCP client.

    This client can connect to a TCP server, send messages, and
    receive messages asynchronously with registered handlers.

    Attributes:
        _config: Socket configuration
        _new_message_handler: List of message handler functions
        sock: Client socket

    Example:
        >>> def handle_msg(msg):
        ...     print(f"Received: {msg}")
        ...
        >>> config = SocketConfig(host='localhost', port=8080)
        >>> client = FastSocketClient(config)
        >>> client.on_new_message(handle_msg)
        >>> client.start()
        >>> client.send_to_server("Hello server!")
    """

    def __init__(self,
                 config: SocketConfig) -> None:
        super().__init__()
        self.daemon = True
        self._config = config
        self._new_message_handler: List[Callable] = []
        self.sock: socket.socket = self._config._create_socket()

    def run(self) -> None:
        self.sock.connect((self._config.host, self._config.port))

        for _message_handler in self._new_message_handler:
            message_thread = Thread(
                target=self._run_new_message_handler,
                args=(_message_handler,),
                daemon=True,
            )
            message_thread.start()

    def send_to_server(self, msg: str) -> None:
        """
        Send a message to the server.

        Args:
            msg: Message string to send

        Raises:
            Exception: If sending fails

        Example:
            >>> client.send_to_server("Hello!")
        """
        try:
            send_framed(self.sock, msg.encode('utf-8'))
        except Exception as e:
            Logger.print_log_error(e, 'FastSocketClient')
            raise

    def on_new_message(self, func: Callable) -> None:
        """
        Register a message handler function.

        The handler will be called with each message received
        from the server as a string parameter.

        Args:
            func: Callable that accepts a string parameter

        Example:
            >>> def my_handler(msg):
            ...     print(f"Got: {msg}")
            >>> client.on_new_message(my_handler)
        """
        self._new_message_handler.append(func)

    def _run_new_message_handler(self, _func: Callable) -> None:
        while True:
            try:
                data = recv_framed(self.sock)
                if not data:
                    break
                _func(data.decode('utf-8'))
            except Exception as e:
                Logger.print_log_error(e, 'FastSocketClient')
                break
