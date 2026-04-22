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
2. Client generates a random `session_key`, encrypts it with RSA, and attaches an HMAC token of the PSK.
3. Server verifies the HMAC, decrypts the `session_key`, and responds with `OK` + its own HMAC.
4. From that point on, all messages are encrypted with AES-256-GCM.

## Best practices

- Use a long, random PSK (minimum 32 characters).
- Rotate secrets periodically in production environments.
- Never hardcode secrets in public code — use environment variables.
- Always check `client.connected` before calling `send_to_server`.
