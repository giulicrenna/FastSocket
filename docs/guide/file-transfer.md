# File Transfer Guide

`FileTransfer` simplifies sending and receiving files with progress tracking and integrity verification.

## Initialization

```python
from FastSocket import FileTransfer

ft = FileTransfer(
    chunk_size=8192,
    verify_integrity=True,
    hash_algorithm="sha256"
)
```

## Send a file

```python
stats = ft.send_file("./my_file.bin", connection)
print(stats)
```

## Receive a file

```python
stats = ft.receive_file(connection, save_path="./downloads")
print(stats["integrity_valid"])
```

## Tips

- Use `sha256` for a good balance between security and speed.
- Define progress callbacks for long transfers to track status in real time.
