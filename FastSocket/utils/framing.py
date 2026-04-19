"""
Length-prefix framing for TCP streams.

Wraps messages as: [4-byte big-endian length][payload]
This ensures each recv() call reconstructs exactly one message,
regardless of how TCP splits or merges the underlying bytes.
"""

import struct
import socket

HEADER_SIZE = 4


def send_framed(sock: socket.socket, data: bytes) -> None:
    """Send data prefixed with a 4-byte length header."""
    sock.sendall(struct.pack('>I', len(data)) + data)


def recv_framed(sock: socket.socket) -> bytes:
    """
    Receive one framed message. Returns b'' if the connection is closed.
    Blocks until the full message arrives.
    """
    header = _recv_exact(sock, HEADER_SIZE)
    if len(header) < HEADER_SIZE:
        return b''
    length = struct.unpack('>I', header)[0]
    return _recv_exact(sock, length)


def _recv_exact(sock: socket.socket, n: int) -> bytes:
    """Read exactly n bytes, looping over partial reads."""
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            break
        buf += chunk
    return bytes(buf)
