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

# Client exports
from FastSocket.client.tcp_client import FastSocketClient
from FastSocket.client.secure_client import SecureFastSocketClient

# Security exports
from FastSocket.security.rsa_encryption import RSAEncryption

# Utility exports
from FastSocket.utils.logger import Logger, Color
from FastSocket.utils.types import Types
from FastSocket.utils.exceptions import (
    InvalidMessageType,
    NetworkException,
    BadEncryptionInput,
)

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

    # Clients
    'FastSocketClient',
    'SecureFastSocketClient',

    # Security
    'RSAEncryption',

    # Utils
    'Logger',
    'Color',
    'Types',
    'Queue',

    # Exceptions
    'InvalidMessageType',
    'NetworkException',
    'BadEncryptionInput',
]
