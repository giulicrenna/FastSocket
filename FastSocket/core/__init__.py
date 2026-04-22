"""Core module for FastSocket."""

from fastsocket.core.config import SocketConfig, SockerConfig
from fastsocket.core.client_handler import ClientType, SecureClientType
from fastsocket.core.udp_handler import UDPClientHandler

__all__ = [
    'SocketConfig',
    'SockerConfig',  # Deprecated alias
    'ClientType',
    'SecureClientType',
    'UDPClientHandler',
]
