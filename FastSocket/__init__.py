"""
FastSocket - Fast TCP/UDP server and client library with encryption support.

This library provides a simple API for creating TCP and UDP servers and clients
with multi-connection handling and optional RSA encryption.

Example:
    Basic TCP server:
    >>> from fastsocket import FastSocketServer, SocketConfig
    >>> config = SocketConfig(host='localhost', port=8080)
    >>> server = FastSocketServer(config)
    >>> server.start()

    Basic TCP client:
    >>> from fastsocket import FastSocketClient, SocketConfig
    >>> config = SocketConfig(host='localhost', port=8080)
    >>> client = FastSocketClient(config)
    >>> client.start()
"""

__version__ = '2.2.0'
__author__ = 'Giuliano Crenna'
__email__ = 'giulicrenna@gmail.com'

# Core exports
from fastsocket.core.config import SocketConfig, SockerConfig

# Server exports
from fastsocket.server.tcp_server import FastSocketServer
from fastsocket.server.secure_server import SecureFastSocketServer
from fastsocket.server.udp_server import FastSocketUDPServer
from fastsocket.server.tls_server import TLSSocketServer

# Client exports
from fastsocket.client.tcp_client import FastSocketClient
from fastsocket.client.secure_client import SecureFastSocketClient
from fastsocket.client.udp_client import FastSocketUDPClient
from fastsocket.client.tls_client import TLSSocketClient

# Security exports
from fastsocket.security.rsa_encryption import RSAEncryption
from fastsocket.security.tls_encryption import (
    derive_psk, generate_session_key, aes_encrypt, aes_decrypt,
    hmac_sign, hmac_verify,
)

# Utility exports
from fastsocket.utils.logger import Logger, Color
from fastsocket.utils.types import Types
from fastsocket.utils.exceptions import (
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
from fastsocket.utils.chunks import ChunkManager
from fastsocket.utils.file_transfer import FileTransfer

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
    'derive_psk',
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
