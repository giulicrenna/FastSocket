"""
FastSocket - Fast TCP/UDP server and client library with encryption support.

This library provides a simple API for creating TCP and UDP servers and clients
with multi-connection handling and optional RSA encryption.

Example:
    Basic TCP server:
    >>> from FastSocket import FastSocketServer, SocketConfig
    >>> config = SocketConfig(host='localhost', port=8080)
    >>> server = FastSocketServer(config)
    >>> server.start()

    Basic TCP client:
    >>> from FastSocket import FastSocketClient, SocketConfig
    >>> config = SocketConfig(host='localhost', port=8080)
    >>> client = FastSocketClient(config)
    >>> client.start()
"""

__version__ = '2.0.0'
__author__ = 'Giuliano Crenna'
__email__ = 'giulicrenna@gmail.com'

# Core exports
from FastSocket.core.config import SocketConfig, SockerConfig

# Server exports
from FastSocket.server.tcp_server import FastSocketServer
from FastSocket.server.secure_server import SecureFastSocketServer
from FastSocket.server.udp_server import FastSocketUDPServer
from FastSocket.server.tls_server import TLSSocketServer

# Client exports
from FastSocket.client.tcp_client import FastSocketClient
from FastSocket.client.secure_client import SecureFastSocketClient
from FastSocket.client.udp_client import FastSocketUDPClient
from FastSocket.client.tls_client import TLSSocketClient

# Security exports
from FastSocket.security.rsa_encryption import RSAEncryption
from FastSocket.security.tls_encryption import (
    generate_session_key, aes_encrypt, aes_decrypt,
    hmac_sign, hmac_verify,
)

# Utility exports
from FastSocket.utils.logger import Logger, Color
from FastSocket.utils.types import Types
from FastSocket.utils.exceptions import (
    FastSocketException,
    InvalidMessageType,
    NetworkException,
    BadEncryptionInput,
    ConnectionClosedException,
    FileTransferException,
    IntegrityException,
    ChunkException,
    TimeoutException,
)
from FastSocket.utils.chunks import ChunkManager
from FastSocket.utils.file_transfer import FileTransfer

# For compatibility with Queue usage in examples
from queue import Queue

__all__ = [
    # Version info
    '__version__',
    '__author__',
    '__email__',

    # Core
    'SocketConfig',
    'SockerConfig',  # Deprecated - use SocketConfig

    # Servers
    'FastSocketServer',
    'SecureFastSocketServer',
    'FastSocketUDPServer',
    'TLSSocketServer',

    # Clients
    'FastSocketClient',
    'SecureFastSocketClient',
    'FastSocketUDPClient',
    'TLSSocketClient',

    # Security
    'RSAEncryption',
    'generate_session_key',
    'aes_encrypt',
    'aes_decrypt',
    'hmac_sign',
    'hmac_verify',

    # Utils
    'Logger',
    'Color',
    'Types',
    'Queue',
    'ChunkManager',
    'FileTransfer',

    # Exceptions
    'FastSocketException',
    'InvalidMessageType',
    'NetworkException',
    'BadEncryptionInput',
    'ConnectionClosedException',
    'FileTransferException',
    'IntegrityException',
    'ChunkException',
    'TimeoutException',
]
