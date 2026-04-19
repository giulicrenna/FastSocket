# FastSocket

Official documentation for **FastSocket**, a Python library for building **TCP/UDP** servers and clients with support for **secure (RSA)** communication, **chunked transfers**, **file transfer**, and a **hybrid TLS** mode.

> Designed for rapid prototyping and production use with multi-connection handling.

## Features

- **Simple API** for TCP and UDP clients and servers
- **UDP support** — unicast and broadcast
- **RSA encryption** — secure mode with RSA-4096 key pairs
- **Hybrid TLS mode** — RSA handshake + AES-256-GCM + HMAC authentication
- **ChunkManager** — automatic splitting and reassembly of large payloads
- **FileTransfer** — file transfers with progress callbacks and SHA-256 integrity checks
- **Examples & benchmarks** — ready-to-run suite included

## Quick Install

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

## Where to go next

1. [**Getting Started**](getting-started/installation.md) — installation and first project.
2. [**Guide**](guide/tcp.md) — TCP, UDP, secure, chunks, and file transfer.
3. [**Examples**](examples/overview.md) — complete, runnable examples.
4. [**API Reference**](api/index.md) — classes and functions in detail.
