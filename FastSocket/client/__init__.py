"""Client module for FastSocket."""

from FastSocket.client.tcp_client import FastSocketClient
from FastSocket.client.secure_client import SecureFastSocketClient

__all__ = [
    'FastSocketClient',
    'SecureFastSocketClient',
]
