# Guía UDP

FastSocket incluye cliente y servidor UDP para casos donde priorizás baja latencia y simplicidad de datagramas.

## Servidor UDP

```python
from FastSocket import FastSocketUDPServer, SocketConfig, Queue
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

## Cliente UDP

```python
from FastSocket import FastSocketUDPClient, SocketConfig
import socket

def on_response(msg: str, addr: tuple):
    print("Respuesta:", msg, "desde", addr)

config = SocketConfig(host="localhost", port=9000, type=socket.SOCK_DGRAM)
client = FastSocketUDPClient(config)
client.on_new_message(on_response)
client.bind(("0.0.0.0", 9001))
client.start()
client.send_to_server("hola udp")
```

## Recomendaciones

- UDP no garantiza orden ni entrega — usarlo para datos donde la pérdida ocasional es aceptable (telemetría, juegos, discovery).
- Para mensajes críticos, preferir TCP o agregar ACKs manuales.
- Limitar el tamaño de datagrama a ≤1400 bytes para evitar fragmentación IP.
- El broadcast requiere `enable_broadcast=True` en el servidor.
