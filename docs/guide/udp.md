# UDP Guide

FastSocket includes UDP client and server support for low-latency, datagram-based communication.

## UDP Server

```python
from fastsocket import FastSocketUDPServer, SocketConfig, Queue
import socket

def handle_messages(messages: Queue):
    while not messages.empty():
        msg, addr = messages.get()
        print(f"{addr} -> {msg}")
        server.send_to(addr, f"Echo: {msg}")

config = SocketConfig(host="0.0.0.0", port=9000, type=socket.SOCK_DGRAM)
server = FastSocketUDPServer(config, enable_broadcast=True)
server.on_new_message(handle_messages)
server.start()
```

## UDP Client

```python
from fastsocket import FastSocketUDPClient, SocketConfig
import socket

def on_response(msg: str, addr: tuple):
    print("Response:", msg, "from", addr)

config = SocketConfig(host="localhost", port=9000, type=socket.SOCK_DGRAM)
client = FastSocketUDPClient(config)
client.on_new_message(on_response)
client.bind(("0.0.0.0", 9001))
client.start()
client.send_to_server("hello udp")
```

## Tips

- UDP does not guarantee delivery or ordering — use it for data where occasional loss is acceptable (telemetry, games, discovery).
- For critical messages, prefer TCP or implement manual ACKs.
- Keep datagram size to ≤1400 bytes to avoid IP fragmentation.
- Broadcast requires `enable_broadcast=True` on the server.
- `send_to()` and `broadcast()` can be called safely from multiple threads — since 2.2.0, a `_socket_lock` serialises concurrent `sendto()` calls on the shared socket.
