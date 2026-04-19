![](https://github.com/giulicrenna/FastSocket/blob/main/assets/Design.png)

# FastSocket

FastSocket es una librería Python para construir servidores y clientes TCP y UDP con manejo de múltiples conexiones, cifrado opcional, transferencia por chunks y soporte de archivos. La API está pensada para ser mínima y rápida de usar.

## Features

- API simple para servidores y clientes TCP y UDP
- Comunicación segura con cifrado RSA
- Modo TLS Hybrid: intercambio de clave RSA-4096 + cifrado AES-256-GCM + autenticación HMAC
- ChunkManager para dividir y reensamblar payloads grandes
- FileTransfer con verificación de integridad (SHA-256)
- Soporte UDP unicast y broadcast
- Ejemplos, benchmarks y stress tests incluidos

## Roadmap

* [ ] Implementación con asyncio
* [ ] Gestión automática de chunks en el protocolo base
* [ ] Reconexión automática en clientes
* [ ] Keep-alive configurable
* [ ] Políticas de rate limiting
* [ ] Serialización de mensajes (JSON, MessagePack)
* [ ] Compresión de payloads (zlib / lz4)

## Instalación

```bash
pip install FastSocket
```

## Quickstart

**Servidor TCP:**

```python
from FastSocket import FastSocketServer, SocketConfig, Queue

def handle_messages(messages: Queue):
    while not messages.empty():
        msg, addr = messages.get()
        print(f"[{addr}] {msg}")
        server.send_msg_stream(f"Echo: {msg}")

config = SocketConfig(host="localhost", port=8080)
server = FastSocketServer(config)
server.on_new_message(handle_messages)
server.start()
```

**Cliente TCP:**

```python
from FastSocket import FastSocketClient, SocketConfig

def on_message(msg: str):
    print("Servidor:", msg)

client = FastSocketClient(SocketConfig(host="localhost", port=8080))
client.on_new_message(on_message)
client.start()
client.send_to_server("hola")
```

## Modo TLS Hybrid

```python
from FastSocket import TLSSocketServer, TLSSocketClient, SocketConfig

# Servidor
server = TLSSocketServer(SocketConfig(host="localhost", port=9443), shared_secret="secreto-fuerte")
server.on_new_message(lambda q: print(q.get()))
server.start()

# Cliente
client = TLSSocketClient(SocketConfig(host="localhost", port=9443), shared_secret="secreto-fuerte")
client.on_new_message(lambda msg: print(msg))
client.start()
```

## UDP

```python
from FastSocket import FastSocketUDPServer, SocketConfig
import socket

config = SocketConfig(host="0.0.0.0", port=9000, type=socket.SOCK_DGRAM)
server = FastSocketUDPServer(config, enable_broadcast=True)
server.start()
```

## Documentación

Documentación completa en [giulicrenna.github.io/FastSocket](https://giulicrenna.github.io/FastSocket/)

## Contribuir

Los pull requests son bienvenidos. Antes de enviar, asegurate de que los tests pasen y de seguir el estilo PEP 8.

## Contacto

**Autor:** Giuliano Crenna  
**Email:** giulicrenna@gmail.com

## Licencia

Este proyecto está licenciado bajo GNU Affero General Public License v3.0 (AGPL-3.0). Ver el archivo LICENSE para más detalles.
