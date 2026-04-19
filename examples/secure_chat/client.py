"""
Secure Chat Client — RSA+AES hybrid encryption with PSK authentication.

All messages are AES-256-GCM encrypted. The server is authenticated
via HMAC before any chat traffic flows.

Local commands:
  /localmetrics  - Show session stats
  /quit  /q      - Disconnect
"""

from FastSocket import TLSSocketClient, SocketConfig
import time
from datetime import datetime

SHARED_SECRET = "fastsocket-secret"   # Must match the server!


class SecureChatClient:
    def __init__(self, host: str = 'localhost', port: int = 9443):
        self.config = SocketConfig(host=host, port=port)
        self.client = TLSSocketClient(self.config, shared_secret=SHARED_SECRET)

        self.connect_time: float = 0.0
        self.messages_sent = 0
        self.messages_received = 0
        self.bytes_sent = 0
        self.bytes_received = 0
        self.running = True

        self.client.on_new_message(self._on_message)

    def _on_message(self, msg: str) -> None:
        self.messages_received += 1
        self.bytes_received += len(msg.encode())
        print(f"\r{msg}\n> ", end='', flush=True)

    def _show_local_metrics(self) -> None:
        uptime = time.time() - self.connect_time
        print(
            "\n=== Client Metrics ===\n"
            f"Session time:   {uptime:.1f}s\n"
            f"Messages sent:  {self.messages_sent}\n"
            f"Messages recv:  {self.messages_received}\n"
            f"Bytes sent:     {self.bytes_sent:,}\n"
            f"Bytes received: {self.bytes_received:,}\n"
            "Encryption:     RSA-4096 + AES-256-GCM\n"
            "Auth:           HMAC-SHA256 (PSK)\n"
            "====================="
        )

    def _send(self, message: str) -> None:
        self.client.send_to_server(message)
        self.messages_sent += 1
        self.bytes_sent += len(message.encode())

    def _input_loop(self) -> None:
        print("Connected! Type /help for commands.\n" + "=" * 60)
        while self.running:
            try:
                message = input("> ").strip()
                if not message:
                    continue
                if message == '/localmetrics':
                    self._show_local_metrics()
                elif message in ('/quit', '/q'):
                    self._send('/quit')
                    self.running = False
                else:
                    self._send(message)
            except (KeyboardInterrupt, EOFError):
                print()
                self.running = False

    def start(self) -> None:
        print("=" * 60)
        print("FastSocket Secure Chat  [RSA-4096 + AES-256-GCM + HMAC]")
        print("=" * 60)
        print(f"Connecting to {self.config.host}:{self.config.port}...")
        print("Performing key exchange and authentication...")

        self.client.start()
        self.connect_time = time.time()

        # Wait for handshake (RSA key generation can take a moment)
        timeout = time.time() + 20
        while not self.client.connected:
            if time.time() > timeout:
                print("Error: handshake timed out.")
                return
            if not self.client.is_alive():
                print("Error: authentication failed (wrong shared secret?).")
                return
            time.sleep(0.1)

        print(f"Secure channel ready at {datetime.now().strftime('%H:%M:%S')}")
        print("RSA-4096 key exchange + HMAC-SHA256 auth complete.")

        self._input_loop()

        uptime = time.time() - self.connect_time
        print(
            f"\nSession: {uptime:.1f}s  |  "
            f"Sent: {self.messages_sent}  |  "
            f"Received: {self.messages_received}\n"
            "Goodbye!"
        )


if __name__ == '__main__':
    client = SecureChatClient(host='localhost', port=9443)
    client.start()
