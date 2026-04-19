# TCP Guide

FastSocket provides a straightforward API for running TCP servers and clients with multi-connection support.

## TCP Server

```python
from FastSocket import FastSocketServer, SocketConfig, Queue

def handle_messages(messages: Queue):
    while not messages.empty():
        msg, addr = messages.get()
        print(f"{addr} -> {msg}")
        server.send_msg_stream(f"Echo: {msg}")

config = SocketConfig(host="localhost", port=8080)
server = FastSocketServer(config)
server.on_new_message(handle_messages)
server.start()
```

## TCP Client

```python
from FastSocket import FastSocketClient, SocketConfig

def on_message(msg: str):
    print("Server:", msg)

client = FastSocketClient(SocketConfig(host="localhost", port=8080))
client.on_new_message(on_message)
client.start()
client.send_to_server("hello")
```

## Tips

- Keep callbacks fast to avoid blocking the receive loop.
- Validate data types before sending.
- For large payloads, use [`ChunkManager`](chunks.md).
