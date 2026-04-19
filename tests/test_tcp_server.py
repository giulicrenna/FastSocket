"""Integration tests for FastSocketServer and FastSocketClient."""

import socket
import time
import threading
import pytest
from FastSocket.core.config import SocketConfig
from FastSocket.server.tcp_server import FastSocketServer
from FastSocket.client.tcp_client import FastSocketClient
from FastSocket.utils.framing import send_framed, recv_framed


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


# ---------- helpers ----------

def start_server(port: int, handler=None) -> FastSocketServer:
    config = SocketConfig(host="127.0.0.1", port=port)
    server = FastSocketServer(config)
    if handler:
        server.on_new_message(handler)
    server.start()
    time.sleep(0.15)  # allow bind + listen
    return server


# ---------- tests ----------

def test_server_receives_message_from_raw_client():
    port = free_port()
    received = []

    def handler(q):
        while not q.empty():
            msg, _ = q.get()
            received.append(msg)

    start_server(port, handler)

    sock = socket.create_connection(("127.0.0.1", port))
    send_framed(sock, b"integration test")
    time.sleep(0.2)
    sock.close()

    assert "integration test" in received


def test_server_broadcast_reaches_all_clients():
    port = free_port()
    server = start_server(port)

    clients = []
    for _ in range(3):
        s = socket.create_connection(("127.0.0.1", port))
        send_framed(s, b"hello")   # register with server
        clients.append(s)

    time.sleep(0.2)
    server.send_msg_stream("broadcast!")

    for s in clients:
        data = recv_framed(s)
        assert data == b"broadcast!"
        s.close()


def test_send_msg_stream_rejects_invalid_type():
    port = free_port()
    server = start_server(port)

    from FastSocket.utils.exceptions import InvalidMessageType
    with pytest.raises(InvalidMessageType):
        server.send_msg_stream(12345)


def test_client_sends_and_server_receives():
    port = free_port()
    received = []
    event = threading.Event()

    def handler(q):
        while not q.empty():
            msg, _ = q.get()
            received.append(msg)
            event.set()

    start_server(port, handler)

    config = SocketConfig(host="127.0.0.1", port=port)
    client = FastSocketClient(config)
    client.start()
    time.sleep(0.1)

    client.send_to_server("from client")
    event.wait(timeout=2)

    assert "from client" in received


def test_disconnected_clients_cleaned_from_buffer():
    port = free_port()
    server = start_server(port)

    sock = socket.create_connection(("127.0.0.1", port))
    send_framed(sock, b"hi")
    time.sleep(0.1)
    sock.close()

    # Wait for the cleanup cycle (server timeout is 5 s)
    time.sleep(6)

    with server._client_lock:
        alive = [c for c in server._client_buffer if not c.connected]
    assert alive == [], "Disconnected clients should have been removed"
