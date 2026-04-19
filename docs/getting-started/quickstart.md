# Quickstart

## 1) Servidor TCP básico

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

## 2) Cliente TCP básico

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
    client.send_to_server("Hola FastSocket")
    time.sleep(1)
```

## 3) Siguiente paso

- UDP: [Guía UDP](../guide/udp.md)
- Seguridad RSA: [Guía Secure](../guide/secure.md)
- Payloads grandes: [Guía Chunks](../guide/chunks.md)
- Transferencia de archivos: [Guía File Transfer](../guide/file-transfer.md)
