"""
Chat Client

Local commands (no server round-trip):
  /localmetrics  - Show this client's session stats
  /quit          - Disconnect

Server commands (see /help):
  /name, /users, /metrics, /whisper (/w), /me, /ping, /help
"""

from fastsocket import FastSocketClient, SocketConfig
import time
from datetime import datetime


class ChatClient:
    def __init__(self, host: str = 'localhost', port: int = 9000):
        self.config = SocketConfig(host=host, port=port)
        self.client = FastSocketClient(self.config)

        self.connect_time: float = 0.0
        self.messages_sent = 0
        self.messages_received = 0
        self.bytes_sent = 0
        self.bytes_received = 0
        self.running = True

        self.client.on_new_message(self._on_message)

    # ── receive ───────────────────────────────────────────────────────────────

    def _on_message(self, msg: str) -> None:
        self.messages_received += 1
        self.bytes_received += len(msg.encode())
        # Erase the "> " prompt, print the message, redraw prompt
        print(f"\r{msg}\n> ", end='', flush=True)

    # ── local commands ────────────────────────────────────────────────────────

    def _show_local_metrics(self) -> None:
        uptime = time.time() - self.connect_time
        print(
            "\n=== Client Metrics ===\n"
            f"Session time:   {uptime:.1f}s\n"
            f"Messages sent:  {self.messages_sent}\n"
            f"Messages recv:  {self.messages_received}\n"
            f"Bytes sent:     {self.bytes_sent:,}\n"
            f"Bytes received: {self.bytes_received:,}\n"
            "====================="
        )

    # ── send ──────────────────────────────────────────────────────────────────

    def _send(self, message: str) -> None:
        self.client.send_to_server(message)
        self.messages_sent += 1
        self.bytes_sent += len(message.encode())

    # ── input loop ────────────────────────────────────────────────────────────

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

    # ── entry point ───────────────────────────────────────────────────────────

    def start(self) -> None:
        print("=" * 60)
        print("FastSocket Chat Client")
        print("=" * 60)
        print(f"Connecting to {self.config.host}:{self.config.port}...")

        self.client.start()
        self.connect_time = time.time()
        time.sleep(0.3)
        print(f"Connected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        self._input_loop()

        uptime = time.time() - self.connect_time
        print(
            "\n=== Session Summary ===\n"
            f"Duration:  {uptime:.1f}s\n"
            f"Sent:      {self.messages_sent} msgs\n"
            f"Received:  {self.messages_received} msgs\n"
            "Goodbye!"
        )


if __name__ == '__main__':
    client = ChatClient(host='localhost', port=9000)
    client.start()
