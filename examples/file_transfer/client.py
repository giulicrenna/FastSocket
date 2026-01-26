"""
File Transfer Client Example

This example demonstrates a file transfer client that can request
and receive files from a server with progress tracking.
"""

from FastSocket import FastSocketClient, SocketConfig, FileTransfer
import time
from pathlib import Path

# Initialize file transfer handler
file_transfer = FileTransfer(
    chunk_size=8192,
    verify_integrity=True,
    hash_algorithm='sha256'
)

def handle_response(msg: str):
    """Handle server responses."""
    if not msg.strip():
        return

    if msg.startswith('FILES:'):
        # File list response
        lines = msg.split('\n')
        count = int(lines[0].split(':')[1])
        print(f'\n📋 Available files ({count}):')
        for i, filename in enumerate(lines[1:-1], 1):
            if filename:
                print(f'  {i}. {filename}')
        print()

    elif msg.startswith('OK:'):
        print(f'✓ Server: {msg[3:]}')

    elif msg.startswith('ERROR:'):
        print(f'❌ Server error: {msg[6:]}')

    else:
        print(f'Server: {msg}')

if __name__ == '__main__':
    config = SocketConfig(host='localhost', port=8080)
    client = FastSocketClient(config)
    client.on_new_message(handle_response)

    print('=' * 60)
    print('File Transfer Client')
    print('=' * 60)

    client.start()
    time.sleep(0.5)  # Wait for connection

    # Create downloads directory
    downloads_dir = Path('downloads')
    downloads_dir.mkdir(exist_ok=True)

    print('\n[1] Listing available files...')
    client.send_to_server('LIST')
    time.sleep(1)

    print('[2] Requesting sample.txt...')
    client.send_to_server('GET:sample.txt')

    # Wait for server confirmation
    time.sleep(0.5)

    # Define progress callback
    def progress(received, total):
        pct = (received / total) * 100
        print(f'\r  Progress: {received}/{total} bytes ({pct:.1f}%)', end='', flush=True)

    # Receive file
    print('📥 Receiving file...')
    try:
        stats = file_transfer.receive_file(
            client.sock,
            save_path=downloads_dir,
            progress_callback=progress
        )

        print(f'\n✅ File received successfully!')
        print(f'   Name: {stats["file_name"]}')
        print(f'   Size: {stats["file_size"]} bytes')
        print(f'   Saved to: {stats["save_path"]}')
        print(f'   Hash: {stats["computed_hash"][:16]}...')
        print(f'   Integrity: {"✓ Verified" if stats["integrity_valid"] else "✗ Failed"}')

    except Exception as e:
        print(f'\n❌ Error receiving file: {e}')

    time.sleep(1)

    print('\n[3] Requesting data.json...')
    client.send_to_server('GET:data.json')
    time.sleep(0.5)

    # Receive second file
    print('📥 Receiving file...')
    try:
        stats = file_transfer.receive_file(
            client.sock,
            save_path=downloads_dir,
            progress_callback=progress
        )

        print(f'\n✅ File received successfully!')
        print(f'   Name: {stats["file_name"]}')
        print(f'   Size: {stats["file_size"]} bytes')
        print(f'   Saved to: {stats["save_path"]}')

    except Exception as e:
        print(f'\n❌ Error receiving file: {e}')

    print('\n' + '=' * 60)
    print('Transfer complete! Check the downloads/ directory')
    print('=' * 60)
    print('\nPress Ctrl+C to exit')

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('\nClient closed')
