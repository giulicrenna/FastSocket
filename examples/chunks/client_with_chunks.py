"""
TCP Client with ChunkManager Example

This example demonstrates receiving large data using ChunkManager.
The client can request large data and receive it in chunks automatically.
"""

from fastsocket import FastSocketClient, SocketConfig, ChunkManager
import socket
import time

# Create chunk manager matching server configuration
chunk_manager = ChunkManager(
    chunk_size=4096,
    use_headers=True
)

received_data = []

def handle_response(msg: str):
    """
    Handle server responses.

    For small messages, print them directly.
    For large chunked data, this won't be called - use direct socket reading instead.
    """
    print(f'\nServer: {msg}')

if __name__ == '__main__':
    config = SocketConfig(host='localhost', port=8080)

    client = FastSocketClient(config)
    client.on_new_message(handle_response)

    print('=' * 60)
    print('TCP Client with ChunkManager')
    print('=' * 60)

    client.start()
    time.sleep(0.5)  # Wait for connection

    print('\n[1] Requesting large data (50KB)...')
    client.send_to_server('SEND_LARGE_DATA')

    # Receive chunked data
    print('Receiving chunked data...')
    large_data = chunk_manager.receive_chunked(client.sock)
    print(f'✓ Received {len(large_data)} bytes')
    print(f'  First 50 bytes: {large_data[:50]}')

    time.sleep(1)

    print('\n[2] Requesting file...')
    client.send_to_server('REQUEST_FILE')

    # Receive chunked file
    print('Receiving chunked file...')
    file_data = chunk_manager.receive_chunked(client.sock)
    print(f'✓ Received file: {len(file_data)} bytes')
    print(f'  Content preview: {file_data[:100].decode("utf-8", errors="ignore")}...')

    time.sleep(1)

    print('\n[3] Sending large data to server...')
    large_upload = b'Client data: ' + (b'Y' * 30000)
    print(f'Sending {len(large_upload)} bytes in chunks...')
    bytes_sent = chunk_manager.send_chunked(client.sock, large_upload)
    print(f'✓ Sent {bytes_sent} bytes total')

    print('\n=' * 60)
    print('Demo completed! Press Ctrl+C to exit')
    print('=' * 60)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('\nClient closed')
