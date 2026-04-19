"""
Secure Chat Server — RSA+AES hybrid encryption with PSK authentication.

Handshake (automatic):
  1. RSA-4096 key exchange → establishes AES-256-GCM session key
  2. Both sides prove knowledge of the shared secret via HMAC-SHA256
  3. All messages encrypted with AES-256-GCM (fast, unlimited size)

Commands:
  /name <name>           - Set username
  /users                 - List online users
  /metrics               - Show server metrics
  /whisper <name> <msg>  - Private message  (/w also works)
  /me <action>           - Broadcast an action
  /ping                  - Check server connection
  /help                  - Show available commands
  /quit                  - Disconnect
"""

from FastSocket import TLSSocketServer, SocketConfig, Queue
import time
from datetime import datetime, timedelta
from threading import Lock
from typing import Dict, List, Optional, Tuple

SHARED_SECRET = "fastsocket-secret"   # Change this before deploying!


class SecureChatServer:
    def __init__(self, host: str = 'localhost', port: int = 9443):
        self.config = SocketConfig(host=host, port=port)
        self.server = TLSSocketServer(self.config, shared_secret=SHARED_SECRET)

        self.start_time = time.time()
        self.total_messages = 0
        self.messages_per_user: Dict[str, int] = {}
        self.user_names: Dict[tuple, str] = {}
        self.message_history: List[Tuple] = []
        self._lock = Lock()

        self.server.on_new_message(self.handle_messages)

    # ── send helpers ─────────────────────────────────────────────────────────

    def _send(self, addr: tuple, text: str) -> None:
        """Send an encrypted message to one client by address."""
        with self.server._client_lock:
            clients = list(self.server._client_buffer)
        for client in clients:
            if client.address == addr and client.connected:
                try:
                    client.send(text.encode('utf-8'))
                except OSError:
                    pass
                break

    def _broadcast(self, text: str, exclude: tuple = None) -> None:
        """Broadcast a timestamped encrypted message to all clients."""
        ts = datetime.now().strftime('%H:%M:%S')
        data = f"[{ts}] {text}".encode('utf-8')
        with self.server._client_lock:
            clients = list(self.server._client_buffer)
        for client in clients:
            if client.connected and client.address != exclude:
                try:
                    client.send(data)
                except OSError:
                    pass

    def _addr_for_name(self, name: str) -> Optional[tuple]:
        with self._lock:
            for addr, uname in self.user_names.items():
                if uname.lower() == name.lower():
                    return addr
        return None

    def _uptime(self) -> str:
        return str(timedelta(seconds=int(time.time() - self.start_time)))

    # ── command handlers ─────────────────────────────────────────────────────

    def _cmd_name(self, addr: tuple, args: str) -> None:
        new_name = args.strip()
        if not new_name:
            self._send(addr, "Usage: /name <username>")
            return
        if ' ' in new_name:
            self._send(addr, "Error: username cannot contain spaces.")
            return
        with self._lock:
            for a, n in self.user_names.items():
                if n.lower() == new_name.lower() and a != addr:
                    self._send(addr, f"Error: '{new_name}' is already taken.")
                    return
            old = self.user_names.get(addr, f"User-{addr[1]}")
            self.user_names[addr] = new_name
        print(f"  {old} → {new_name}")
        self._broadcast(f"*** {old} is now known as {new_name}")

    def _cmd_users(self, addr: tuple) -> None:
        with self._lock:
            names = list(self.user_names.values())
        with self.server._client_lock:
            active = len([c for c in self.server._client_buffer if c.connected])
        self._send(addr, f"Online ({active}): {', '.join(names) if names else '(none)'}")

    def _cmd_metrics(self, addr: tuple) -> None:
        with self.server._client_lock:
            active = len([c for c in self.server._client_buffer if c.connected])
        with self._lock:
            total = self.total_messages
            registered = len(self.user_names)
            avg = total / max(registered, 1)
            top = sorted(self.messages_per_user.items(), key=lambda x: x[1], reverse=True)[:5]

        lines = [
            "=== Server Metrics ===",
            f"Uptime:         {self._uptime()}",
            f"Active users:   {active}",
            f"Total messages: {total}",
            f"Avg msg/user:   {avg:.1f}",
            "Encryption:     RSA-4096 + AES-256-GCM",
            "Auth:           HMAC-SHA256 (PSK)",
        ]
        if top:
            lines.append("Top talkers:")
            for name, count in top:
                lines.append(f"  {name}: {count} msgs")
        lines.append("=" * 22)
        self._send(addr, "\n".join(lines))

    def _cmd_whisper(self, addr: tuple, args: str) -> None:
        parts = args.split(' ', 1)
        if len(parts) < 2 or not parts[1].strip():
            self._send(addr, "Usage: /whisper <name> <message>")
            return
        target_name, message = parts[0], parts[1].strip()
        target_addr = self._addr_for_name(target_name)
        if target_addr is None:
            self._send(addr, f"Error: user '{target_name}' not found.")
            return
        with self._lock:
            sender = self.user_names.get(addr, f"User-{addr[1]}")
        ts = datetime.now().strftime('%H:%M:%S')
        self._send(target_addr, f"[{ts}] [PM from {sender}] {message}")
        self._send(addr,        f"[{ts}] [PM to {target_name}] {message}")

    def _cmd_me(self, addr: tuple, args: str) -> None:
        action = args.strip()
        if not action:
            self._send(addr, "Usage: /me <action>")
            return
        with self._lock:
            username = self.user_names.get(addr, f"User-{addr[1]}")
        self._broadcast(f"* {username} {action}")

    def _cmd_ping(self, addr: tuple) -> None:
        self._send(addr, "PONG")

    def _cmd_help(self, addr: tuple) -> None:
        self._send(addr, (
            "Available commands:\n"
            "  /name <name>           - Set your username\n"
            "  /users                 - List online users\n"
            "  /metrics               - Show server metrics\n"
            "  /whisper <name> <msg>  - Send a private message  (/w)\n"
            "  /me <action>           - Broadcast an action\n"
            "  /ping                  - Check server connection\n"
            "  /help                  - Show this help\n"
            "  /quit                  - Disconnect"
        ))

    def _cmd_quit(self, addr: tuple) -> None:
        with self._lock:
            username = self.user_names.pop(addr, f"User-{addr[1]}")
        print(f"  {username} disconnected")
        self._broadcast(f"*** {username} left the chat", exclude=addr)
        with self.server._client_lock:
            clients = list(self.server._client_buffer)
        for client in clients:
            if client.address == addr:
                try:
                    client.connection.close()
                except OSError:
                    pass
                break

    # ── main handler ─────────────────────────────────────────────────────────

    def handle_messages(self, messages: Queue) -> None:
        while not messages.empty():
            msg, addr = messages.get()
            command = msg.strip()

            with self._lock:
                if addr not in self.user_names:
                    self.user_names[addr] = f"User-{addr[1]}"

            if command.startswith('/name '):
                self._cmd_name(addr, command[6:])
            elif command == '/users':
                self._cmd_users(addr)
            elif command == '/metrics':
                self._cmd_metrics(addr)
            elif command.startswith('/whisper '):
                self._cmd_whisper(addr, command[9:])
            elif command.startswith('/w '):
                self._cmd_whisper(addr, command[3:])
            elif command.startswith('/me '):
                self._cmd_me(addr, command[4:])
            elif command == '/ping':
                self._cmd_ping(addr)
            elif command == '/help':
                self._cmd_help(addr)
            elif command == '/quit':
                self._cmd_quit(addr)
            elif command.startswith('/'):
                self._send(addr, "Unknown command. Type /help for the list.")
            else:
                with self._lock:
                    username = self.user_names.get(addr, f"User-{addr[1]}")
                    self.total_messages += 1
                    self.messages_per_user[username] = self.messages_per_user.get(username, 0) + 1
                    self.message_history.append((time.time(), username, command))
                print(f"  [{username}] {command}")
                self._broadcast(f"{username}: {command}", exclude=addr)

    def start(self) -> None:
        print("=" * 60)
        print("FastSocket Secure Chat  [RSA-4096 + AES-256-GCM + HMAC]")
        print("=" * 60)
        print(f"Listening on {self.config.host}:{self.config.port}")
        print(f"Started:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Generating RSA key pair...")
        print("=" * 60)
        self.server.start()


if __name__ == '__main__':
    server = SecureChatServer(host='localhost', port=9443)
    server.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('\nServidor detenido.')
