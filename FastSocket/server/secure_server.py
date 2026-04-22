"""
Secure TCP Server module for FastSocket.

This module provides a multi-threaded TCP server with RSA encryption
for secure communication with clients.
"""

import socket
import time
from threading import Thread, Lock
from typing import List, Callable

from fastsocket.core.config import SocketConfig
from fastsocket.core.client_handler import SecureClientType
from fastsocket.security.rsa_encryption import RSAEncryption
from fastsocket.utils.logger import Logger
from fastsocket.utils.exceptions import InvalidMessageType, NetworkException
from fastsocket.utils.types import Types


class SecureFastSocketServer(Thread):
    """
    Multi-threaded TCP server with RSA encryption.

    This server handles encrypted communication with clients using RSA.
    It manages key exchange and encrypted message transmission.

    Attributes:
        _config: Socket configuration
        _client_buffer: List of connected secure client handlers
        _client_lock: Lock protecting _client_buffer
        _new_message_handler: List of message handler functions
        _security: RSA encryption handler
        sock: Server socket
    """

    def __init__(self,
                 config: SocketConfig,
                 pub_key_path: str = None,
                 priv_key_path: str = None,
                 _recv_size: int = 1024*10) -> None:
        super().__init__()
        self.daemon = True
        self._config = config
        self._client_buffer: List[SecureClientType] = []
        self._client_lock = Lock()
        self._new_message_handler: List[Callable] = []
        self._recv_size = _recv_size
        self._running = True

        if pub_key_path is not None and priv_key_path is not None:
            Logger.print_log_debug('Loading RSA key pair.')
        else:
            Logger.print_log_debug('No key paths provided. Generating new RSA key pair.')
        self._security = RSAEncryption(pub_key_path, priv_key_path)
        Logger.print_log_debug('RSA key pair loaded succesfully.')

    def run(self) -> None:
        Logger.print_log_normal(f'Running secure server on {self._config.host}:{self._config.port}', 'SecureServer')
        self.sock: socket.socket = self._config._create_socket()

        try:
            self.sock.bind((self._config.host, self._config.port))
        except OSError:
            raise NetworkException

        Thread(target=self._send_server_pub_key, daemon=True).start()
        Thread(target=self._listen_for_new_clients, daemon=True).start()

        for _message_handler in self._new_message_handler:
            Thread(target=self._run_new_message_handler, args=(_message_handler,), daemon=True).start()

        while self._running:
            time.sleep(1)

    def stop(self) -> None:
        """Gracefully stop the server."""
        self._running = False
        try:
            self.sock.close()
        except Exception:
            pass

    def _send_server_pub_key(self) -> None:
        """Send server public key to each client once their key is received."""
        while self._running:
            with self._client_lock:
                clients = list(self._client_buffer)
            for client in clients:
                if client.public_key is not None and not client.full_reached:
                    try:
                        client.connection.sendall(self._security.pub_key.export_key())
                        client.full_reached = True
                    except OSError:
                        pass
            time.sleep(0.05)

    def _listen_for_new_clients(self) -> None:
        while self._running:
            self.sock.settimeout(5)
            self.sock.listen()
            try:
                with self._client_lock:
                    self._client_buffer = [c for c in self._client_buffer if c.connected]

                conn, addr = self.sock.accept()

                client_handler = SecureClientType(conn, addr, self._recv_size, self._security)
                client_handler.connection.sendall(b'Send public key with size: 4096 bytes\n')
                client_handler.start()

                with self._client_lock:
                    self._client_buffer.append(client_handler)
            except socket.timeout:
                pass

    def on_new_message(self, func: Callable) -> None:
        """Register a message handler function."""
        self._new_message_handler.append(func)

    def _run_new_message_handler(self, _func: Callable) -> None:
        while self._running:
            with self._client_lock:
                clients = list(self._client_buffer)
            found = False
            for client in clients:
                if client.connected and not client.message_queue.empty():
                    _func(client.message_queue)
                    found = True
            if not found:
                time.sleep(0.005)

    def send_msg_stream(self, message: str | bytes) -> None:
        """Broadcast an encrypted message to all connected clients."""
        if type(message) not in [str, bytes]:
            raise InvalidMessageType

        with self._client_lock:
            clients = list(self._client_buffer)

        for client in clients:
            try:
                if client.full_reached and client.connected:
                    client.connection.sendall(self._security.encrypt(message, client.public_key))
            except OSError:
                pass
