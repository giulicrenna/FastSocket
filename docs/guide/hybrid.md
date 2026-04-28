# Hybrid TLS Guide (RSA + AES-256-GCM + HMAC)

The **Hybrid TLS mode** combines:

- **RSA-4096** for session key exchange
- **AES-256-GCM** for payload encryption
- **HMAC** with a pre-shared key (PSK) for mutual authentication

This gives better throughput than pure RSA for continuous messaging, while authenticating both endpoints before any data is exchanged.

## Server

```python
from fastsocket import TLSSocketServer, SocketConfig

server = TLSSocketServer(
    SocketConfig(host="localhost", port=9555),
    shared_secret="my-very-strong-secret"
)
server.on_new_message(lambda q: print(q.get()))
server.start()
```

## Client

```python
from fastsocket import TLSSocketClient, SocketConfig

def on_message(msg: str):
    print("Server:", msg)

client = TLSSocketClient(
    SocketConfig(host="localhost", port=9555),
    shared_secret="my-very-strong-secret"
)
client.on_new_message(on_message)
client.start()

# Wait for the handshake to complete
import time
while not client.connected:
    time.sleep(0.05)

client.send_to_server("encrypted message")
```

## Handshake flow

1. Server sends its RSA public key.
2. Client generates a random `session_key`, encrypts it with RSA, and attaches an HMAC token derived from the PSK.
3. Server verifies the HMAC, decrypts the `session_key`, and responds with `OK` + its own HMAC.
4. From that point on, all messages are encrypted with AES-256-GCM.

## PSK derivation

Since 2.2.0, the raw `shared_secret` string is **never used directly** in cryptographic operations. Both sides call `derive_psk()` once at construction time, which runs PBKDF2-SHA256 (50 000 iterations) over the secret. This means:

- Short or low-entropy PSKs (e.g. `"dev"`) are meaningfully hardened.
- The ~50 ms derivation cost is paid once, not per handshake.
- **Client and server must both run ≥ 2.2.0** — the derived keys are incompatible with the raw bytes used in 2.1.x.

You can call `derive_psk` yourself if you need to inspect the derived key:

```python
from fastsocket import derive_psk
key = derive_psk(b"my-secret")  # 32-byte key
```

## Auto-reconnect

`TLSSocketClient` supports automatic reconnection including a full new handshake:

```python
client = TLSSocketClient(
    SocketConfig(host="localhost", port=9555),
    shared_secret="my-very-strong-secret",
    auto_reconnect=True,
    reconnect_delay=1.0,   # seconds between attempts
)
client.on_disconnect(lambda: print("disconnected, retrying…"))
client.on_new_message(handle_message)  # required to detect disconnects
client.start()
```

> **Note:** at least one `on_new_message` handler must be registered for disconnect detection to work. Without a handler no recv loop runs, so the client cannot observe that the connection dropped.

When the connection drops, only one internal thread handles the reconnect (via `_reconnect_lock`). After a successful re-handshake, all registered handlers are restarted automatically.

## Best practices

- Use a long, random PSK (minimum 32 characters). Short PSKs are hardened by PBKDF2 but a strong secret is still preferred.
- Rotate secrets periodically in production environments.
- Never hardcode secrets in public code — use environment variables.
- Always check `client.connected` before calling `send_to_server`.
- Register `on_new_message` if you need `on_disconnect` or `auto_reconnect` to work.
