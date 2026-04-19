# Guía Chunks

`ChunkManager` permite dividir y recomponer payloads grandes para transferencias robustas.

## Uso básico

```python
from FastSocket import ChunkManager

manager = ChunkManager(chunk_size=4096, use_headers=True)
data = b"A" * 50000

chunks = manager.split_data(data)
rebuilt = manager.reassemble_chunks(chunks)
assert rebuilt == data
```

## Envío/recepción sobre socket

```python
# enviar
bytes_sent = manager.send_chunked(sock, data)

# recibir
received = manager.receive_chunked(sock)
```

## Cuándo usarlo

- Archivos o blobs grandes
- Mensajes que exceden límites prácticos de buffer
- Casos donde querés estimar overhead y cantidad de paquetes
