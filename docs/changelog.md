# Changelog

## [2.2.0] — 2026-04-28

### Breaking changes

- **PSK derivation in Hybrid TLS** — the pre-shared key is now passed through PBKDF2-SHA256 (50 000 iterations, fixed application salt) before it is used in HMAC operations. Servers and clients must both run ≥ 2.2.0; a 2.1.x client will be rejected by a 2.2.0 server and vice-versa. The derivation happens once at construction time so handshake latency is unaffected.

### Bug fixes

- **TLS auto-reconnect with multiple handlers** — when more than one `on_new_message` callback was registered, all recv threads detected the disconnect simultaneously and raced to create a new socket, clobbering each other. A `_reconnect_lock` now ensures only one thread handles the reconnect; on success it restarts recv loops for **all** registered handlers.
- **`TLSSocketServer.stop()` closes active connections** — previously `stop()` only closed the listening socket, leaving already-connected `TLSClientHandler` threads alive indefinitely. Now it also closes every active client socket before shutting down.
- **`TLSSocketServer._listen_for_new_clients` exits cleanly on stop** — the `accept()` call raised an unhandled `OSError` when the socket was closed by `stop()`. The exception is now caught when `_running` is `False`.

### Security

- **PSK hardening** (`derive_psk`) — see breaking changes above. Weak or short PSKs (e.g. `"dev"`) are now stretched by PBKDF2 before use, reducing the impact of low-entropy secrets.

### Improvements

- **Thread-safe logger** — `fastsocket.utils.logger` now uses Python's stdlib `logging` module instead of bare `print()`. Concurrent log calls from multiple threads no longer interleave. New helpers: `Logger.set_level(level)` and `Logger.add_file_handler(path)`.
- **UDP concurrent-send safety** — `FastSocketUDPServer.send_to()` now holds `_socket_lock` around every `sendto()` call, preventing concurrent broadcasts from racing on the same socket.
- **RSA validation consolidated** — `SecureFastSocketClient.send_to_server()` delegates to `RSAEncryption.encrypt()` instead of duplicating the size-check inline. `BadEncryptionInput` is raised from a single, tested code path.

### Housekeeping

- Removed legacy files: `fastsocket/fastsocket.py`, `fastsocket/_expt.py`, `fastsocket/_types.py`, `fastsocket/logger.py`. None were imported by the package; they existed only as historical artefacts.
- `derive_psk` is now a public export from both `fastsocket.security.tls_encryption` and the top-level `fastsocket` namespace.

### Tests

- `test_psk_derivation_is_symmetric` — verifies `derive_psk` is deterministic and collision-free.
- `test_client_reconnects_after_server_drop` — end-to-end test: connect → server drops → client detects → reconnects → sends message.
- `test_multiple_concurrent_tls_clients` — five clients connect, authenticate, and exchange messages simultaneously.

---

## [2.1.1] — 2026-04-22

- Renamed Python import from `FastSocket` to `fastsocket` (lowercase) to match the package directory.
- Renamed PyPI package from `FastSocket` to `fastsocket`.
- All docs, examples, and tests updated accordingly.

## [2.1.0] — 2026-04-22

### Bug fixes

- **Busy-loop eliminated** — `_run_new_message_handler` in all servers (`FastSocketServer`, `SecureFastSocketServer`, `TLSSocketServer`, `FastSocketUDPServer`) now checks `message_queue.empty()` before dispatching and sleeps 5 ms when no messages are pending, instead of spinning a CPU core at 100%.
- **UDP client crash fixed** — `FastSocketUDPClient.run` no longer calls `.__self__` on handler functions, which caused an `AttributeError` crash when using plain functions (not bound methods).
- **`recv_framed` return contract clarified** — now returns `None` when the peer closes the connection and `b''` for a legitimate zero-length message. Previously both cases returned `b''`, making them indistinguishable. All internal callers updated to `if data is None:`.
- **Race condition in UDP server fixed** — `_receive_datagrams` and `_cleanup_inactive_clients` now share a `threading.Lock` around all accesses to `_client_buffer`, preventing concurrent structural modification from different threads.

### New features

- **`stop()` / `close()` API** — all servers (`FastSocketServer`, `SecureFastSocketServer`, `TLSSocketServer`, `FastSocketUDPServer`) and TCP clients (`FastSocketClient`, `TLSSocketClient`, `SecureFastSocketClient`, `FastSocketUDPClient`) now expose a `stop()` / `close()` method for graceful shutdown.
- **RSA plaintext size validation** — `RSAEncryption.encrypt()` and `SecureFastSocketClient.send_to_server()` now raise `BadEncryptionInput` with a descriptive message when the plaintext exceeds the RSA key's maximum size (`key_size_bytes - 42` for OAEP/SHA-1), instead of propagating an undocumented `ValueError` from pycryptodome.
- **`on_disconnect` callback** — `FastSocketClient` and `TLSSocketClient` now accept `on_disconnect(func)` to register callbacks invoked when the server closes the connection or the network fails.
- **Auto-reconnect** — `FastSocketClient(config, auto_reconnect=True, reconnect_delay=1.0)` and `TLSSocketClient(config, shared_secret, auto_reconnect=True, reconnect_delay=1.0)` automatically re-establish the connection (including full TLS handshake) after a disconnect.

### Performance

- **`FileTransfer` metadata no longer read byte-by-byte** — sender uses `send_framed` and receiver uses `recv_framed` for metadata, replacing the O(n) syscall loop that could also block indefinitely on malformed input.
- **`ChunkManager._recv_exactly` is now O(n)** — replaced `bytes` concatenation (`data += packet`) with `bytearray` + `.extend()`, eliminating the O(n²) memory copy overhead for large transfers.

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
