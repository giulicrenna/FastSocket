# Changelog

## [2.0.0]

- Reescritura completa con estructura de paquete modular.
- Soporte TLS Hybrid (RSA-4096 + AES-256-GCM + HMAC).
- `ChunkManager` para payloads grandes.
- `FileTransfer` con verificación de integridad por hash.
- Soporte UDP con broadcast.
- Suite de ejemplos: echo, chat, secure chat, chunks, file transfer, UDP, benchmarks, stress test.
- `mkdocs` con tema Material para documentación.

## [1.x]

- API inicial TCP/UDP con soporte RSA básico.
- Servidor multi-cliente con threads.
