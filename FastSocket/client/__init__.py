"""Client module for FastSocket."""

from FastSocket.client.tcp_client import FastSocketClient
from FastSocket.client.secure_client import SecureFastSocketClient
from FastSocket.client.udp_client import FastSocketUDPClient

__all__ = [
    'FastSocketClient',
    'SecureFastSocketClient',
    'FastSocketUDPClient',
]
