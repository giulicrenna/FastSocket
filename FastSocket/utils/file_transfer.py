"""
File transfer module for FastSocket.

This module provides high-level file transfer functionality with
progress tracking, integrity verification, and resumable transfers.
"""

import os
import hashlib
import socket
from typing import Callable, Optional, Tuple
from pathlib import Path

from fastsocket.utils.chunks import ChunkManager
from fastsocket.utils.framing import send_framed, recv_framed
from fastsocket.utils.logger import Logger


class FileTransfer:
    """
    High-level file transfer handler with progress tracking.

    This class provides automatic file transfer over socket connections
    with optional integrity verification and progress callbacks.

    Attributes:
        chunk_manager: ChunkManager instance for handling data transfer
        verify_integrity: Whether to compute and verify file hashes
        hash_algorithm: Hash algorithm to use ('md5', 'sha256', etc.)

    Example:
        >>> transfer = FileTransfer(chunk_size=8192, verify_integrity=True)
        >>> transfer.send_file('document.pdf', socket)
        >>> transfer.receive_file(socket, 'received.pdf')
    """

    def __init__(self,
                 chunk_size: int = 8192,
                 verify_integrity: bool = True,
                 hash_algorithm: str = 'sha256'):
        """
        Initialize file transfer handler.

        Args:
            chunk_size: Size of chunks for transfer (default: 8KB)
            verify_integrity: Enable hash-based integrity checking
            hash_algorithm: Hash algorithm ('md5', 'sha256', 'sha1')
        """
        self.chunk_manager = ChunkManager(chunk_size=chunk_size, use_headers=True)
        self.verify_integrity = verify_integrity
        self.hash_algorithm = hash_algorithm

    def send_file(self,
                  file_path: str | Path,
                  connection: socket.socket,
                  progress_callback: Optional[Callable[[int, int], None]] = None) -> dict:
        """
        Send a file over a socket connection.

        The file is sent with metadata (filename, size, hash) followed by
        the file content in chunks.

        Args:
            file_path: Path to file to send
            connection: Socket connection to send through
            progress_callback: Optional callback(bytes_sent, total_bytes)

        Returns:
            dict: Transfer statistics including bytes_sent, hash, etc.

        Raises:
            FileNotFoundError: If file doesn't exist
            OSError: If sending fails

        Example:
            >>> def progress(sent, total):
            ...     print(f"{sent}/{total} bytes ({sent/total*100:.1f}%)")
            >>> stats = transfer.send_file('video.mp4', sock, progress)
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_size = file_path.stat().st_size
        file_name = file_path.name

        Logger.print_log_debug(f'Sending file: {file_name} ({file_size} bytes)')

        # Compute hash if verification is enabled
        file_hash = None
        if self.verify_integrity:
            file_hash = self._compute_file_hash(file_path)
            Logger.print_log_debug(f'File hash ({self.hash_algorithm}): {file_hash}')

        # Send metadata using framing to avoid byte-by-byte reads on the receiver
        metadata = f"{file_name}|{file_size}|{file_hash or 'NONE'}"
        send_framed(connection, metadata.encode('utf-8'))

        # Send file content
        bytes_sent = 0
        hash_obj = hashlib.new(self.hash_algorithm) if self.verify_integrity else None

        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(self.chunk_manager.chunk_size)
                if not chunk:
                    break

                if hash_obj:
                    hash_obj.update(chunk)

                # Send chunk with headers
                self.chunk_manager.send_chunked(connection, chunk)
                bytes_sent += len(chunk)

                if progress_callback:
                    progress_callback(bytes_sent, file_size)

        # Send termination (empty chunk handled by ChunkManager)

        Logger.print_log_debug(f'File sent: {bytes_sent} bytes')

        return {
            'file_name': file_name,
            'file_size': file_size,
            'bytes_sent': bytes_sent,
            'hash': file_hash,
            'hash_algorithm': self.hash_algorithm if self.verify_integrity else None
        }

    def receive_file(self,
                     connection: socket.socket,
                     save_path: str | Path = None,
                     progress_callback: Optional[Callable[[int, int], None]] = None) -> dict:
        """
        Receive a file over a socket connection.

        Receives file metadata, content in chunks, and optionally verifies
        integrity using the transmitted hash.

        Args:
            connection: Socket connection to receive from
            save_path: Path to save file (uses transmitted name if None)
            progress_callback: Optional callback(bytes_received, total_bytes)

        Returns:
            dict: Transfer statistics including file info and verification

        Raises:
            ValueError: If hash verification fails
            OSError: If receiving fails

        Example:
            >>> def progress(recv, total):
            ...     pct = recv/total*100
            ...     print(f"\\rProgress: {pct:.1f}%", end='')
            >>> stats = transfer.receive_file(sock, 'downloads/', progress)
        """
        # Receive metadata via framing (single recv_framed call, no byte-by-byte loop)
        metadata_bytes = recv_framed(connection)
        if metadata_bytes is None:
            raise ConnectionError("Connection closed during metadata transfer")
        metadata = metadata_bytes.decode('utf-8')
        file_name, file_size_str, file_hash = metadata.split('|')
        file_size = int(file_size_str)

        if file_hash == 'NONE':
            file_hash = None

        Logger.print_log_debug(f'Receiving file: {file_name} ({file_size} bytes)')

        # Determine save path
        if save_path is None:
            save_path = Path(file_name)
        else:
            save_path = Path(save_path)
            if save_path.is_dir():
                save_path = save_path / file_name

        # Create parent directory if needed
        save_path.parent.mkdir(parents=True, exist_ok=True)

        # Receive file content
        bytes_received = 0
        hash_obj = hashlib.new(self.hash_algorithm) if file_hash else None

        with open(save_path, 'wb') as f:
            while bytes_received < file_size:
                # Receive chunk
                chunk = self.chunk_manager.receive_chunked(connection)

                if not chunk:
                    break

                if hash_obj:
                    hash_obj.update(chunk)

                f.write(chunk)
                bytes_received += len(chunk)

                if progress_callback:
                    progress_callback(bytes_received, file_size)

        Logger.print_log_debug(f'File received: {bytes_received} bytes')

        # Verify integrity
        computed_hash = hash_obj.hexdigest() if hash_obj else None
        integrity_valid = True

        if file_hash and computed_hash:
            integrity_valid = (computed_hash == file_hash)
            if not integrity_valid:
                Logger.print_log_error(
                    f'Hash mismatch! Expected: {file_hash}, Got: {computed_hash}',
                    'FileTransfer'
                )
                raise ValueError(f'File integrity check failed for {file_name}')
            else:
                Logger.print_log_debug('File integrity verified ✓')

        return {
            'file_name': file_name,
            'file_size': file_size,
            'bytes_received': bytes_received,
            'save_path': str(save_path),
            'transmitted_hash': file_hash,
            'computed_hash': computed_hash,
            'integrity_valid': integrity_valid,
            'hash_algorithm': self.hash_algorithm if file_hash else None
        }

    def _compute_file_hash(self, file_path: Path) -> str:
        """
        Compute hash of a file.

        Args:
            file_path: Path to file

        Returns:
            str: Hexadecimal hash string
        """
        hash_obj = hashlib.new(self.hash_algorithm)

        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(self.chunk_manager.chunk_size)
                if not chunk:
                    break
                hash_obj.update(chunk)

        return hash_obj.hexdigest()

    def estimate_transfer_time(self,
                               file_size: int,
                               bandwidth_bps: int) -> Tuple[float, int, int]:
        """
        Estimate transfer time and overhead for a file.

        Args:
            file_size: File size in bytes
            bandwidth_bps: Bandwidth in bytes per second

        Returns:
            Tuple[float, int, int]: (time_seconds, num_chunks, overhead_bytes)

        Example:
            >>> transfer = FileTransfer(chunk_size=8192)
            >>> time, chunks, overhead = transfer.estimate_transfer_time(
            ...     file_size=10*1024*1024,  # 10MB
            ...     bandwidth_bps=1024*1024  # 1MB/s
            ... )
            >>> print(f"ETA: {time:.1f}s, {chunks} chunks, {overhead}B overhead")
        """
        num_chunks, overhead = self.chunk_manager.estimate_chunks(file_size)

        # Add metadata overhead (rough estimate)
        metadata_overhead = 100  # filename + size + hash
        total_overhead = overhead + metadata_overhead

        total_bytes = file_size + total_overhead
        transfer_time = total_bytes / bandwidth_bps if bandwidth_bps > 0 else 0

        return transfer_time, num_chunks, total_overhead
