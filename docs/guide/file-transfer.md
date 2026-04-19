# Guía File Transfer

`FileTransfer` simplifica envío/recepción de archivos, con progreso y verificación de integridad.

## Inicialización

```python
from FastSocket import FileTransfer

ft = FileTransfer(
    chunk_size=8192,
    verify_integrity=True,
    hash_algorithm="sha256"
)
```

## Enviar archivo

```python
stats = ft.send_file("./mi_archivo.bin", connection)
print(stats)
```

## Recibir archivo

```python
stats = ft.receive_file(connection, save_path="./downloads")
print(stats["integrity_valid"])
```

## Recomendaciones

- Usar `sha256` para balance entre seguridad y velocidad.
- Definir callbacks de progreso en transferencias largas.
