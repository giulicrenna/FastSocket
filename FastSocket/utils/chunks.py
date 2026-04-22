"""
Chunk management module for FastSocket.

This module provides automatic chunking and reassembly of large data
transmissions over socket connections.
"""

import socket
import struct
from typing import List, Iterator, Tuple
from FastSocket.utils.logger import Logger


class ChunkManager:
    """
    Manager for splitting and reassembling data into chunks.

    This class handles automatic chunking of large data for transmission
    over sockets and reassembly on the receiving end.

    Attributes:
        chunk_size (int): Size of each chunk in bytes
        use_headers (bool): Whether to include size headers in chunks

    Example:
        >>> manager = ChunkManager(chunk_size=4096)
        >>> chunks = manager.split_data(large_data)
        >>> manager.send_chunked(socket, large_data)
        >>> received = manager.receive_chunked(socket)
    """

    def __init__(self, chunk_size: int = 4096, use_headers: bool = True):
        """
        Initialize chunk manager.

        Args:
            chunk_size: Size of each chunk in bytes (default: 4KB)
            use_headers: Include chunk metadata headers (default: True)
        """
        self.chunk_size = chunk_size
        self.use_headers = use_headers
        self._header_format = '!I'  # Network byte order, unsigned int (4 bytes)
        self._header_size = struct.calcsize(self._header_format)

    def split_data(self, data: bytes | str) -> List[bytes]:
        """
        Split data into chunks.

        Args:
            data: Data to split (bytes or string)

        Returns:
            List[bytes]: List of data chunks

        Example:
            >>> manager = ChunkManager(chunk_size=1024)
            >>> chunks = manager.split_data(b"x" * 5000)
            >>> len(chunks)
            5
        """
        if isinstance(data, str):
            data = data.encode('utf-8')

        chunks = []
        for i in range(0, len(data), self.chunk_size):
            chunk = data[i:i + self.chunk_size]
            chunks.append(chunk)

        return chunks

    def reassemble_chunks(self, chunks: List[bytes]) -> bytes:
        """
        Reassemble chunks into original data.

        Args:
            chunks: List of data chunks

        Returns:
            bytes: Reassembled data

        Example:
            >>> manager = ChunkManager()
            >>> chunks = [b"Hello", b" ", b"World"]
            >>> manager.reassemble_chunks(chunks)
            b'Hello World'
        """
        return b''.join(chunks)

    def send_chunked(self, connection: socket.socket, data: bytes | str) -> int:
        """
        Send data in chunks over a socket connection.

        If use_headers is True, each chunk is prefixed with a 4-byte
        header containing the chunk size. The final chunk is followed
        by a zero-length header to signal completion.

        Args:
            connection: Socket connection to send through
            data: Data to send (bytes or string)

        Returns:
            int: Total number of bytes sent (including headers)

        Raises:
            OSError: If sending fails

        Example:
            >>> manager = ChunkManager(chunk_size=4096)
            >>> bytes_sent = manager.send_chunked(socket, large_data)
        """
        if isinstance(data, str):
            data = data.encode('utf-8')

        chunks = self.split_data(data)
        total_sent = 0

        Logger.print_log_debug(f'Sending {len(data)} bytes in {len(chunks)} chunks')

        for i, chunk in enumerate(chunks):
            if self.use_headers:
                # Send chunk size header
                header = struct.pack(self._header_format, len(chunk))
                connection.sendall(header)
                total_sent += len(header)

            # Send chunk data
            connection.sendall(chunk)
            total_sent += len(chunk)

            Logger.print_log_debug(f'Sent chunk {i+1}/{len(chunks)} ({len(chunk)} bytes)')

        if self.use_headers:
            # Send termination header (zero length)
            header = struct.pack(self._header_format, 0)
            connection.sendall(header)
            total_sent += len(header)

        Logger.print_log_debug(f'Total sent: {total_sent} bytes')
        return total_sent

    def receive_chunked(self, connection: socket.socket,
                       max_size: int = None) -> bytes:
        """
        Receive chunked data from a socket connection.

        If use_headers is True, reads chunks until a zero-length header
        is received. Otherwise, reads until max_size or connection closes.

        Args:
            connection: Socket connection to receive from
            max_size: Maximum bytes to receive (optional, for headerless mode)

        Returns:
            bytes: Reassembled data

        Raises:
            OSError: If receiving fails
            ValueError: If chunk size exceeds reasonable limits

        Example:
            >>> manager = ChunkManager(chunk_size=4096)
            >>> data = manager.receive_chunked(socket)
        """
        chunks = []
        total_received = 0

        if self.use_headers:
            while True:
                # Read chunk size header
                header_data = self._recv_exactly(connection, self._header_size)
                if not header_data:
                    break

                chunk_size = struct.unpack(self._header_format, header_data)[0]

                # Zero-length header signals end
                if chunk_size == 0:
                    Logger.print_log_debug('Received termination header')
                    break

                # Sanity check for chunk size
                if chunk_size > self.chunk_size * 10:  # Allow some flexibility
                    raise ValueError(f'Chunk size {chunk_size} exceeds limit')

                # Read chunk data
                chunk = self._recv_exactly(connection, chunk_size)
                if not chunk or len(chunk) != chunk_size:
                    Logger.print_log_error(f'Incomplete chunk received', 'ChunkManager')
                    break

                chunks.append(chunk)
                total_received += len(chunk)
                Logger.print_log_debug(f'Received chunk {len(chunks)} ({chunk_size} bytes)')

        else:
            # Headerless mode - receive until max_size or connection closes
            while True:
                if max_size and total_received >= max_size:
                    break

                to_receive = self.chunk_size
                if max_size:
                    to_receive = min(self.chunk_size, max_size - total_received)

                chunk = connection.recv(to_receive)
                if not chunk:
                    break

                chunks.append(chunk)
                total_received += len(chunk)

        Logger.print_log_debug(f'Total received: {total_received} bytes in {len(chunks)} chunks')
        return self.reassemble_chunks(chunks)

    def _recv_exactly(self, connection: socket.socket, size: int) -> bytes:
        """
        Receive exactly size bytes from socket.

        Continues receiving until the exact number of bytes is read
        or the connection is closed.

        Args:
            connection: Socket connection
            size: Number of bytes to receive

        Returns:
            bytes: Received data (may be less than size if connection closes)
        """
        buf = bytearray()
        while len(buf) < size:
            packet = connection.recv(size - len(buf))
            if not packet:
                break
            buf.extend(packet)
        return bytes(buf)

    def iter_chunks(self, data: bytes | str) -> Iterator[bytes]:
        """
        Create an iterator over data chunks.

        Useful for processing large data without loading all chunks
        into memory at once.

        Args:
            data: Data to iterate over

        Yields:
            bytes: Individual chunks

        Example:
            >>> manager = ChunkManager(chunk_size=1024)
            >>> for chunk in manager.iter_chunks(large_data):
            ...     process(chunk)
        """
        if isinstance(data, str):
            data = data.encode('utf-8')

        for i in range(0, len(data), self.chunk_size):
            yield data[i:i + self.chunk_size]

    def estimate_chunks(self, data_size: int) -> Tuple[int, int]:
        """
        Estimate number of chunks and overhead for a data size.

        Args:
            data_size: Size of data in bytes

        Returns:
            Tuple[int, int]: (number_of_chunks, overhead_bytes)

        Example:
            >>> manager = ChunkManager(chunk_size=4096)
            >>> chunks, overhead = manager.estimate_chunks(100000)
            >>> print(f"Will send {chunks} chunks with {overhead} bytes overhead")
        """
        num_chunks = (data_size + self.chunk_size - 1) // self.chunk_size
        overhead = 0

        if self.use_headers:
            overhead = (num_chunks + 1) * self._header_size  # +1 for termination header

        return num_chunks, overhead
