"""
Multi-Client Chat Server with Metrics

A chat server that supports multiple clients with real-time metrics
including message count, active users, and uptime.
"""

from FastSocket import FastSocketServer, SocketConfig, Queue
import time
from datetime import datetime, timedelta
from typing import Dict, List


class ChatServer:
    """Chat server with metrics tracking."""

    def __init__(self, host: str = 'localhost', port: int = 9000):
        self.config = SocketConfig(host=host, port=port)
        self.server = FastSocketServer(self.config)

        # Metrics
        self.start_time = time.time()
        self.total_messages = 0
        self.messages_per_user: Dict[str, int] = {}
        self.user_names: Dict[tuple, str] = {}  # address -> username
        self.message_history: List[tuple] = []  # (timestamp, user, message)

        # Setup
        self.server.on_new_message(self.handle_messages)

    def get_uptime(self) -> str:
        """Get server uptime."""
        uptime_seconds = time.time() - self.start_time
        uptime = timedelta(seconds=int(uptime_seconds))
        return str(uptime)

    def get_metrics(self) -> dict:
        """Get current server metrics."""
        active_clients = len([c for c in self.server._client_buffer if c.connected])

        return {
            'uptime': self.get_uptime(),
            'total_messages': self.total_messages,
            'active_users': active_clients,
            'registered_users': len(self.user_names),
            'messages_per_user': self.messages_per_user.copy(),
            'avg_messages_per_user': self.total_messages / max(len(self.user_names), 1)
        }

    def broadcast_message(self, message: str, exclude_addr: tuple = None):
        """Broadcast message to all clients except one."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted = f"[{timestamp}] {message}"

        for client in self.server._client_buffer:
            if client.connected and client.address != exclude_addr:
                try:
                    client.connection.sendall(formatted.encode())
                except:
                    pass

    def handle_messages(self, messages: Queue):
        """Handle incoming chat messages."""
        while not messages.empty():
            msg, addr = messages.get()
            command = msg.strip()

            # Get username
            username = self.user_names.get(addr, f"User-{addr[1]}")

            # Handle commands
            if command.startswith('/name '):
                # Set username
                new_name = command[6:].strip()
                old_name = self.user_names.get(addr, "Anonymous")
                self.user_names[addr] = new_name

                print(f"👤 {old_name} changed name to {new_name}")
                self.broadcast_message(f"*** {old_name} is now known as {new_name}")

            elif command == '/users':
                # List online users
                users = [name for name in self.user_names.values()]
                user_list = f"Online users ({len(users)}): {', '.join(users)}"

                for client in self.server._client_buffer:
                    if client.address == addr:
                        client.connection.sendall(user_list.encode())
                        break

            elif command == '/metrics':
                # Send server metrics
                metrics = self.get_metrics()
                report = [
                    "\n=== Server Metrics ===",
                    f"Uptime: {metrics['uptime']}",
                    f"Total messages: {metrics['total_messages']}",
                    f"Active users: {metrics['active_users']}",
                    f"Registered users: {metrics['registered_users']}",
                    f"Avg messages/user: {metrics['avg_messages_per_user']:.1f}",
                    "\nTop talkers:"
                ]

                # Sort users by message count
                sorted_users = sorted(
                    metrics['messages_per_user'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )

                for username, count in sorted_users[:5]:
                    report.append(f"  {username}: {count} messages")

                report.append("=" * 25)

                for client in self.server._client_buffer:
                    if client.address == addr:
                        client.connection.sendall('\n'.join(report).encode())
                        break

            elif command == '/help':
                # Show help
                help_text = """
Available commands:
  /name <name>  - Set your username
  /users        - List online users
  /metrics      - Show server metrics
  /help         - Show this help
  /quit         - Disconnect
"""
                for client in self.server._client_buffer:
                    if client.address == addr:
                        client.connection.sendall(help_text.encode())
                        break

            elif command == '/quit':
                # Disconnect user
                print(f"👋 {username} disconnected")
                self.broadcast_message(f"*** {username} left the chat", exclude_addr=addr)

                for client in self.server._client_buffer:
                    if client.address == addr:
                        client.connection.close()
                        break

            elif command.startswith('/'):
                # Unknown command
                for client in self.server._client_buffer:
                    if client.address == addr:
                        client.connection.sendall(b"Unknown command. Type /help for help.")
                        break

            else:
                # Regular message
                self.total_messages += 1
                self.messages_per_user[username] = self.messages_per_user.get(username, 0) + 1
                self.message_history.append((time.time(), username, command))

                print(f"💬 [{username}] {command}")
                self.broadcast_message(f"{username}: {command}", exclude_addr=addr)

    def start(self):
        """Start the chat server."""
        print("=" * 60)
        print("FastSocket Chat Server with Metrics")
        print("=" * 60)
        print(f"Listening on {self.config.host}:{self.config.port}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\nCommands:")
        print("  /name <name> - Set username")
        print("  /users       - List users")
        print("  /metrics     - Show metrics")
        print("  /help        - Show help")
        print("=" * 60)

        self.server.start()


if __name__ == '__main__':
    server = ChatServer(host='localhost', port=9000)
    server.start()
