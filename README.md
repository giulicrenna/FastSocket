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
| **Auto-reconnect** | Clients reconnect automatically on connection loss |
| **Disconnect callbacks** | `on_disconnect` hook for connection loss events |
| **Graceful shutdown** | `stop()` method on all servers and clients |
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

# Graceful shutdown
# server.stop()
```

### TCP Client

```python
from FastSocket import FastSocketClient, SocketConfig

def on_message(msg: str):
    print("Server:", msg)

# Auto-reconnect and disconnect callback (new in 2.1.0)
client = FastSocketClient(
    SocketConfig(host="localhost", port=8080),
    auto_reconnect=True,
    reconnect_delay=2.0,
)
client.on_new_message(on_message)
client.on_disconnect(lambda: print("Connection lost, reconnecting…"))
client.start()
client.send_to_server("Hello FastSocket")

# Graceful shutdown
# client.stop()
```

### Hybrid TLS Mode (RSA + AES-256-GCM + HMAC)

```python
from FastSocket import TLSSocketServer, TLSSocketClient, SocketConfig

# Server
server = TLSSocketServer(SocketConfig(host="localhost", port=9443), shared_secret="strong-secret")
server.on_new_message(lambda q: print(q.get()))
server.start()

# Client (auto_reconnect supported)
client = TLSSocketClient(
    SocketConfig(host="localhost", port=9443),
    shared_secret="strong-secret",
    auto_reconnect=True,
)
client.on_new_message(lambda msg: print(msg))
client.on_disconnect(lambda: print("TLS connection lost"))
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

All servers expose `stop()` for graceful shutdown.

### Clients

| Class | Protocol | Encryption |
|---|---|---|
| `FastSocketClient` | TCP | None |
| `SecureFastSocketClient` | TCP | RSA-4096 |
| `TLSSocketClient` | TCP | RSA + AES-256-GCM + HMAC |
| `FastSocketUDPClient` | UDP | None |

`FastSocketClient` and `TLSSocketClient` support `on_disconnect` and `auto_reconnect`. All clients expose `stop()` / `close()`.

### Utilities

| Class | Description |
|---|---|
| `ChunkManager` | Split and reassemble large byte payloads |
| `FileTransfer` | File transfer with progress callbacks and hash verification |
| `SocketConfig` | Configuration object for host, port, and socket type |

## What's new in 2.1.0

- **Busy-loop fix** — message handler threads now sleep when queues are idle instead of spinning at 100% CPU.
- **`stop()` API** — every server and client can now be shut down cleanly.
- **`on_disconnect` + auto-reconnect** — TCP clients notify user code on disconnect and can reconnect automatically (including full TLS handshake re-negotiation).
- **Race condition fix** — UDP server dict access is now protected by a lock.
- **RSA size guard** — oversized messages raise `BadEncryptionInput` instead of a cryptic pycryptodome error.
- **Performance** — `FileTransfer` uses framing for metadata (no more byte-by-byte reads); `ChunkManager` uses `bytearray` to avoid O(n²) copies.

See the full [Changelog](https://giulicrenna.github.io/FastSocket/changelog/) for details.

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
