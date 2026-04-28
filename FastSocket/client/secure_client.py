"""
Secure TCP Client module for FastSocket.

This module provides a TCP client with RSA encryption for secure
communication with a server.
"""

import socket
from threading import Thread
from typing import List, Callable

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

from fastsocket.core.config import SocketConfig
from fastsocket.security.rsa_encryption import RSAEncryption
from fastsocket.utils.logger import Logger
from fastsocket.utils.types import Types


class SecureFastSocketClient(Thread):
    """
    Multi-threaded TCP client with RSA encryption.

    This client establishes an encrypted connection with a server,
    exchanges RSA public keys, and handles encrypted message transmission.

    Attributes:
        _config: Socket configuration
        _new_message_handler: List of message handler functions
        _recv_size: Maximum bytes to receive at once
        _security: RSA encryption handler
        server_pub_key: Server's RSA public key
        sock: Client socket

    Example:
        >>> def handle_msg(msg):
        ...     print(f"Received: {msg}")
        ...
        >>> config = SocketConfig(host='localhost', port=8080)
        >>> client = SecureFastSocketClient(config)
        >>> client.on_new_message(handle_msg)
        >>> client.start()
        >>> client.send_to_server("Hello server!")
    """

    def __init__(self,
                 config: SocketConfig,
                 pub_key_path: str = None,
                 priv_key_path: str = None,
                 _recv_size: int = 1024*10) -> None:
        """
        Initialize secure TCP client.

        Args:
            config: Socket configuration object
            pub_key_path: Path to public key file (optional)
            priv_key_path: Path to private key file (optional)
            _recv_size: Maximum bytes to receive at once (default: 10KB)

        Note:
            If key paths are not provided, new RSA keys will be generated.
        """
        super().__init__()
        self.daemon = True
        self._config = config
        self._new_message_handler: List[Callable] = []
        self._recv_size = _recv_size
        self.server_pub_key: RSA.RsaKey = None
        self._running = True

        if pub_key_path is not None and priv_key_path is not None:
            Logger.print_log_debug('Loading RSA key pair.')
        else:
            Logger.print_log_debug('No key paths provided. Generating new RSA key pair.')
        self._security = RSAEncryption(pub_key_path, priv_key_path)
        Logger.print_log_debug('RSA key pair loaded succesfully.')

    def run(self) -> None:
        """
        Connect to server and perform key exchange.

        Establishes connection, exchanges public keys with the server,
        and starts message handler threads.
        """
        Logger.print_log_normal(f'Running server on {self._config.host}:{self._config.port}', 'Server')
        self.sock: socket.socket = self._config._create_socket()
        self.sock.connect((self._config.host, self._config.port))

        ord: bytes = self.sock.recv(self._recv_size)
        self.sock.sendall(self._security.pub_key.export_key())

        self.server_pub_key = RSA.import_key(self.sock.recv(self._recv_size))

        for _message_handler in self._new_message_handler:
            message_thread = Thread(target=self._run_new_message_handler, args=(_message_handler,))
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
        Send an encrypted message to the server.

        The message is encrypted with the server's public key before sending.

        Args:
            msg: Message string to send

        Raises:
            Exception: If sending fails

        Example:
            >>> client.send_to_server("Hello!")
        """
        if self.server_pub_key is None:
            return
        try:
            # RSAEncryption.encrypt() validates the payload size and raises
            # BadEncryptionInput if it exceeds the key's OAEP limit.
            message = self._security.encrypt(msg, self.server_pub_key)
            self.sock.sendall(message)
        except Exception as e:
            Logger.print_log_error(e, 'SecureFastSocketClient')
            raise

    def on_new_message(self, func: Callable) -> None:
        """
        Register a message handler function.

        The handler will be called with each decrypted message
        received from the server as a string parameter.

        Args:
            func: Callable that accepts a string parameter

        Example:
            >>> def my_handler(msg):
            ...     print(f"Got: {msg}")
            >>> client.on_new_message(my_handler)
        """
        self._new_message_handler.append(func)

    def _run_new_message_handler(self, _func: Callable) -> None:
        """
        Execute a message handler in a loop.

        Continuously receives encrypted messages from the server,
        decrypts them, and passes them to the handler function.

        Args:
            _func: Message handler function
        """
        while True:
            try:
                msg = self.sock.recv(self._recv_size)
                cipher = PKCS1_OAEP.new(self._security.priv_key)
                decrypted_msg = cipher.decrypt(msg).decode('utf-8')
                _func(decrypted_msg)
            except Exception as e:
                Logger.print_log_error(e, 'FastSocketClient')
                raise e
