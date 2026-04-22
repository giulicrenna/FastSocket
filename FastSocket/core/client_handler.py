"""
Client handler module for FastSocket.

This module contains client handler classes for managing individual
client connections on the server side.
"""

import socket
from threading import Thread
from queue import Queue
from typing import Tuple

from Crypto.PublicKey import RSA

from FastSocket.utils.types import Types
from FastSocket.utils.framing import recv_framed
from FastSocket.security.rsa_encryption import RSAEncryption
from FastSocket.utils.logger import Logger


class ClientType(Thread):
    """
    Handler for a single TCP client connection.

    This class runs in its own thread and manages receiving messages
    from a connected client.

    Attributes:
        connection: Socket connection to the client
        address: Client's (host, port) tuple
        message_queue: Queue for storing received messages
        connected: Connection status flag
    """

    def __init__(self,
                 connection: socket.socket,
                 address: Tuple[str, int]) -> None:
        super().__init__()
        self.daemon = True
        self.connection: socket.socket = connection
        self.address: Tuple[str, int] = address
        self.message_queue: Queue = Queue()
        self.connected: bool = True

    def run(self):
        while True:
            try:
                data = recv_framed(self.connection)
                if data is None:
                    self.connected = False
                    self.connection.close()
                    break
                self.message_queue.put((data.decode("utf-8"), self.address))
            except Exception:
                self.connected = False
                self.connection.close()
                break


class SecureClientType(Thread):
    """
    Handler for a single encrypted TCP client connection.

    This class manages RSA-encrypted communication with a client,
    including key exchange and encrypted message handling.

    Attributes:
        connection: Socket connection to the client
        address: Client's (host, port) tuple
        message_queue: Queue for storing decrypted messages
        connected: Connection status flag
        public_key: Client's RSA public key
        server_security: Server's RSA encryption handler
        full_reached: Flag indicating key exchange completion
    """

    def __init__(self,
                 connection: socket.socket,
                 address: Tuple[str, int],
                 recv_size: int,
                 server_security: RSAEncryption) -> None:
        super().__init__()
        self.daemon = True
        self.connection: socket.socket = connection
        self.address: Tuple[str, int] = address
        self.message_queue: Queue = Queue()
        self.connected: bool = True
        self.full_reached: bool = False
        self._recv_size = recv_size
        self.public_key: RSA.RsaKey = None
        self.server_security = server_security

    def run(self):
        while True:
            try:
                if self.public_key is None:
                    try:
                        pub_key_bytes = self.connection.recv(self._recv_size)
                        if not pub_key_bytes:
                            self.connected = False
                            self.connection.close()
                            break
                        self.public_key = RSA.import_key(pub_key_bytes)
                        Logger.print_log_debug(self.public_key)
                    except Exception as e:
                        self.connection.sendall('Invalid Public Key'.encode('utf-8'))
                        Logger.print_log_error(e, 'SecureClientType key exchange')
                else:
                    data: bytes = self.connection.recv(self._recv_size)
                    if not data:
                        self.connected = False
                        self.connection.close()
                        break
                    message = self.server_security.decrypt(data)
                    self.message_queue.put((message, self.address))
                self.connected = True
            except Exception as e:
                Logger.print_log_error(e, 'SecureClientType')
                self.connected = False
                self.connection.close()
                break
