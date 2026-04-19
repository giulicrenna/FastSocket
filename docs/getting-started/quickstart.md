# Quickstart

## 1) Basic TCP Server

```python
from FastSocket import FastSocketServer, SocketConfig, Queue

def on_messages(messages: Queue):
    while not messages.empty():
        msg, addr = messages.get()
        print(f"[{addr}] {msg}")
        server.send_msg_stream(f"Echo: {msg}")

config = SocketConfig(host="localhost", port=8080)
server = FastSocketServer(config)
server.on_new_message(on_messages)
server.start()
```

## 2) Basic TCP Client

```python
from FastSocket import FastSocketClient, SocketConfig
import time

def on_message(msg: str):
    print("Server:", msg)

config = SocketConfig(host="localhost", port=8080)
client = FastSocketClient(config)
client.on_new_message(on_message)
client.start()

while True:
    client.send_to_server("Hello FastSocket")
    time.sleep(1)
```

## 3) Next steps

- UDP: [UDP Guide](../guide/udp.md)
- RSA Security: [Secure Guide](../guide/secure.md)
- Large payloads: [Chunks Guide](../guide/chunks.md)
- File transfer: [File Transfer Guide](../guide/file-transfer.md)
- Hybrid TLS: [Hybrid Guide](../guide/hybrid.md)
