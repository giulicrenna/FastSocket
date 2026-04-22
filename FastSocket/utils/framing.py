"""
Length-prefix framing for TCP streams.

Wraps messages as: [4-byte big-endian length][payload]
This ensures each recv() call reconstructs exactly one message,
regardless of how TCP splits or merges the underlying bytes.
"""

import struct
import socket
from typing import Optional

HEADER_SIZE = 4


def send_framed(sock: socket.socket, data: bytes) -> None:
    """Send data prefixed with a 4-byte length header."""
    sock.sendall(struct.pack('>I', len(data)) + data)


def recv_framed(sock: socket.socket) -> Optional[bytes]:
    """
    Receive one framed message.

    Returns:
        bytes: The message payload (may be b'' for a legitimate zero-length message).
        None:  The peer closed the connection before a complete message arrived.
    """
    header = _recv_exact(sock, HEADER_SIZE)
    if len(header) < HEADER_SIZE:
        return None
    length = struct.unpack('>I', header)[0]
    if length == 0:
        return b''
    payload = _recv_exact(sock, length)
    if len(payload) < length:
        return None
    return payload


def _recv_exact(sock: socket.socket, n: int) -> bytes:
    """Read exactly n bytes, looping over partial reads."""
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            break
        buf.extend(chunk)
    return bytes(buf)
