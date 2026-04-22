# Error Handling

FastSocket exposes specific exception classes for common failure scenarios.

## Available exceptions

| Exception | Description |
|---|---|
| `FastSocketException` | Base exception for all FastSocket errors |
| `InvalidMessageType` | Message type not supported |
| `NetworkException` | Network-level failure |
| `BadEncryptionInput` | Invalid encryption input |
| `ConnectionClosedException` | Remote connection closed unexpectedly |
| `FileTransferException` | Error during file transfer |
| `IntegrityException` | Hash or integrity check failed |
| `ChunkException` | Error during chunk splitting or reassembly |
| `TimeoutException` | Operation timed out |

## Recommended pattern

```python
from fastsocket import FastSocketClient, SocketConfig
from fastsocket import NetworkException, TimeoutException

try:
    client = FastSocketClient(SocketConfig(host="localhost", port=8080))
    client.start()
except (NetworkException, TimeoutException) as e:
    print(f"Network error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```
