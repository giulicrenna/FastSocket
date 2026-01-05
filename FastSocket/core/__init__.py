"""Core module for FastSocket."""

from FastSocket.core.config import SocketConfig, SockerConfig
from FastSocket.core.client_handler import ClientType, SecureClientType

__all__ = [
    'SocketConfig',
    'SockerConfig',  # Deprecated alias
    'ClientType',
    'SecureClientType',
]
