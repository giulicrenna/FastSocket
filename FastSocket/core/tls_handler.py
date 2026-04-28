"""
Server-side per-client handler for hybrid-encrypted connections.

Handshake (runs once, blocking, in this thread):
  1. Server → Client : RSA public key  (framed)
  2. Client → Server : RSA_enc(session_key) + HMAC(session_key, psk)  (framed)
  3. Server verifies HMAC, decrypts session key
  4. Server → Client : AES_enc("OK" + HMAC(session_key+"server", psk))  (framed)
  5. Client verifies server auth token → mutual authentication complete

After handshake, every message is AES-256-GCM encrypted and framed.
"""

import socket
from threading import Thread
from queue import Queue
from typing import Tuple

from fastsocket.security.rsa_encryption import RSAEncryption
from fastsocket.security.tls_encryption import (
    aes_encrypt, aes_decrypt,
    hmac_sign, hmac_verify,
    rsa_decrypt_key,
    RSA_BLOCK, HMAC_SIZE,
)
from fastsocket.utils.framing import send_framed, recv_framed
from fastsocket.utils.logger import Logger


class TLSClientHandler(Thread):
    """
    Handler for a single hybrid-encrypted TCP client connection.

    Attributes:
        connection: Raw socket to the client
        address: (host, port) of the client
        message_queue: Decrypted messages ready to consume
        connected: True once the handshake succeeds and while receiving
    """

    def __init__(self,
                 connection: socket.socket,
                 address: Tuple[str, int],
                 server_security: RSAEncryption,
                 shared_secret: bytes) -> None:
        super().__init__()
        self.daemon = True
        self.connection = connection
        self.address = address
        self.message_queue: Queue = Queue()
        self.connected: bool = False
        self._server_security = server_security
        # The server already derived the PSK via derive_psk(); use it as-is.
        self._shared_secret = shared_secret
        self._session_key: bytes = None

    # ── handshake ─────────────────────────────────────────────────────────────

    def _handshake(self) -> bool:
        try:
            # Step 1: send server RSA public key
            send_framed(self.connection, self._server_security.pub_key.export_key())

            # Step 2: receive RSA_enc(session_key) + HMAC token
            payload = recv_framed(self.connection)
            if len(payload) < RSA_BLOCK + HMAC_SIZE:
                return False

            encrypted_key = payload[:RSA_BLOCK]
            client_hmac   = payload[RSA_BLOCK:RSA_BLOCK + HMAC_SIZE]

            # Step 3: decrypt session key and verify client auth
            session_key = rsa_decrypt_key(self._server_security.priv_key, encrypted_key)

            if not hmac_verify(self._shared_secret, session_key, client_hmac):
                send_framed(self.connection, b"AUTH_FAIL")
                Logger.print_log_error(f'Auth failed for {self.address}', 'HybridHandler')
                return False

            # Step 4: send AES-encrypted OK + server auth token
            server_auth = hmac_sign(self._shared_secret, session_key + b"server")
            send_framed(self.connection, aes_encrypt(session_key, b"OK" + server_auth))

            self._session_key = session_key
            return True

        except Exception as e:
            Logger.print_log_error(e, 'HybridHandler handshake')
            return False

    # ── main loop ─────────────────────────────────────────────────────────────

    def run(self) -> None:
        if not self._handshake():
            self.connection.close()
            return

        self.connected = True

        while True:
            try:
                raw = recv_framed(self.connection)
                if raw is None:
                    self.connected = False
                    self.connection.close()
                    break
                plaintext = aes_decrypt(self._session_key, raw).decode('utf-8')
                self.message_queue.put((plaintext, self.address))
            except Exception:
                self.connected = False
                self.connection.close()
                break

    # ── send ──────────────────────────────────────────────────────────────────

    def send(self, data: bytes) -> None:
        """Send AES-256-GCM encrypted data to this client."""
        if self._session_key is None:
            return
        send_framed(self.connection, aes_encrypt(self._session_key, data))
