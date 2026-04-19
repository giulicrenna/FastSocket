# Changelog

## [2.0.0]

- Complete rewrite with modular package structure.
- Hybrid TLS mode (RSA-4096 + AES-256-GCM + HMAC).
- `ChunkManager` for large payload splitting and reassembly.
- `FileTransfer` with SHA-256 integrity verification.
- UDP support with broadcast.
- Example suite: echo, chat, secure chat, chunks, file transfer, UDP, benchmarks, stress test.
- MkDocs with Material theme for documentation.

## [1.x]

- Initial TCP/UDP API with basic RSA support.
- Multi-client server with threads.
