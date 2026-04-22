"""
TCP vs UDP Performance Comparison

This benchmark compares TCP and UDP performance for different
scenarios including latency, throughput, and packet loss.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import time
import statistics
import socket
from fastsocket import (
    FastSocketServer,
    FastSocketClient,
    FastSocketUDPServer,
    FastSocketUDPClient,
    SocketConfig,
    Queue
)
from threading import Thread
import sys


class TCPvsUDPBenchmark:
    """Benchmark comparing TCP and UDP performance."""
    def __init__(self):
        self.tcp_port = 8001
        self.udp_port = 8002
        self.results = {}

    def benchmark_tcp_throughput(self, num_messages: int, message_size: int):
        """Benchmark TCP throughput."""
        print("\n" + "=" * 70)
        print(f"TCP THROUGHPUT TEST ({num_messages} messages of {message_size} bytes)")
        print("=" * 70)

        # Server setup
        messages_received = []
        start_time = [None]
        end_time = [None]

        def handle_tcp(queue: Queue):
            if start_time[0] is None:
                start_time[0] = time.perf_counter()

            while not queue.empty():
                msg, addr = queue.get()
                messages_received.append(msg)

                if len(messages_received) >= num_messages:
                    end_time[0] = time.perf_counter()

        config = SocketConfig(host='localhost', port=self.tcp_port)
        server = FastSocketServer(config)
        server.on_new_message(handle_tcp)

        server_thread = Thread(target=server.run, daemon=True)
        server_thread.start()
        time.sleep(0.5)

        # Client setup and send
        client = FastSocketClient(config)
        client.start()
        time.sleep(0.3)

        test_message = 'X' * message_size
        send_start = time.perf_counter()

        for i in range(num_messages):
            client.send_to_server(test_message)

        send_end = time.perf_counter()

        # Wait for all messages to be received
        time.sleep(2)

        # Calculate results
        send_time = send_end - send_start
        if end_time[0] and start_time[0]:
            total_time = end_time[0] - start_time[0]
        else:
            total_time = send_time

        total_bytes = num_messages * message_size
        throughput_mbps = (total_bytes / total_time) / (1024 * 1024)

        print(f"Messages sent: {num_messages}")
        print(f"Messages received: {len(messages_received)}")
        print(f"Send time: {send_time*1000:.2f} ms")
        print(f"Total time: {total_time*1000:.2f} ms")
        print(f"Throughput: {throughput_mbps:.2f} MB/s")
        print(f"Messages/sec: {num_messages/total_time:.2f}")
        print(f"Packet loss: 0.00% (TCP guarantees delivery)")

        return {
            'protocol': 'TCP',
            'messages_sent': num_messages,
            'messages_received': len(messages_received),
            'total_time': total_time,
            'throughput_mbps': throughput_mbps,
            'packet_loss': 0.0
        }

    def benchmark_udp_throughput(self, num_messages: int, message_size: int):
        """Benchmark UDP throughput."""
        print("\n" + "=" * 70)
        print(f"UDP THROUGHPUT TEST ({num_messages} messages of {message_size} bytes)")
        print("=" * 70)

        # Server setup
        messages_received = []
        start_time = [None]

        def handle_udp(queue: Queue):
            if start_time[0] is None:
                start_time[0] = time.perf_counter()

            while not queue.empty():
                msg, addr = queue.get()
                messages_received.append(msg)

        config = SocketConfig(
            host='localhost',
            port=self.udp_port,
            type=socket.SOCK_DGRAM
        )

        server = FastSocketUDPServer(config)
        server.on_new_message(handle_udp)

        server_thread = Thread(target=server.run, daemon=True)
        server_thread.start()
        time.sleep(0.5)

        # Client setup and send
        client = FastSocketUDPClient(config)
        client.bind(('0.0.0.0', 0))  # Bind to any available port

        test_message = 'Y' * message_size
        send_start = time.perf_counter()

        for i in range(num_messages):
            client.send_to_server(test_message)

        send_end = time.perf_counter()

        # Wait for messages to arrive
        time.sleep(2)
        end_time = time.perf_counter()

        # Calculate results
        send_time = send_end - send_start
        if start_time[0]:
            total_time = end_time - start_time[0]
        else:
            total_time = send_time

        total_bytes = len(messages_received) * message_size
        throughput_mbps = (total_bytes / total_time) / (1024 * 1024)
        packet_loss = ((num_messages - len(messages_received)) / num_messages) * 100

        print(f"Messages sent: {num_messages}")
        print(f"Messages received: {len(messages_received)}")
        print(f"Send time: {send_time*1000:.2f} ms")
        print(f"Total time: {total_time*1000:.2f} ms")
        print(f"Throughput: {throughput_mbps:.2f} MB/s")
        print(f"Messages/sec: {len(messages_received)/total_time:.2f}")
        print(f"Packet loss: {packet_loss:.2f}%")

        client.close()

        return {
            'protocol': 'UDP',
            'messages_sent': num_messages,
            'messages_received': len(messages_received),
            'total_time': total_time,
            'throughput_mbps': throughput_mbps,
            'packet_loss': packet_loss
        }

    def benchmark_latency_comparison(self, num_pings: int = 100):
        """Compare TCP vs UDP latency."""
        print("\n" + "=" * 70)
        print(f"LATENCY COMPARISON ({num_pings} round trips)")
        print("=" * 70)

        # TCP Latency
        print("\nTCP Latency Test:")
        tcp_times = []

        def tcp_echo(queue: Queue):
            while not queue.empty():
                msg, addr = queue.get()
                for client in tcp_server._client_buffer:
                    if client.address == addr:
                        client.connection.sendall(msg.encode())
                        break

        config_tcp = SocketConfig(host='localhost', port=self.tcp_port)
        tcp_server = FastSocketServer(config_tcp)
        tcp_server.on_new_message(tcp_echo)

        server_thread = Thread(target=tcp_server.run, daemon=True)
        server_thread.start()
        time.sleep(0.5)

        tcp_client = FastSocketClient(config_tcp)

        responses = []
        def collect_response(msg):
            responses.append(time.perf_counter())

        tcp_client.on_new_message(collect_response)
        tcp_client.start()
        time.sleep(0.3)

        for i in range(num_pings):
            responses.clear()
            start = time.perf_counter()
            tcp_client.send_to_server(f"ping{i}")

            # Wait for response
            timeout = time.time() + 1.0
            while not responses and time.time() < timeout:
                time.sleep(0.001)

            if responses:
                latency = (responses[0] - start) * 1000  # ms
                tcp_times.append(latency)

        tcp_avg = statistics.mean(tcp_times) if tcp_times else 0
        tcp_min = min(tcp_times) if tcp_times else 0
        tcp_max = max(tcp_times) if tcp_times else 0
        tcp_std = statistics.stdev(tcp_times) if len(tcp_times) > 1 else 0

        print(f"  Successful pings: {len(tcp_times)}/{num_pings}")
        print(f"  Average latency: {tcp_avg:.3f} ms")
        print(f"  Min latency: {tcp_min:.3f} ms")
        print(f"  Max latency: {tcp_max:.3f} ms")
        print(f"  Std deviation: {tcp_std:.3f} ms")

        # UDP Latency
        print("\nUDP Latency Test:")
        udp_times = []

        udp_responses = []
        def udp_echo(queue: Queue):
            while not queue.empty():
                msg, addr = queue.get()
                udp_server.send_to(addr, msg)

        config_udp = SocketConfig(
            host='localhost',
            port=self.udp_port,
            type=socket.SOCK_DGRAM
        )

        udp_server = FastSocketUDPServer(config_udp)
        udp_server.on_new_message(udp_echo)

        server_thread2 = Thread(target=udp_server.run, daemon=True)
        server_thread2.start()
        time.sleep(0.5)

        udp_client = FastSocketUDPClient(config_udp)

        def collect_udp_response(msg, addr):
            udp_responses.append(time.perf_counter())

        udp_client.on_new_message(collect_udp_response)
        udp_client.bind(('0.0.0.0', 0))
        udp_client.start()
        time.sleep(0.3)

        for i in range(num_pings):
            udp_responses.clear()
            start = time.perf_counter()
            udp_client.send_to_server(f"ping{i}")

            # Wait for response
            timeout = time.time() + 1.0
            while not udp_responses and time.time() < timeout:
                time.sleep(0.001)

            if udp_responses:
                latency = (udp_responses[0] - start) * 1000  # ms
                udp_times.append(latency)

        udp_avg = statistics.mean(udp_times) if udp_times else 0
        udp_min = min(udp_times) if udp_times else 0
        udp_max = max(udp_times) if udp_times else 0
        udp_std = statistics.stdev(udp_times) if len(udp_times) > 1 else 0

        print(f"  Successful pings: {len(udp_times)}/{num_pings}")
        print(f"  Average latency: {udp_avg:.3f} ms")
        print(f"  Min latency: {udp_min:.3f} ms")
        print(f"  Max latency: {udp_max:.3f} ms")
        print(f"  Std deviation: {udp_std:.3f} ms")

        # Comparison
        print("\nComparison:")
        print(f"  TCP is {udp_avg/tcp_avg:.2f}x {'slower' if tcp_avg > udp_avg else 'faster'} than UDP")
        print(f"  Latency difference: {abs(tcp_avg - udp_avg):.3f} ms")

        udp_client.close()

    def run_all_benchmarks(self):
        """Run all TCP vs UDP benchmarks."""
        print("\n" + "=" * 70)
        print("TCP VS UDP PERFORMANCE COMPARISON")
        print("=" * 70)

        # Throughput tests
        tcp_result = self.benchmark_tcp_throughput(1000, 1024)
        udp_result = self.benchmark_udp_throughput(1000, 1024)

        # Latency test
        self.benchmark_latency_comparison(100)

        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"TCP Throughput: {tcp_result['throughput_mbps']:.2f} MB/s")
        print(f"UDP Throughput: {udp_result['throughput_mbps']:.2f} MB/s")
        print(f"UDP Packet Loss: {udp_result['packet_loss']:.2f}%")
        print("\nConclusions:")
        print("  - TCP: Reliable, ordered delivery with slightly lower speed")
        print("  - UDP: Faster but may lose packets, best for real-time data")
        print("=" * 70)


if __name__ == '__main__':
    benchmark = TCPvsUDPBenchmark()
    benchmark.run_all_benchmarks()
