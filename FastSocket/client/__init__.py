"""Client module for FastSocket."""

from fastsocket.client.tcp_client import FastSocketClient
from fastsocket.client.secure_client import SecureFastSocketClient
from fastsocket.client.udp_client import FastSocketUDPClient

__all__ = [
    'FastSocketClient',
    'SecureFastSocketClient',
    'FastSocketUDPClient',
]
