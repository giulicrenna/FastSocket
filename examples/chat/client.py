"""
Chat Client with Performance Metrics

A chat client that tracks connection time, messages sent/received,
and displays performance statistics.
"""

from FastSocket import FastSocketClient, SocketConfig
import time
import threading
from datetime import datetime


class ChatClient:
    """Chat client with metrics tracking."""

    def __init__(self, host: str = 'localhost', port: int = 9000):
        self.config = SocketConfig(host=host, port=port)
        self.client = FastSocketClient(self.config)

        # Metrics
        self.connect_time = None
        self.messages_sent = 0
        self.messages_received = 0
        self.bytes_sent = 0
        self.bytes_received = 0
        self.last_message_time = None

        # Setup
        self.client.on_new_message(self.handle_message)
        self.running = True

    def handle_message(self, msg: str):
        """Handle incoming messages."""
        self.messages_received += 1
        self.bytes_received += len(msg.encode())
        self.last_message_time = time.time()

        # Display message
        print(f"\r{msg}")
        print("> ", end='', flush=True)

    def send_message(self, message: str):
        """Send a message and track metrics."""
        self.client.send_to_server(message)
        self.messages_sent += 1
        self.bytes_sent += len(message.encode())

    def get_metrics(self) -> dict:
        """Get client metrics."""
        if self.connect_time:
            uptime = time.time() - self.connect_time
        else:
            uptime = 0

        return {
            'uptime': uptime,
            'messages_sent': self.messages_sent,
            'messages_received': self.messages_received,
            'total_messages': self.messages_sent + self.messages_received,
            'bytes_sent': self.bytes_sent,
            'bytes_received': self.bytes_received,
            'total_bytes': self.bytes_sent + self.bytes_received,
            'avg_send_rate': self.messages_sent / uptime if uptime > 0 else 0,
            'avg_recv_rate': self.messages_received / uptime if uptime > 0 else 0
        }

    def display_local_metrics(self):
        """Display local client metrics."""
        metrics = self.get_metrics()

        print("\n" + "=" * 60)
        print("CLIENT METRICS")
        print("=" * 60)
        print(f"Connection time: {metrics['uptime']:.1f}s")
        print(f"Messages sent: {metrics['messages_sent']}")
        print(f"Messages received: {metrics['messages_received']}")
        print(f"Total messages: {metrics['total_messages']}")
        print(f"Bytes sent: {metrics['bytes_sent']:,}")
        print(f"Bytes received: {metrics['bytes_received']:,}")
        print(f"Total bandwidth: {metrics['total_bytes']:,} bytes")
        print(f"Send rate: {metrics['avg_send_rate']:.2f} msg/s")
        print(f"Receive rate: {metrics['avg_recv_rate']:.2f} msg/s")
        print("=" * 60)

    def input_loop(self):
        """Handle user input."""
        print("\nConnected! Type /help for commands, /localmetrics for client stats")
        print("=" * 60)

        while self.running:
            try:
                message = input("> ").strip()

                if not message:
                    continue

                if message == '/localmetrics':
                    self.display_local_metrics()
                    continue

                if message == '/quit':
                    self.send_message('/quit')
                    self.running = False
                    break

                self.send_message(message)

            except (KeyboardInterrupt, EOFError):
                print("\nDisconnecting...")
                self.running = False
                break

    def start(self):
        """Start the chat client."""
        print("=" * 60)
        print("FastSocket Chat Client")
        print("=" * 60)
        print(f"Connecting to {self.config.host}:{self.config.port}...")

        self.client.start()
        self.connect_time = time.time()
        time.sleep(0.5)  # Wait for connection

        print(f"Connected at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Start input loop in main thread
        self.input_loop()

        # Display final metrics
        print("\n" + "=" * 60)
        print("SESSION SUMMARY")
        print("=" * 60)
        metrics = self.get_metrics()
        print(f"Session duration: {metrics['uptime']:.1f}s")
        print(f"Messages exchanged: {metrics['total_messages']}")
        print(f"Data transferred: {metrics['total_bytes']:,} bytes")
        print("=" * 60)
        print("Goodbye!")


if __name__ == '__main__':
    client = ChatClient(host='localhost', port=9000)
    client.start()
