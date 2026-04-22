"""
TCP Client module for FastSocket.

This module provides a TCP client implementation with support for
sending and receiving messages from a server.
"""

import socket
import time
from threading import Thread
from typing import List, Callable, Optional

from fastsocket.core.config import SocketConfig
from fastsocket.utils.framing import send_framed, recv_framed
from fastsocket.utils.logger import Logger
from fastsocket.utils.types import Types


class FastSocketClient(Thread):
    """
    Multi-threaded TCP client.

    This client can connect to a TCP server, send messages, and
    receive messages asynchronously with registered handlers.

    Attributes:
        _config: Socket configuration
        _new_message_handler: List of message handler functions
        _disconnect_handlers: List of disconnect callbacks
        _auto_reconnect: Reconnect automatically on connection loss
        _reconnect_delay: Seconds to wait between reconnect attempts
        sock: Client socket

    Example:
        >>> def handle_msg(msg):
        ...     print(f"Received: {msg}")
        ...
        >>> config = SocketConfig(host='localhost', port=8080)
        >>> client = FastSocketClient(config, auto_reconnect=True)
        >>> client.on_new_message(handle_msg)
        >>> client.on_disconnect(lambda: print("disconnected"))
        >>> client.start()
        >>> client.send_to_server("Hello server!")
    """

    def __init__(self,
                 config: SocketConfig,
                 auto_reconnect: bool = False,
                 reconnect_delay: float = 1.0) -> None:
        super().__init__()
        self.daemon = True
        self._config = config
        self._new_message_handler: List[Callable] = []
        self._disconnect_handlers: List[Callable] = []
        self._auto_reconnect = auto_reconnect
        self._reconnect_delay = reconnect_delay
        self._running = True
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

    def stop(self) -> None:
        """Close the connection and stop receive loops."""
        self._running = False
        try:
            self.sock.close()
        except Exception:
            pass

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

    def on_disconnect(self, func: Callable) -> None:
        """
        Register a disconnect callback.

        The callback is called (with no arguments) when the server closes
        the connection or the network fails. If auto_reconnect is enabled,
        it fires before each reconnect attempt.

        Args:
            func: Callable with no arguments

        Example:
            >>> client.on_disconnect(lambda: print("lost connection"))
        """
        self._disconnect_handlers.append(func)

    def _run_new_message_handler(self, _func: Callable) -> None:
        while True:
            try:
                data = recv_framed(self.sock)
                if data is None:
                    break
                _func(data.decode('utf-8'))
            except Exception as e:
                Logger.print_log_error(e, 'FastSocketClient')
                break
        self._handle_disconnect(_func)

    def _handle_disconnect(self, _func: Callable) -> None:
        for handler in self._disconnect_handlers:
            try:
                handler()
            except Exception as e:
                Logger.print_log_error(e, 'FastSocketClient disconnect handler')

        if self._auto_reconnect and self._running:
            self._reconnect(_func)

    def _reconnect(self, _func: Callable) -> None:
        while self._running:
            time.sleep(self._reconnect_delay)
            try:
                self.sock = self._config._create_socket()
                self.sock.connect((self._config.host, self._config.port))
                Logger.print_log_normal('Reconnected to server', 'FastSocketClient')
                # Restart recv loop for this handler in a new thread
                Thread(
                    target=self._run_new_message_handler,
                    args=(_func,),
                    daemon=True,
                ).start()
                return
            except Exception as e:
                Logger.print_log_error(f'Reconnect failed: {e}', 'FastSocketClient')
