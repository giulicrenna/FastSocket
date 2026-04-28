# Security

::: fastsocket.security.rsa_encryption

::: fastsocket.security.tls_encryption

## `derive_psk(raw_secret: bytes) -> bytes`

Derives a 32-byte cryptographic key from a raw pre-shared secret using PBKDF2-SHA256 (50 000 iterations, fixed application salt `fastsocket-psk-v2`).

Called automatically by `TLSSocketClient` and `TLSSocketServer` at construction time. You only need to call it directly if you are inspecting or testing the derived key.

```python
from fastsocket import derive_psk

key = derive_psk(b"my-passphrase")
assert len(key) == 32
```

> **Breaking change in 2.2.0:** the derived key is not interoperable with the raw PSK bytes used in ≤ 2.1.x. Both sides of a connection must run the same major version.
