# Chunks Guide

`ChunkManager` lets you split and reassemble large payloads for reliable transfers.

## Basic usage

```python
from fastsocket import ChunkManager

manager = ChunkManager(chunk_size=4096, use_headers=True)
data = b"A" * 50000

chunks = manager.split_data(data)
rebuilt = manager.reassemble_chunks(chunks)
assert rebuilt == data
```

## Sending and receiving over a socket

```python
# Send
bytes_sent = manager.send_chunked(sock, data)

# Receive
received = manager.receive_chunked(sock)
```

## When to use it

- Files or large binary blobs
- Messages that exceed practical buffer limits
- Cases where you need to estimate packet count and overhead
