"""
Real-Time Metrics Monitor for FastSocket

This script monitors FastSocket server performance in real-time,
displaying metrics like throughput, active connections, message rate, etc.
"""

import time
import threading
from collections import deque
from datetime import datetime
from fastsocket import FastSocketServer, SocketConfig, Queue


class MetricsCollector:
    """Collects and tracks server metrics over time."""

    def __init__(self, window_size: int = 60):
        """
        Initialize metrics collector.

        Args:
            window_size: Number of seconds to keep in rolling window
        """
        self.window_size = window_size
        self.start_time = time.time()

        # Metrics storage (time-series with rolling window)
        self.message_timestamps = deque(maxlen=window_size * 10)  # Assume max 10 msg/s
        self.bytes_received = deque(maxlen=window_size * 10)
        self.bytes_sent = deque(maxlen=window_size * 10)
        self.connection_events = deque(maxlen=100)  # Last 100 events

        # Current stats
        self.total_messages = 0
        self.total_bytes_received = 0
        self.total_bytes_sent = 0
        self.active_connections = 0
        self.peak_connections = 0

    def record_message(self, message: str, is_incoming: bool = True):
        """Record a message event."""
        now = time.time()
        msg_bytes = len(message.encode())

        self.message_timestamps.append(now)
        self.total_messages += 1

        if is_incoming:
            self.bytes_received.append((now, msg_bytes))
            self.total_bytes_received += msg_bytes
        else:
            self.bytes_sent.append((now, msg_bytes))
            self.total_bytes_sent += msg_bytes

    def record_connection(self, event_type: str, address: tuple):
        """Record a connection event."""
        self.connection_events.append({
            'time': time.time(),
            'type': event_type,  # 'connect' or 'disconnect'
            'address': address
        })

        if event_type == 'connect':
            self.active_connections += 1
            if self.active_connections > self.peak_connections:
                self.peak_connections = self.active_connections
        elif event_type == 'disconnect':
            self.active_connections = max(0, self.active_connections - 1)

    def get_messages_per_second(self, window: int = 5) -> float:
        """Get messages per second over the last N seconds."""
        now = time.time()
        cutoff = now - window

        recent_messages = [t for t in self.message_timestamps if t >= cutoff]
        return len(recent_messages) / window if recent_messages else 0

    def get_bandwidth(self, window: int = 5) -> dict:
        """Get bandwidth (bytes/sec) over the last N seconds."""
        now = time.time()
        cutoff = now - window

        recent_received = [b for t, b in self.bytes_received if t >= cutoff]
        recent_sent = [b for t, b in self.bytes_sent if t >= cutoff]

        recv_bps = sum(recent_received) / window if recent_received else 0
        sent_bps = sum(recent_sent) / window if recent_sent else 0

        return {
            'received_bps': recv_bps,
            'sent_bps': sent_bps,
            'total_bps': recv_bps + sent_bps
        }

    def get_uptime(self) -> float:
        """Get server uptime in seconds."""
        return time.time() - self.start_time

    def get_snapshot(self) -> dict:
        """Get current metrics snapshot."""
        bandwidth = self.get_bandwidth(5)
        msg_rate = self.get_messages_per_second(5)

        return {
            'timestamp': datetime.now(),
            'uptime': self.get_uptime(),
            'total_messages': self.total_messages,
            'total_bytes_received': self.total_bytes_received,
            'total_bytes_sent': self.total_bytes_sent,
            'active_connections': self.active_connections,
            'peak_connections': self.peak_connections,
            'messages_per_second': msg_rate,
            'bandwidth_bps': bandwidth['total_bps'],
            'recv_bandwidth_bps': bandwidth['received_bps'],
            'sent_bandwidth_bps': bandwidth['sent_bps']
        }


