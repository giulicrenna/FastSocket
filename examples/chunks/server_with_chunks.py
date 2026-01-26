"""
TCP Server with ChunkManager Example

This example demonstrates automatic chunking for large data transfers.
The server receives large data in chunks and reassembles it automatically.
"""

from FastSocket import FastSocketServer, SocketConfig, Queue, ChunkManager
import socket

# Create chunk manager for handling large data
chunk_manager = ChunkManager(
    chunk_size=4096,  # 4KB chunks
    use_headers=True  # Use size headers for automatic reassembly
)

def handle_messages(messages: Queue):
    """Handle incoming messages with chunk support."""
    while not messages.empty():
        msg, addr = messages.get()

        print(f'\n[{addr[0]}:{addr[1]}] Received command: {msg}')

        if msg.strip() == 'SEND_LARGE_DATA':
            # Send large response using chunks
            large_data = b'X' * 50000  # 50KB of data

            print(f'Sending {len(large_data)} bytes in chunks...')

            # Find the client connection
            for client in server._client_buffer:
                if client.address == addr and client.connected:
                    bytes_sent = chunk_manager.send_chunked(client.connection, large_data)
                    print(f'Sent {bytes_sent} bytes total (including headers)')
                    break

        elif msg.strip() == 'REQUEST_FILE':
            # Simulate sending a file
            file_content = b'This is a simulated file content. ' * 1000  # ~35KB

            print(f'Sending file ({len(file_content)} bytes)...')

            for client in server._client_buffer:
                if client.address == addr and client.connected:
                    bytes_sent = chunk_manager.send_chunked(client.connection, file_content)
                    print(f'File sent: {bytes_sent} bytes')
                    break

        else:
            # Echo small messages normally
            server.send_msg_stream(f'Echo: {msg}')

if __name__ == '__main__':
    config = SocketConfig(host='localhost', port=8080)

    server = FastSocketServer(config)
    server.on_new_message(handle_messages)

    print('=' * 60)
    print('TCP Server with ChunkManager')
    print('=' * 60)
    print(f'Listening on localhost:8080')
    print(f'Chunk size: {chunk_manager.chunk_size} bytes')
    print('\nCommands:')
    print('  - SEND_LARGE_DATA: Request 50KB of data')
    print('  - REQUEST_FILE: Request simulated file')
    print('  - Any other text: Echo back')
    print('=' * 60)

    server.start()
