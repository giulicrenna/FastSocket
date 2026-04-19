# Manejo de errores

FastSocket expone excepciones específicas para casos comunes.

## Excepciones destacadas

- `FastSocketException`
- `InvalidMessageType`
- `NetworkException`
- `BadEncryptionInput`
- `ConnectionClosedException`
- `FileTransferException`
- `IntegrityException`
- `ChunkException`
- `TimeoutException`

## Patrón recomendado

```python
from FastSocket import FastSocketClient, SocketConfig
from FastSocket import NetworkException, TimeoutException

try:
    client = FastSocketClient(SocketConfig(host="localhost", port=8080))
    client.start()
except (NetworkException, TimeoutException) as e:
    print(f"Error de red: {e}")
except Exception as e:
    print(f"Error inesperado: {e}")
```
