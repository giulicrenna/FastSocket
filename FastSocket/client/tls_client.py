"""
Hybrid-encrypted TCP client for FastSocket.

Performs RSA+HMAC key exchange on connect, then uses AES-256-GCM
for all subsequent messages. Both ends authenticate each other
before any application data flows.
"""

import socket
import time
from threading import Thread
from typing import List, Callable

from Crypto.PublicKey import RSA

from FastSocket.core.config import SocketConfig
from FastSocket.security.rsa_encryption import RSAEncryption
from FastSocket.security.tls_encryption import (
    generate_session_key, aes_encrypt, aes_decrypt,
    hmac_sign, hmac_verify, rsa_encrypt_key,
    HMAC_SIZE,
)
from FastSocket.utils.framing import send_framed, recv_framed
from FastSocket.utils.logger import Logger


class TLSSocketClient(Thread):
    """
    TCP client with hybrid RSA+AES encryption and PSK authentication.

    Attributes:
        connected: True after a successful handshake
        _session_key: AES-256 session key shared with the server
        _auto_reconnect: Reconnect automatically on connection loss
        _reconnect_delay: Seconds to wait between reconnect attempts

    Example:
        >>> config = SocketConfig(host='localhost', port=9443)
        >>> client = TLSSocketClient(config, shared_secret="my-secret")
        >>> client.on_new_message(lambda msg: print(msg))
        >>> client.on_disconnect(lambda: print("disconnected"))
        >>> client.start()
        >>> # wait for client.connected == True
        >>> client.send_to_server("Hello!")
    """

    def __init__(self,
                 config: SocketConfig,
                 shared_secret: str,
                 auto_reconnect: bool = False,
                 reconnect_delay: float = 1.0) -> None:
        super().__init__()
        self.daemon = True
        self._config = config
        self._shared_secret: bytes = (
            shared_secret.encode('utf-8')
            if isinstance(shared_secret, str)
            else shared_secret
        )
        self._new_message_handler: List[Callable] = []
        self._disconnect_handlers: List[Callable] = []
        self._session_key: bytes = None
        self.connected: bool = False
        self._running = True
        self._auto_reconnect = auto_reconnect
        self._reconnect_delay = reconnect_delay
        self.sock: socket.socket = self._config._create_socket()

    # ── handshake ─────────────────────────────────────────────────────────────

    def _handshake(self) -> bool:
        try:
            # Step 1: receive server RSA public key
            pub_key_bytes = recv_framed(self.sock)
            if pub_key_bytes is None:
                return False
            server_pub_key = RSA.import_key(pub_key_bytes)

            # Step 2: generate session key, encrypt with server's RSA pub key,
            #         attach HMAC proof of PSK knowledge, send both
            session_key   = generate_session_key()
            encrypted_key = rsa_encrypt_key(server_pub_key, session_key)
            auth_token    = hmac_sign(self._shared_secret, session_key)
            send_framed(self.sock, encrypted_key + auth_token)

            # Step 3: receive server's AES-encrypted OK + server auth token
            raw = recv_framed(self.sock)
            if raw is None:
                return False

            if raw == b"AUTH_FAIL":
                Logger.print_log_error("Authentication rejected by server.", "HybridClient")
                return False

            response = aes_decrypt(session_key, raw)

            if not response.startswith(b"OK"):
                return False

            server_auth = response[2:2 + HMAC_SIZE]
            if not hmac_verify(self._shared_secret, session_key + b"server", server_auth):
                Logger.print_log_error("Server authentication failed (wrong PSK?)", "HybridClient")
                return False

            self._session_key = session_key
            return True

        except Exception as e:
            Logger.print_log_error(e, 'TLSSocketClient handshake')
            return False

    # ── entry point ───────────────────────────────────────────────────────────

    def run(self) -> None:
        self.sock.connect((self._config.host, self._config.port))

        if not self._handshake():
            self.sock.close()
            return

        self.connected = True

        for handler in self._new_message_handler:
            Thread(target=self._recv_loop, args=(handler,), daemon=True).start()

    # ── stop ──────────────────────────────────────────────────────────────────

    def stop(self) -> None:
        """Close the connection and stop receive loops."""
        self._running = False
        self.connected = False
        try:
            self.sock.close()
        except Exception:
            pass

    # ── send / receive ────────────────────────────────────────────────────────

    def send_to_server(self, msg: str) -> None:
        """Send an AES-256-GCM encrypted message to the server."""
        if not self.connected or self._session_key is None:
            return
        try:
            send_framed(self.sock, aes_encrypt(self._session_key, msg.encode('utf-8')))
        except Exception as e:
            Logger.print_log_error(e, 'TLSSocketClient')
            raise

    def on_new_message(self, func: Callable) -> None:
        """Register a callback: func(plaintext_str) called on each message."""
        self._new_message_handler.append(func)

    def on_disconnect(self, func: Callable) -> None:
        """
        Register a disconnect callback.

        Called (with no arguments) when the connection is lost. If
        auto_reconnect is enabled, fires before each reconnect attempt.

        Args:
            func: Callable with no arguments
        """
        self._disconnect_handlers.append(func)

    def _recv_loop(self, func: Callable) -> None:
        while True:
            try:
                raw = recv_framed(self.sock)
                if raw is None:
                    self.connected = False
                    break
                plaintext = aes_decrypt(self._session_key, raw).decode('utf-8')
                func(plaintext)
            except Exception as e:
                Logger.print_log_error(e, 'TLSSocketClient')
                self.connected = False
                break
        self._handle_disconnect(func)

    def _handle_disconnect(self, func: Callable) -> None:
        for handler in self._disconnect_handlers:
            try:
                handler()
            except Exception as e:
                Logger.print_log_error(e, 'TLSSocketClient disconnect handler')

        if self._auto_reconnect and self._running:
            self._reconnect(func)

    def _reconnect(self, func: Callable) -> None:
        while self._running:
            time.sleep(self._reconnect_delay)
            try:
                self.sock = self._config._create_socket()
                self.sock.connect((self._config.host, self._config.port))
                self._session_key = None

                if not self._handshake():
                    self.sock.close()
                    continue

                self.connected = True
                Logger.print_log_normal('Reconnected to TLS server', 'TLSSocketClient')
                Thread(target=self._recv_loop, args=(func,), daemon=True).start()
                return
            except Exception as e:
                Logger.print_log_error(f'Reconnect failed: {e}', 'TLSSocketClient')
