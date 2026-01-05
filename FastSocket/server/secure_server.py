"""
Secure TCP Server module for FastSocket.

This module provides a multi-threaded TCP server with RSA encryption
for secure communication with clients.
"""

import socket
from threading import Thread
from typing import List, Callable

from FastSocket.core.config import SocketConfig
from FastSocket.core.client_handler import SecureClientType
from FastSocket.security.rsa_encryption import RSAEncryption
from FastSocket.utils.logger import Logger
from FastSocket.utils.exceptions import InvalidMessageType, NetworkException
from FastSocket.utils.types import Types


class SecureFastSocketServer(Thread):
    """
    Multi-threaded TCP server with RSA encryption.

    This server handles encrypted communication with clients using RSA.
    It manages key exchange and encrypted message transmission.

    Attributes:
        _config: Socket configuration
        _client_buffer: List of connected secure client handlers
        _new_message_handler: List of message handler functions
        _security: RSA encryption handler
        sock: Server socket

    Example:
        >>> def handle_msg(queue):
        ...     while not queue.empty():
        ...         msg, addr = queue.get()
        ...         print(f"From {addr}: {msg}")
        ...
        >>> config = SocketConfig(host='localhost', port=8080)
        >>> server = SecureFastSocketServer(config)
        >>> server.on_new_message(handle_msg)
        >>> server.start()
    """

    def __init__(self,
                 config: SocketConfig,
                 pub_key_path: str = None,
                 priv_key_path: str = None,
                 _recv_size: int = 1024*10) -> None:
        """
        Initialize secure TCP server.

        Args:
            config: Socket configuration object
            pub_key_path: Path to public key file (optional)
            priv_key_path: Path to private key file (optional)
            _recv_size: Maximum bytes to receive at once (default: 10KB)

        Note:
            If key paths are not provided, new RSA keys will be generated.
        """
        super().__init__()
        self._config = config
        self._client_buffer: List[SecureClientType] = []
        self._new_message_handler: List[Callable] = []
        self._recv_size = _recv_size

        if pub_key_path is not None and priv_key_path is not None:
            Logger.print_log_debug('Loading RSA key pair.')
        else:
            Logger.print_log_debug('No key paths provided. Generating new RSA key pair.')
        self._security = RSAEncryption(pub_key_path, priv_key_path)
        Logger.print_log_debug('RSA key pair loaded succesfully.')

    def run(self) -> None:
        """
        Start the secure server.

        Creates the server socket, binds to the configured address,
        and starts threads for key exchange, client listening, and
        message handling.

        Raises:
            NetworkException: If unable to bind to the specified address
        """
        Logger.print_log_normal(f'Running server on {self._config.host}:{self._config.port}', 'Server')
        self.sock: socket.socket = self._config._create_socket()

        try:
            self.sock.bind((self._config.host, self._config.port))
        except OSError:
            raise NetworkException

        task_send_pub_key = Thread(target=self._send_server_pub_key, name="_send_server_pub_key")
        task_send_pub_key.start()

        task_wait_for_client = Thread(target=self._listen_for_new_clients)
        task_wait_for_client.start()

        for _message_handler in self._new_message_handler:
            message_thread = Thread(target=self._run_new_message_handler, args=(_message_handler,))
            message_thread.start()

    def _send_server_pub_key(self) -> None:
        """
        Send server's public key to clients after key exchange.

        Runs in a separate thread, sending the public key to each
        client once their public key has been received.
        """
        while True:
            for client in self._client_buffer:
                if client.public_key is not None and self._security.pub_key is not None and not client.full_reached:
                    client.connection.sendall(self._security.pub_key.export_key())
                    client.full_reached = True

    def _listen_for_new_clients(self) -> None:
        """
        Listen for and accept new encrypted client connections.

        Runs in a separate thread, accepting new connections and
        creating SecureClientType handlers for each. Also removes
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

                client_handler = SecureClientType(conn, addr, self._recv_size, self._security)
                client_handler.connection.sendall(f'Send public key with size: 4096 bytes\n'.encode('utf-8'))
                client_handler.start()

                self._client_buffer.append(client_handler)
            except socket.timeout:
                pass

    def on_new_message(self, func: Callable) -> None:
        """
        Register a message handler function.

        The handler will be called with a Queue containing decrypted
        messages from connected clients.

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
                if client.connected and not client.message_queue.empty():
                    _func(client.message_queue)

    def send_msg_stream(self, message: str | bytes) -> None:
        """
        Broadcast an encrypted message to all connected clients.

        The message is encrypted with each client's public key before
        being sent.

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
                if client.full_reached and client.connected:
                    client.connection.sendall(self._security.encrypt(message, client.public_key))
            except OSError:
                pass
