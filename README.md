<div align="center">

![FastSocket](https://github.com/giulicrenna/FastSocket/blob/main/assets/Design.png)

# FastSocket

**A fast, minimal Python library for building TCP and UDP servers and clients with optional encryption, chunking, and file transfer.**

[![PyPI version](https://img.shields.io/pypi/v/FastSocket.svg)](https://pypi.org/project/FastSocket/)
[![Python](https://img.shields.io/pypi/pyversions/FastSocket.svg)](https://pypi.org/project/FastSocket/)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![GitHub issues](https://img.shields.io/github/issues/giulicrenna/FastSocket)](https://github.com/giulicrenna/FastSocket/issues)
[![GitHub stars](https://img.shields.io/github/stars/giulicrenna/FastSocket)](https://github.com/giulicrenna/FastSocket/stargazers)

[Documentation](https://giulicrenna.github.io/FastSocket/) · [Quick Start](#quick-start) · [Examples](https://giulicrenna.github.io/FastSocket/examples/overview/) · [API Reference](https://giulicrenna.github.io/FastSocket/api/) · [Changelog](https://giulicrenna.github.io/FastSocket/changelog/)

</div>

---

## Overview

FastSocket is a Python library designed for rapid development and production use. It supports multi-connection handling out of the box and offers three security modes — plain, RSA, and a hybrid TLS-like mode (RSA key exchange + AES-256-GCM + HMAC) — without the complexity of managing raw sockets or TLS certificates.

## Features

| Feature | Description |
|---|---|
| **TCP & UDP** | Simple API for servers and clients over TCP or UDP |
| **Multi-connection** | Thread-based multi-client support with callback handlers |
| **RSA encryption** | Secure mode with RSA-4096 key exchange |
| **Hybrid TLS mode** | RSA-4096 handshake + AES-256-GCM messaging + HMAC authentication |
| **ChunkManager** | Split and reassemble large payloads reliably |
| **FileTransfer** | Send and receive files with SHA-256 integrity verification |
| **UDP broadcast** | Unicast and broadcast UDP support |
| **Examples & benchmarks** | Ready-to-run examples, benchmarks, and stress tests included |

## Installation

```bash
pip install FastSocket
```

**Requirements:** Python 3.8+, [pycryptodome](https://pycryptodome.readthedocs.io/) (installed automatically).

To install from source:

```bash
git clone https://github.com/giulicrenna/FastSocket.git
cd FastSocket
pip install -e .
```

## Quick Start

### TCP Server

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

### TCP Client

```python
from FastSocket import FastSocketClient, SocketConfig

def on_message(msg: str):
    print("Server:", msg)

client = FastSocketClient(SocketConfig(host="localhost", port=8080))
client.on_new_message(on_message)
client.start()
client.send_to_server("Hello FastSocket")
```

### Hybrid TLS Mode (RSA + AES-256-GCM + HMAC)

```python
from FastSocket import TLSSocketServer, TLSSocketClient, SocketConfig

# Server
server = TLSSocketServer(SocketConfig(host="localhost", port=9443), shared_secret="strong-secret")
server.on_new_message(lambda q: print(q.get()))
server.start()

# Client
client = TLSSocketClient(SocketConfig(host="localhost", port=9443), shared_secret="strong-secret")
client.on_new_message(lambda msg: print(msg))
client.start()
```

### UDP

```python
from FastSocket import FastSocketUDPServer, SocketConfig
import socket

config = SocketConfig(host="0.0.0.0", port=9000, type=socket.SOCK_DGRAM)
server = FastSocketUDPServer(config, enable_broadcast=True)
server.start()
```

## Available Classes

### Servers

| Class | Protocol | Encryption |
|---|---|---|
| `FastSocketServer` | TCP | None |
| `SecureFastSocketServer` | TCP | RSA-4096 |
| `TLSSocketServer` | TCP | RSA + AES-256-GCM + HMAC |
| `FastSocketUDPServer` | UDP | None |

### Clients

| Class | Protocol | Encryption |
|---|---|---|
| `FastSocketClient` | TCP | None |
| `SecureFastSocketClient` | TCP | RSA-4096 |
| `TLSSocketClient` | TCP | RSA + AES-256-GCM + HMAC |
| `FastSocketUDPClient` | UDP | None |

### Utilities

| Class | Description |
|---|---|
| `ChunkManager` | Split and reassemble large byte payloads |
| `FileTransfer` | File transfer with progress callbacks and hash verification |
| `SocketConfig` | Configuration object for host, port, and socket type |

## Documentation

Full documentation is available at **[giulicrenna.github.io/FastSocket](https://giulicrenna.github.io/FastSocket/)**, including:

- [Getting Started — Installation & Quickstart](https://giulicrenna.github.io/FastSocket/getting-started/installation/)
- [TCP Guide](https://giulicrenna.github.io/FastSocket/guide/tcp/)
- [UDP Guide](https://giulicrenna.github.io/FastSocket/guide/udp/)
- [Secure (RSA) Guide](https://giulicrenna.github.io/FastSocket/guide/secure/)
- [Hybrid TLS Guide](https://giulicrenna.github.io/FastSocket/guide/hybrid/)
- [ChunkManager Guide](https://giulicrenna.github.io/FastSocket/guide/chunks/)
- [File Transfer Guide](https://giulicrenna.github.io/FastSocket/guide/file-transfer/)
- [Error Handling](https://giulicrenna.github.io/FastSocket/guide/errors/)
- [API Reference](https://giulicrenna.github.io/FastSocket/api/)

## Roadmap

- [ ] Native TLS/SSL support (via Python `ssl` stdlib)
- [ ] Auto-reconnect for TCP clients
- [ ] `async`/`await` API (`asyncio`)
- [ ] Message compression (zlib / lz4)
- [ ] Exportable metrics (Prometheus / JSON)
- [ ] WebSocket support
- [ ] Channel multiplexing over a single connection
- [ ] Bindings for other languages (Go, Rust)

See the full [Roadmap](https://giulicrenna.github.io/FastSocket/roadmap/) for details.

## Contributing

Pull requests are welcome. Before submitting, make sure tests pass and code follows [PEP 8](https://peps.python.org/pep-0008/).

```bash
git clone https://github.com/giulicrenna/FastSocket.git
cd FastSocket
pip install -e ".[dev]"
pytest tests/
```

See [Contributing Guide](https://giulicrenna.github.io/FastSocket/contributing/) for full instructions.

## Contact

**Author:** Giuliano Crenna  
**Email:** [giulicrenna@gmail.com](mailto:giulicrenna@gmail.com)  
**GitHub:** [github.com/giulicrenna](https://github.com/giulicrenna)

## License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.  
See the [LICENSE](./LICENSE) file for details.
