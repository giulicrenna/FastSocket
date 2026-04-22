# Secure Guide (RSA)

FastSocket provides secure variants (`SecureFastSocketServer` and `SecureFastSocketClient`) that use RSA-4096 encryption for all messages.

## Secure Server

```python
from fastsocket import SecureFastSocketServer, SocketConfig, Queue

def handle_messages(messages: Queue):
    while not messages.empty():
        msg, addr = messages.get()
        print(f"{addr}: {msg}")
        server.send_msg_stream(f"Secure echo: {msg}")

server = SecureFastSocketServer(SocketConfig(host="localhost", port=9443))
server.on_new_message(handle_messages)
server.start()
```

## Secure Client

```python
from fastsocket import SecureFastSocketClient, SocketConfig

def on_message(msg: str):
    print(msg)

client = SecureFastSocketClient(SocketConfig(host="localhost", port=9443))
client.on_new_message(on_message)
client.start()
client.send_to_server("encrypted message")
```

## Notes

- RSA is not optimized for large or continuous messages.
- For high throughput or longer messages, consider [Hybrid TLS mode](hybrid.md) instead.
