"""
Hybrid-encrypted TCP server for FastSocket.

Uses RSA-4096 for key exchange and AES-256-GCM for all messages.
Clients must supply the correct pre-shared secret (PSK) during the
handshake — connections with a wrong or missing PSK are rejected.
"""

import socket
import time
from threading import Thread, Lock
from typing import List, Callable

from fastsocket.core.config import SocketConfig
from fastsocket.core.tls_handler import TLSClientHandler
from fastsocket.security.rsa_encryption import RSAEncryption
from fastsocket.utils.logger import Logger
from fastsocket.utils.exceptions import InvalidMessageType, NetworkException


class TLSSocketServer(Thread):
    """
    Multi-threaded TCP server with hybrid RSA+AES encryption and PSK auth.

    Attributes:
        _config: Socket configuration
        _client_buffer: Connected and authenticated client handlers
        _client_lock: Lock protecting _client_buffer
        _new_message_handler: Registered message callbacks
        _security: Server RSA key pair

    Example:
        >>> config = SocketConfig(host='localhost', port=9443)
        >>> server = TLSSocketServer(config, shared_secret="my-secret")
        >>> server.on_new_message(lambda q: print(q.get()))
        >>> server.start()
    """

    def __init__(self,
                 config: SocketConfig,
                 shared_secret: str,
                 pub_key_path: str = None,
                 priv_key_path: str = None) -> None:
        super().__init__()
        self.daemon = True
        self._config = config
        self._shared_secret: bytes = (
            shared_secret.encode('utf-8')
            if isinstance(shared_secret, str)
            else shared_secret
        )
        self._client_buffer: List[TLSClientHandler] = []
        self._client_lock = Lock()
        self._new_message_handler: List[Callable] = []
        self._security = RSAEncryption(pub_key_path, priv_key_path)
        self._running = True

    def run(self) -> None:
        Logger.print_log_normal(
            f'Running hybrid server on {self._config.host}:{self._config.port}',
            'HybridServer'
        )
        self.sock: socket.socket = self._config._create_socket()
        try:
            self.sock.bind((self._config.host, self._config.port))
        except OSError:
            raise NetworkException

        Thread(target=self._listen_for_new_clients, daemon=True).start()
        for handler in self._new_message_handler:
            Thread(target=self._run_message_handler, args=(handler,), daemon=True).start()

        while self._running:
            time.sleep(1)

    def stop(self) -> None:
        """Gracefully stop the server."""
        self._running = False
        try:
            self.sock.close()
        except Exception:
            pass

    def _listen_for_new_clients(self) -> None:
        while self._running:
            self.sock.settimeout(5)
            self.sock.listen()
            try:
                # Remove handlers whose threads have finished (failed handshake or disconnected)
                with self._client_lock:
                    self._client_buffer = [c for c in self._client_buffer if c.is_alive()]

                conn, addr = self.sock.accept()
                handler = TLSClientHandler(conn, addr, self._security, self._shared_secret)
                handler.start()

                with self._client_lock:
                    self._client_buffer.append(handler)
            except socket.timeout:
                pass

    def on_new_message(self, func: Callable) -> None:
        """Register a callback: func(queue) called when messages arrive."""
        self._new_message_handler.append(func)

    def _run_message_handler(self, func: Callable) -> None:
        while self._running:
            with self._client_lock:
                clients = list(self._client_buffer)
            found = False
            for client in clients:
                if client.connected and not client.message_queue.empty():
                    func(client.message_queue)
                    found = True
            if not found:
                time.sleep(0.005)

    def send_msg_stream(self, message: str | bytes) -> None:
        """Broadcast an AES-encrypted message to all authenticated clients."""
        if type(message) not in [str, bytes]:
            raise InvalidMessageType
        data = message.encode('utf-8') if isinstance(message, str) else message

        with self._client_lock:
            clients = list(self._client_buffer)

        for client in clients:
            if client.connected:
                try:
                    client.send(data)
                except OSError:
                    pass
