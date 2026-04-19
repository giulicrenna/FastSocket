"""Tests for length-prefix framing utilities."""

import socket
import pytest
from FastSocket.utils.framing import send_framed, recv_framed


def socketpair():
    """Return a connected (writer, reader) socket pair."""
    return socket.socketpair()


def test_single_message():
    a, b = socketpair()
    send_framed(a, b"hello")
    assert recv_framed(b) == b"hello"
    a.close(); b.close()


def test_multiple_messages_arrive_in_order():
    a, b = socketpair()
    messages = [b"first", b"second", b"third message here"]
    for msg in messages:
        send_framed(a, msg)
    for expected in messages:
        assert recv_framed(b) == expected
    a.close(); b.close()


def test_large_message():
    a, b = socketpair()
    data = b"x" * 200_000
    send_framed(a, data)
    assert recv_framed(b) == data
    a.close(); b.close()


def test_empty_payload():
    a, b = socketpair()
    send_framed(a, b"")
    assert recv_framed(b) == b""
    a.close(); b.close()


def test_closed_peer_returns_empty_bytes():
    a, b = socketpair()
    a.close()
    assert recv_framed(b) == b""
    b.close()


def test_unicode_encoded_message():
    a, b = socketpair()
    text = "hola mundo 🌎"
    send_framed(a, text.encode("utf-8"))
    assert recv_framed(b).decode("utf-8") == text
    a.close(); b.close()
