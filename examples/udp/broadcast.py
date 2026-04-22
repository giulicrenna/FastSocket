"""
UDP Broadcast Example

This example demonstrates UDP broadcast for service discovery
or network announcements.
"""

from fastsocket import FastSocketUDPClient, SocketConfig
import socket
import time

def handle_response(msg: str, addr: tuple):
    """Handle responses from broadcast."""
    print(f'Response from {addr[0]}:{addr[1]}: {msg}')

if __name__ == '__main__':
    # Create UDP client with broadcast enabled
    config = SocketConfig(
        host='<broadcast>',  # Placeholder, actual broadcast addr used in method
        port=9000,
        type=socket.SOCK_DGRAM
    )

    client = FastSocketUDPClient(
        config,
        enable_broadcast=True  # Must enable broadcast
    )

    # Register response handler
    client.on_new_message(handle_response)

    # Bind to receive responses
    client.bind(('0.0.0.0', 9002))

    # Start client
    client.start()

    print('Broadcasting discovery messages...')

    # Send broadcast messages
    for i in range(3):
        message = f'DISCOVERY_REQUEST_{i+1}'
        try:
            bytes_sent = client.broadcast_message(
                message,
                port=9000,
                broadcast_addr='255.255.255.255'
            )
            print(f'Broadcast sent: {message} ({bytes_sent} bytes)')
        except Exception as e:
            print(f'Broadcast failed: {e}')

        time.sleep(2)

    print('\nListening for responses (press Ctrl+C to exit)...')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        client.close()
        print('\nBroadcast client closed')
