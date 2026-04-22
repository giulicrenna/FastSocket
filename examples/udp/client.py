"""
UDP Echo Client Example

This example demonstrates a simple UDP client that sends datagrams
to a server and receives responses.
"""

from fastsocket import FastSocketUDPClient, SocketConfig
import socket
import time

def handle_response(msg: str, addr: tuple):
    """Handle incoming UDP responses."""
    print(f'Server response: {msg}')

if __name__ == '__main__':
    # Create UDP client configuration
    config = SocketConfig(
        host='localhost',
        port=9000,
        type=socket.SOCK_DGRAM  # UDP socket type
    )

    # Create and configure client
    client = FastSocketUDPClient(
        config,
        recv_size=65507,
        enable_broadcast=False
    )

    # Register message handler
    client.on_new_message(handle_response)

    # Bind to receive responses
    client.bind(('0.0.0.0', 9001))

    # Start client (starts message handlers)
    client.start()

    # Send some messages
    print('Sending datagrams to server...')
    for i in range(5):
        message = f'Message {i+1}: Hello from UDP client!'
        bytes_sent = client.send_to_server(message)
        print(f'Sent: {message} ({bytes_sent} bytes)')
        time.sleep(1)

    print('\nPress Ctrl+C to exit')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        client.close()
        print('\nClient closed')
