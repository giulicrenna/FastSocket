"""
Custom exceptions for FastSocket.

This module defines all custom exceptions used throughout FastSocket.
"""


class FastSocketException(Exception):
    """Base exception for all FastSocket errors."""
    pass


class InvalidMessageType(FastSocketException):
    """Raised when message type is not str or bytes."""

    def __init__(self, message_type: type = None) -> None:
        self.message_type = message_type
        super().__init__()

    def __str__(self) -> str:
        if self.message_type:
            return f'Message has to be a string or bytes, got {self.message_type.__name__}'
        return 'Message has to be a string or byte array'


class NetworkException(FastSocketException):
    """Raised when network operations fail."""

    def __init__(self, message: str = None, details: str = None) -> None:
        self.message = message or 'Network Exception'
        self.details = details
        super().__init__()

    def __str__(self) -> str:
        if self.details:
            return f'{self.message}: {self.details}'
        return self.message


class BadEncryptionInput(FastSocketException):
    """Raised when encryption input is invalid."""

    def __init__(self, message: str = None) -> None:
        self.message = message or 'Invalid message to encrypt'
        super().__init__()

    def __str__(self) -> str:
        return self.message


class ConnectionClosedException(FastSocketException):
    """Raised when connection is unexpectedly closed."""

    def __init__(self, address: tuple = None) -> None:
        self.address = address
        super().__init__()

    def __str__(self) -> str:
        if self.address:
            return f'Connection closed by {self.address[0]}:{self.address[1]}'
        return 'Connection unexpectedly closed'


class FileTransferException(FastSocketException):
    """Raised when file transfer fails."""

    def __init__(self, message: str, file_path: str = None) -> None:
        self.message = message
        self.file_path = file_path
        super().__init__()

    def __str__(self) -> str:
        if self.file_path:
            return f'File transfer error for {self.file_path}: {self.message}'
        return f'File transfer error: {self.message}'


class IntegrityException(FastSocketException):
    """Raised when data integrity check fails."""

    def __init__(self, expected: str = None, got: str = None) -> None:
        self.expected = expected
        self.got = got
        super().__init__()

    def __str__(self) -> str:
        if self.expected and self.got:
            return f'Integrity check failed: expected {self.expected}, got {self.got}'
        return 'Data integrity check failed'


class ChunkException(FastSocketException):
    """Raised when chunking operations fail."""

    def __init__(self, message: str, chunk_number: int = None) -> None:
        self.message = message
        self.chunk_number = chunk_number
        super().__init__()

    def __str__(self) -> str:
        if self.chunk_number is not None:
            return f'Chunk {self.chunk_number}: {self.message}'
        return f'Chunk error: {self.message}'


class TimeoutException(FastSocketException):
    """Raised when operation times out."""

    def __init__(self, operation: str = None, timeout: float = None) -> None:
        self.operation = operation
        self.timeout = timeout
        super().__init__()

    def __str__(self) -> str:
        msg = 'Operation timed out'
        if self.operation:
            msg = f'{self.operation} timed out'
        if self.timeout:
            msg += f' after {self.timeout}s'
        return msg