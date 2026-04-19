# Guía TCP

FastSocket ofrece una API directa para levantar servidores y clientes TCP con múltiples conexiones.

## Servidor TCP

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

## Cliente TCP

```python
from FastSocket import FastSocketClient, SocketConfig

def on_message(msg: str):
    print("Server:", msg)

client = FastSocketClient(SocketConfig(host="localhost", port=8080))
client.on_new_message(on_message)
client.start()
client.send_to_server("hola")
```

## Recomendaciones

- Definí callbacks rápidos para no bloquear el loop de recepción.
- Validá el tipo de dato antes de enviar.
- Para payloads grandes, usar `ChunkManager`.
