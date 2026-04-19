# FastSocket 🚀

Documentación oficial de **FastSocket**, una librería Python para construir servidores y clientes **TCP/UDP**, con soporte **secure (RSA)**, transferencias por **chunks**, **file transfer** y modo **hybrid**.

> Pensado para prototipos rápidos y casos reales con múltiples conexiones.

## Features principales

- ⚡ API simple para cliente/servidor TCP
- 📡 Soporte UDP (unicast + broadcast)
- 🔐 Comunicación segura con RSA
- 🧩 Chunking automático para payloads grandes
- 📁 Transferencia de archivos con hash/integridad
- 🧪 Suite de ejemplos, benchmarks y stress tests

## Instalación rápida

```bash
pip install FastSocket
```

## Quickstart

```python
from FastSocket import FastSocketServer, SocketConfig, Queue

def handle_messages(messages: Queue):
    while not messages.empty():
        msg, addr = messages.get()
        print(f"[{addr}] {msg}")

config = SocketConfig(host="localhost", port=8080)
server = FastSocketServer(config)
server.on_new_message(handle_messages)
server.start()
```

Seguí por:

1. **Getting Started** para instalación y primer proyecto.
2. **Guía** para TCP, UDP, secure, chunks y file transfer.
3. **Ejemplos** para casos completos listos para correr.
4. **API Reference** para detalle de clases y funciones.