class MonitoredServer:
    """FastSocket server with real-time metrics monitoring."""

    def __init__(self, host: str = 'localhost', port: int = 9000):
        self.config = SocketConfig(host=host, port=port)
        self.server = FastSocketServer(self.config)
        self.metrics = MetricsCollector()

        # Setup message handler
        self.server.on_new_message(self.handle_messages)

        # Monitoring
        self.monitoring = False

    def handle_messages(self, queue: Queue):
        """Handle messages and record metrics."""
        while not queue.empty():
            msg, addr = queue.get()

            # Record incoming message
            self.metrics.record_message(msg, is_incoming=True)

            # Echo back (for demo)
            response = f"Echo: {msg}"
            for client in self.server._client_buffer:
                if client.address == addr and client.connected:
                    client.connection.sendall(response.encode())
                    self.metrics.record_message(response, is_incoming=False)
                    break

    def display_metrics_dashboard(self):
        """Display real-time metrics dashboard."""
        import os

        while self.monitoring:
            # Clear screen (works on Unix/Linux/Mac)
            os.system('clear' if os.name != 'nt' else 'cls')

            snapshot = self.metrics.get_snapshot()

            # Header
            print("=" * 80)
            print(f"{'FASTSOCKET REAL-TIME METRICS DASHBOARD':^80}")
            print("=" * 80)
            print(f"Time: {snapshot['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Uptime: {snapshot['uptime']:.1f}s")
            print("=" * 80)

            # Connection metrics
            print("\nCONNECTION METRICS")
            print("-" * 80)
            print(f"  Active connections: {snapshot['active_connections']:>10}")
            print(f"  Peak connections:   {snapshot['peak_connections']:>10}")

            # Traffic metrics
            print("\nTRAFFIC METRICS")
            print("-" * 80)
            print(f"  Total messages:     {snapshot['total_messages']:>10,}")
            print(f"  Messages/sec (5s):  {snapshot['messages_per_second']:>10.2f}")

            # Bandwidth metrics
            print("\nBANDWIDTH METRICS (5-second average)")
            print("-" * 80)
            print(f"  Received:   {snapshot['recv_bandwidth_bps']:>10.2f} bytes/s  "
                  f"({snapshot['recv_bandwidth_bps']/1024:>8.2f} KB/s)")
            print(f"  Sent:       {snapshot['sent_bandwidth_bps']:>10.2f} bytes/s  "
                  f"({snapshot['sent_bandwidth_bps']/1024:>8.2f} KB/s)")
            print(f"  Total:      {snapshot['bandwidth_bps']:>10.2f} bytes/s  "
                  f"({snapshot['bandwidth_bps']/1024:>8.2f} KB/s)")

            # Cumulative data
            print("\nCUMULATIVE DATA")
            print("-" * 80)
            print(f"  Total received: {snapshot['total_bytes_received']:>15,} bytes  "
                  f"({snapshot['total_bytes_received']/1024/1024:>8.2f} MB)")
            print(f"  Total sent:     {snapshot['total_bytes_sent']:>15,} bytes  "
                  f"({snapshot['total_bytes_sent']/1024/1024:>8.2f} MB)")

            # Graphs (simple text-based)
            print("\nMESSAGE RATE GRAPH (last 10 seconds)")
            print("-" * 80)
            self.display_rate_graph()

            print("\n" + "=" * 80)
            print("Press Ctrl+C to stop monitoring")
            print("=" * 80)

            time.sleep(1)  # Update every second

    def display_rate_graph(self):
        """Display a simple text-based graph of message rate."""
        # Get message rates for last 10 seconds
        rates = []
        for i in range(10, 0, -1):
            rate = self.metrics.get_messages_per_second(window=1)
            rates.append(rate)

        if not rates or max(rates) == 0:
            print("  (no data)")
            return

        # Normalize to fit in 40 character height
        max_rate = max(rates)
        scale = 40 / max_rate if max_rate > 0 else 1

        # Print graph
        for i, rate in enumerate(rates):
            bar_length = int(rate * scale)
            bar = '█' * bar_length
            print(f"  {10-i:2d}s ago: {bar} {rate:.1f} msg/s")

    def start(self):
        """Start the monitored server."""
        print("=" * 80)
        print("FastSocket Server with Real-Time Metrics")
        print("=" * 80)
        print(f"Starting server on {self.config.host}:{self.config.port}")
        print("Metrics will be displayed in real-time...")
        print("=" * 80)

        # Start server in background
        server_thread = threading.Thread(target=self.server.run, daemon=True)
        server_thread.start()

        time.sleep(1)  # Wait for server to start

        # Start monitoring
        self.monitoring = True
        try:
            self.display_metrics_dashboard()
        except KeyboardInterrupt:
            print("\n\nStopping server...")
            self.monitoring = False

        # Final stats
        print("\n" + "=" * 80)
        print("FINAL STATISTICS")
        print("=" * 80)
        snapshot = self.metrics.get_snapshot()
        print(f"Total runtime: {snapshot['uptime']:.1f}s")
        print(f"Total messages: {snapshot['total_messages']:,}")
        print(f"Peak connections: {snapshot['peak_connections']}")
        print(f"Total data: {(snapshot['total_bytes_received'] + snapshot['total_bytes_sent'])/1024/1024:.2f} MB")
        print("=" * 80)


if __name__ == '__main__':
    server = MonitoredServer(host='localhost', port=9000)
    server.start()
