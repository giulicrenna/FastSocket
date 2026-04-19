# Guía Secure (RSA)

FastSocket incluye variantes seguras (`SecureFastSocketServer` y `SecureFastSocketClient`) que usan RSA.

## Servidor seguro

```python
from FastSocket import SecureFastSocketServer, SocketConfig, Queue

def handle_messages(messages: Queue):
    while not messages.empty():
        msg, addr = messages.get()
        print(f"{addr}: {msg}")
        server.send_msg_stream(f"Secure echo: {msg}")

server = SecureFastSocketServer(SocketConfig(host="localhost", port=9443))
server.on_new_message(handle_messages)
server.start()
```

## Cliente seguro

```python
from FastSocket import SecureFastSocketClient, SocketConfig

def on_message(msg: str):
    print(msg)

client = SecureFastSocketClient(SocketConfig(host="localhost", port=9443))
client.on_new_message(on_message)
client.start()
client.send_to_server("mensaje cifrado")
```

## Notas

- RSA no está optimizado para mensajes muy grandes.
- Para cargas altas y mensajes más largos, considerar modo Hybrid.
