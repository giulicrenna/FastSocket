"""Tests for ClientType — the per-connection server-side handler."""

import socket
import time
import pytest
from FastSocket.core.client_handler import ClientType
from FastSocket.utils.framing import send_framed


def test_receives_message_into_queue():
    server_sock, client_sock = socket.socketpair()
    handler = ClientType(server_sock, ("127.0.0.1", 9999))
    handler.start()

    send_framed(client_sock, b"hello world")
    msg, addr = handler.message_queue.get(timeout=2)

    assert msg == "hello world"
    assert addr == ("127.0.0.1", 9999)
    client_sock.close()
    handler.join(timeout=2)


def test_multiple_messages_queued_in_order():
    server_sock, client_sock = socket.socketpair()
    handler = ClientType(server_sock, ("127.0.0.1", 9999))
    handler.start()

    messages = ["alpha", "beta", "gamma"]
    for m in messages:
        send_framed(client_sock, m.encode())

    for expected in messages:
        msg, _ = handler.message_queue.get(timeout=2)
        assert msg == expected

    client_sock.close()
    handler.join(timeout=2)


def test_sets_connected_false_when_peer_closes():
    server_sock, client_sock = socket.socketpair()
    handler = ClientType(server_sock, ("127.0.0.1", 9999))
    handler.start()

    client_sock.close()
    handler.join(timeout=2)

    assert not handler.connected
    assert not handler.is_alive()


def test_thread_exits_on_disconnect():
    """Thread must not linger after the peer closes."""
    server_sock, client_sock = socket.socketpair()
    handler = ClientType(server_sock, ("127.0.0.1", 9999))
    handler.start()

    assert handler.is_alive()
    client_sock.close()
    handler.join(timeout=2)
    assert not handler.is_alive()
