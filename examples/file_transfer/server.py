"""
File Transfer Server Example

This example demonstrates a file transfer server that can send files
to clients with progress tracking and integrity verification.
"""

from fastsocket import FastSocketServer, SocketConfig, Queue, FileTransfer
import os
from pathlib import Path

# Initialize file transfer handler
file_transfer = FileTransfer(
    chunk_size=8192,  # 8KB chunks
    verify_integrity=True,  # Enable hash verification
    hash_algorithm='sha256'
)

def handle_commands(messages: Queue):
    """Handle client commands for file transfer."""
    while not messages.empty():
        msg, addr = messages.get()
        command = msg.strip()

        print(f'\n[{addr[0]}:{addr[1]}] Command: {command}')

        if command.startswith('GET:'):
            # Client requests a file
            filename = command[4:].strip()
            filepath = Path('files_to_send') / filename

            if not filepath.exists():
                print(f'❌ File not found: {filename}')
                for client in server._client_buffer:
                    if client.address == addr:
                        client.connection.sendall(b'ERROR:File not found\n')
                        break
                continue

            # Find client connection
            for client in server._client_buffer:
                if client.address == addr and client.connected:
                    # Send confirmation
                    client.connection.sendall(b'OK:Sending file\n')

                    # Define progress callback
                    def progress(sent, total):
                        pct = (sent / total) * 100
                        print(f'\r  Progress: {sent}/{total} bytes ({pct:.1f}%)', end='', flush=True)

                    # Send file
                    print(f'📤 Sending: {filename}')
                    try:
                        stats = file_transfer.send_file(
                            filepath,
                            client.connection,
                            progress_callback=progress
                        )
                        print(f'\n✅ Sent: {filename}')
                        print(f'   Size: {stats["file_size"]} bytes')
                        print(f'   Hash: {stats["hash"][:16]}...')
                    except Exception as e:
                        print(f'\n❌ Error sending file: {e}')

                    break

        elif command == 'LIST':
            # List available files
            files_dir = Path('files_to_send')
            if files_dir.exists():
                files = [f.name for f in files_dir.iterdir() if f.is_file()]
                file_list = '\n'.join(files) if files else 'No files available'

                for client in server._client_buffer:
                    if client.address == addr:
                        response = f'FILES:{len(files)}\n{file_list}\n'
                        client.connection.sendall(response.encode())
                        break

                print(f'📋 Sent file list ({len(files)} files)')
            else:
                print('❌ files_to_send directory not found')

if __name__ == '__main__':
    # Create files_to_send directory if it doesn't exist
    Path('files_to_send').mkdir(exist_ok=True)

    # Create some sample files for testing
    sample_files = [
        ('sample.txt', 'This is a sample text file.\n' * 100),
        ('data.json', '{"message": "Sample JSON data", "numbers": [1,2,3,4,5]}\n' * 50),
    ]

    for filename, content in sample_files:
        filepath = Path('files_to_send') / filename
        if not filepath.exists():
            with open(filepath, 'w') as f:
                f.write(content)

    config = SocketConfig(host='localhost', port=8080)
    server = FastSocketServer(config)
    server.on_new_message(handle_commands)

    print('=' * 60)
    print('File Transfer Server')
    print('=' * 60)
    print(f'Listening on localhost:8080')
    print(f'Chunk size: {file_transfer.chunk_manager.chunk_size} bytes')
    print(f'Integrity check: {file_transfer.verify_integrity}')
    print(f'Hash algorithm: {file_transfer.hash_algorithm}')
    print('\nCommands:')
    print('  LIST          - List available files')
    print('  GET:filename  - Request a file')
    print('=' * 60)

    server.start()
