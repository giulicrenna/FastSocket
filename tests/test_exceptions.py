"""Tests for custom exception classes."""

import pytest
from FastSocket.utils.exceptions import (
    InvalidMessageType,
    NetworkException,
    BadEncryptionInput,
    ConnectionClosedException,
    FileTransferException,
    IntegrityException,
    ChunkException,
    TimeoutException,
    FastSocketException,
)


def test_invalid_message_type_with_type():
    exc = InvalidMessageType(int)
    assert "int" in str(exc)


def test_invalid_message_type_without_type():
    exc = InvalidMessageType()
    s = str(exc).lower()
    assert "string" in s or "bytes" in s


def test_network_exception_with_details():
    exc = NetworkException("Connection failed", "timeout")
    assert "Connection failed" in str(exc)
    assert "timeout" in str(exc)


def test_network_exception_default_message():
    exc = NetworkException()
    assert str(exc)  # not empty


def test_bad_encryption_input():
    exc = BadEncryptionInput("bad key")
    assert "bad key" in str(exc)


def test_connection_closed_with_address():
    exc = ConnectionClosedException(("192.168.1.1", 8080))
    assert "192.168.1.1" in str(exc)
    assert "8080" in str(exc)


def test_connection_closed_without_address():
    exc = ConnectionClosedException()
    assert str(exc)


def test_file_transfer_exception_with_path():
    exc = FileTransferException("disk full", "/tmp/test.txt")
    assert "/tmp/test.txt" in str(exc)
    assert "disk full" in str(exc)


def test_integrity_exception_with_hashes():
    exc = IntegrityException("abc123", "def456")
    assert "abc123" in str(exc)
    assert "def456" in str(exc)


def test_chunk_exception_with_number():
    exc = ChunkException("too large", 5)
    assert "5" in str(exc)
    assert "too large" in str(exc)


def test_timeout_exception_with_details():
    exc = TimeoutException("connect", 30.0)
    assert "connect" in str(exc)
    assert "30" in str(exc)


def test_all_exceptions_inherit_from_base():
    for cls in [
        InvalidMessageType, NetworkException, BadEncryptionInput,
        ConnectionClosedException, FileTransferException, IntegrityException,
        ChunkException, TimeoutException,
    ]:
        assert issubclass(cls, FastSocketException)
