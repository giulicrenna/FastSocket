"""Integration tests for hybrid RSA+AES encryption and PSK authentication."""

import socket
import time
import threading
import pytest
from fastsocket.core.config import SocketConfig
from fastsocket.server.tls_server import TLSSocketServer
from fastsocket.client.tls_client import TLSSocketClient
from fastsocket.security.tls_encryption import (
    aes_encrypt, aes_decrypt, hmac_sign, hmac_verify, generate_session_key,
)


SECRET = "test-secret-key"
WRONG_SECRET = "wrong-secret"


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def start_server(port: int, secret: str = SECRET, handler=None) -> TLSSocketServer:
    config = SocketConfig(host="127.0.0.1", port=port)
    server = TLSSocketServer(config, shared_secret=secret)
    if handler:
        server.on_new_message(handler)
    server.start()
    time.sleep(0.5)   # RSA key generation needs a moment
    return server


# ── crypto unit tests ─────────────────────────────────────────────────────────

def test_aes_encrypt_decrypt_roundtrip():
    key = generate_session_key()
    plaintext = b"hello hybrid world"
    assert aes_decrypt(key, aes_encrypt(key, plaintext)) == plaintext


def test_aes_decrypt_detects_tampered_ciphertext():
    key = generate_session_key()
    blob = bytearray(aes_encrypt(key, b"secret"))
    blob[-1] ^= 0xFF   # flip a bit in the ciphertext
    with pytest.raises(Exception):
        aes_decrypt(key, bytes(blob))


def test_aes_decrypt_detects_tampered_tag():
    key = generate_session_key()
    blob = bytearray(aes_encrypt(key, b"secret"))
    blob[16] ^= 0xFF   # flip a bit in the tag
    with pytest.raises(Exception):
        aes_decrypt(key, bytes(blob))


def test_hmac_verify_correct():
    key = b"my-secret"
    data = b"session-key-bytes"
    sig = hmac_sign(key, data)
    assert hmac_verify(key, data, sig)


def test_hmac_verify_wrong_key():
    sig = hmac_sign(b"correct", b"data")
    assert not hmac_verify(b"wrong", b"data", sig)


def test_hmac_verify_tampered_data():
    sig = hmac_sign(b"key", b"data")
    assert not hmac_verify(b"key", b"tampered", sig)


# ── integration tests ─────────────────────────────────────────────────────────

def test_client_connects_and_sends_message():
    port = free_port()
    received = []
    event = threading.Event()

    def handler(q):
        while not q.empty():
            msg, _ = q.get()
            received.append(msg)
            event.set()

    start_server(port, handler=handler)

    config = SocketConfig(host="127.0.0.1", port=port)
    client = TLSSocketClient(config, shared_secret=SECRET)
    client.start()

    # Wait for handshake
    deadline = time.time() + 20
    while not client.connected and time.time() < deadline:
        time.sleep(0.1)

    assert client.connected, "Handshake should succeed with correct PSK"

    client.send_to_server("hello from hybrid client")
    event.wait(timeout=3)

    assert "hello from hybrid client" in received


def test_wrong_psk_is_rejected():
    port = free_port()
    start_server(port, secret=SECRET)

    config = SocketConfig(host="127.0.0.1", port=port)
    client = TLSSocketClient(config, shared_secret=WRONG_SECRET)
    client.start()

    # Handshake should fail — give it time to try
    time.sleep(3)
    assert not client.connected, "Client with wrong PSK must not connect"


def test_server_sends_message_to_client():
    port = free_port()
    server = start_server(port)

    received = []
    config = SocketConfig(host="127.0.0.1", port=port)
    client = TLSSocketClient(config, shared_secret=SECRET)
    client.on_new_message(received.append)
    client.start()

    deadline = time.time() + 20
    while not client.connected and time.time() < deadline:
        time.sleep(0.1)

    # Need at least one message from client so it appears in _client_buffer
    client.send_to_server("ping")
    time.sleep(0.3)

    server.send_msg_stream("broadcast from server")
    time.sleep(0.5)

    assert "broadcast from server" in received


def test_multiple_messages_in_sequence():
    port = free_port()
    received = []
    event = threading.Event()

    def handler(q):
        while not q.empty():
            msg, _ = q.get()
            received.append(msg)
            if len(received) >= 3:
                event.set()

    start_server(port, handler=handler)

    config = SocketConfig(host="127.0.0.1", port=port)
    client = TLSSocketClient(config, shared_secret=SECRET)
    client.start()

    deadline = time.time() + 20
    while not client.connected and time.time() < deadline:
        time.sleep(0.1)

    for msg in ["one", "two", "three"]:
        client.send_to_server(msg)

    event.wait(timeout=3)
    assert received == ["one", "two", "three"]
