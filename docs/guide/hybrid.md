# Guía TLS Hybrid (RSA + AES-256-GCM + HMAC)

El modo **TLS Hybrid** combina:

- Intercambio de clave de sesión con **RSA-4096**
- Cifrado de payload con **AES-256-GCM**
- Autenticación mutua con **HMAC** usando un secreto compartido (PSK)

Esto da mejor rendimiento que RSA puro para mensajes continuos y autentica ambos extremos antes de enviar datos.

## Servidor

```python
from FastSocket import TLSSocketServer, SocketConfig

server = TLSSocketServer(
    SocketConfig(host="localhost", port=9555),
    shared_secret="mi-secreto-super-fuerte"
)
server.on_new_message(lambda q: print(q.get()))
server.start()
```

## Cliente

```python
from FastSocket import TLSSocketClient, SocketConfig

def on_message(msg: str):
    print("Server:", msg)

client = TLSSocketClient(
    SocketConfig(host="localhost", port=9555),
    shared_secret="mi-secreto-super-fuerte"
)
client.on_new_message(on_message)
client.start()

# Esperar a que el handshake termine
import time
while not client.connected:
    time.sleep(0.05)

client.send_to_server("mensaje cifrado")
```

## Flujo del handshake

1. Servidor envía su clave pública RSA.
2. Cliente genera `session_key` aleatoria, la encripta con RSA y adjunta un token HMAC del PSK.
3. Servidor verifica el HMAC, desencripta la `session_key` y responde con `OK` + su propio HMAC.
4. A partir de ahí, todos los mensajes viajan cifrados con AES-256-GCM.

## Buenas prácticas

- Usar PSK largo y aleatorio (mínimo 32 caracteres).
- Rotar secretos periódicamente en entornos productivos.
- No hardcodear secretos en código público — usar variables de entorno.
- Verificar `client.connected` antes de llamar a `send_to_server`.
