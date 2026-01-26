"""
UDP Echo Server Example

This example demonstrates a simple UDP echo server that receives
datagrams from multiple sources and echoes them back.
"""

from FastSocket import FastSocketUDPServer, SocketConfig, Queue
import socket

def handle_messages(messages: Queue):
    """Handle incoming UDP messages and echo them back."""
    while not messages.empty():
        msg, addr = messages.get()
        print(f'[{addr[0]}:{addr[1]}] {msg}')

        # Echo the message back to the sender
        server.send_to(addr, f'Echo: {msg}')

if __name__ == '__main__':
    # Create UDP server configuration
    config = SocketConfig(
        host='0.0.0.0',  # Listen on all interfaces
        port=9000,
        type=socket.SOCK_DGRAM  # UDP socket type
    )

    # Create and configure server
    server = FastSocketUDPServer(
        config,
        recv_size=65507,  # Max UDP datagram size
        client_timeout=60.0,  # Remove inactive sources after 60s
        enable_broadcast=True  # Enable broadcast support
    )

    server.on_new_message(handle_messages)

    print('UDP Echo Server started on port 9000')
    print('Waiting for datagrams...')

    server.start()
