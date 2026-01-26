"""
Load Testing and Stress Test for FastSocket

This script performs stress testing on FastSocket servers to measure
performance under high load, concurrent connections, and sustained traffic.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import time
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from FastSocket import FastSocketServer, FastSocketClient, SocketConfig, Queue


class LoadTester:
    """Load testing suite for FastSocket."""

    def __init__(self, host: str = 'localhost', port: int = 8000):
        self.host = host
        self.port = port
        self.results = []
        self.errors = []
        self.server = None
        self.server_thread = None

    def start_server(self):
        """Start the shared echo server for testing."""
        if self.server is not None:
            return  # Already started

        def echo_handler(queue: Queue):
            while not queue.empty():
                msg, addr = queue.get()
                for client in self.server._client_buffer:
                    if client.address == addr and client.connected:
                        try:
                            client.connection.sendall(msg.encode())
                        except:
                            pass
                        break

        config = SocketConfig(host=self.host, port=self.port)
        self.server = FastSocketServer(config)
        self.server.on_new_message(echo_handler)

        # Run server in background thread
        self.server_thread = threading.Thread(target=self.server.run, daemon=True)
        self.server_thread.start()
        time.sleep(1)  # Give server time to start

    def stop_server(self):
        """Stop the shared server."""
        if self.server and self.server.sock:
            try:
                self.server.sock.close()
            except:
                pass
        self.server = None
        self.server_thread = None

    def setup_echo_server(self):
        """Setup a simple echo server for testing (deprecated - use start_server)."""
        return self.start_server()

    def single_client_test(self, client_id: int, num_messages: int, message_size: int) -> dict:
        """Test a single client sending multiple messages."""
        config = SocketConfig(host=self.host, port=self.port)
        client = FastSocketClient(config)

        responses = []
        response_times = []

        def handle_response(msg):
            responses.append(msg)

        client.on_new_message(handle_response)

        try:
            # Connect
            connect_start = time.perf_counter()
            client.start()
            time.sleep(0.1)  # Wait for connection
            connect_time = time.perf_counter() - connect_start

            # Send messages and measure response times
            test_message = 'X' * message_size
            send_times = []

            for i in range(num_messages):
                responses.clear()
                start = time.perf_counter()
                client.send_to_server(f"{test_message}_{i}")

                # Wait for echo
                timeout = time.time() + 5.0
                while len(responses) == 0 and time.time() < timeout:
                    time.sleep(0.001)

                if responses:
                    response_time = (time.perf_counter() - start) * 1000
                    response_times.append(response_time)

                send_times.append(time.perf_counter() - start)

            # Calculate statistics
            success_rate = (len(response_times) / num_messages) * 100
            avg_response_time = statistics.mean(response_times) if response_times else 0
            min_response_time = min(response_times) if response_times else 0
            max_response_time = max(response_times) if response_times else 0

            return {
                'client_id': client_id,
                'success': True,
                'connect_time': connect_time,
                'messages_sent': num_messages,
                'messages_received': len(response_times),
                'success_rate': success_rate,
                'avg_response_time': avg_response_time,
                'min_response_time': min_response_time,
                'max_response_time': max_response_time
            }

        except Exception as e:
            return {
                'client_id': client_id,
                'success': False,
                'error': str(e)
            }

    def concurrent_connections_test(self, num_clients: int, messages_per_client: int, message_size: int):
        """Test multiple concurrent client connections."""
        print("\n" + "=" * 70)
        print(f"CONCURRENT CONNECTIONS TEST")
        print("=" * 70)
        print(f"Clients: {num_clients}")
        print(f"Messages per client: {messages_per_client}")
        print(f"Message size: {message_size} bytes")
        print("-" * 70)

        # Run concurrent clients
        start_time = time.perf_counter()

        with ThreadPoolExecutor(max_workers=num_clients) as executor:
            futures = []
            for i in range(num_clients):
                future = executor.submit(
                    self.single_client_test,
                    i,
                    messages_per_client,
                    message_size
                )
                futures.append(future)

            # Collect results
            results = []
            for future in as_completed(futures):
                result = future.result()
                results.append(result)

                if result['success']:
                    status = "OK"
                else:
                    status = "FAIL"

                print(f"  Client {result['client_id']:>3}: {status}")

        total_time = time.perf_counter() - start_time

        # Analyze results
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]

        if successful:
            avg_connect_time = statistics.mean([r['connect_time'] for r in successful])
            avg_response_time = statistics.mean([r['avg_response_time'] for r in successful])
            total_messages = sum([r['messages_sent'] for r in successful])
            total_received = sum([r['messages_received'] for r in successful])
            overall_success_rate = (total_received / total_messages) * 100 if total_messages > 0 else 0

            print("\n" + "-" * 70)
            print("RESULTS:")
            print(f"  Total time: {total_time:.2f}s")
            print(f"  Successful clients: {len(successful)}/{num_clients}")
            print(f"  Failed clients: {len(failed)}")
            print(f"  Avg connect time: {avg_connect_time*1000:.2f} ms")
            print(f"  Avg response time: {avg_response_time:.2f} ms")
            print(f"  Total messages sent: {total_messages:,}")
            print(f"  Total messages received: {total_received:,}")
            print(f"  Overall success rate: {overall_success_rate:.2f}%")
            print(f"  Throughput: {total_messages/total_time:.2f} msg/s")

        return results

    def sustained_load_test(self, duration_seconds: int, messages_per_second: int):
        """Test sustained load over time."""
        print("\n" + "=" * 70)
        print(f"SUSTAINED LOAD TEST")
        print("=" * 70)
        print(f"Duration: {duration_seconds}s")
        print(f"Target rate: {messages_per_second} msg/s")
        print("-" * 70)

        # Setup client
        config = SocketConfig(host=self.host, port=self.port)
        client = FastSocketClient(config)

        responses = []
        def handle_response(msg):
            responses.append(time.time())

        client.on_new_message(handle_response)
        client.start()
        time.sleep(0.3)

        # Send messages at target rate
        start_time = time.time()
        messages_sent = 0
        interval = 1.0 / messages_per_second

        print("\nSending messages (press Ctrl+C to stop)...")

        try:
            while (time.time() - start_time) < duration_seconds:
                send_time = time.time()

                client.send_to_server(f"msg_{messages_sent}")
                messages_sent += 1

                # Sleep to maintain rate
                elapsed = time.time() - send_time
                sleep_time = max(0, interval - elapsed)
                time.sleep(sleep_time)

                # Progress update every second
                if messages_sent % messages_per_second == 0:
                    elapsed_total = time.time() - start_time
                    actual_rate = messages_sent / elapsed_total
                    print(f"  {elapsed_total:.0f}s: {messages_sent} sent, {len(responses)} recv, {actual_rate:.1f} msg/s")

        except KeyboardInterrupt:
            print("\nStopped by user")

        total_time = time.time() - start_time

        # Results
        print("\n" + "-" * 70)
        print("RESULTS:")
        print(f"  Duration: {total_time:.2f}s")
        print(f"  Messages sent: {messages_sent:,}")
        print(f"  Messages received: {len(responses):,}")
        print(f"  Actual send rate: {messages_sent/total_time:.2f} msg/s")
        print(f"  Success rate: {(len(responses)/messages_sent*100):.2f}%")

    def memory_leak_test(self, num_iterations: int = 1000):
        """Test for memory leaks over many iterations."""
        print("\n" + "=" * 70)
        print(f"MEMORY LEAK TEST")
        print("=" * 70)
        print(f"Iterations: {num_iterations}")
        print("-" * 70)

        import gc
        import psutil
        import os

        process = psutil.Process(os.getpid())

        # Get initial memory
        gc.collect()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        print(f"\nInitial memory: {initial_memory:.2f} MB")

        # Run iterations
        for i in range(num_iterations):
            # Create client, send message, disconnect
            config = SocketConfig(host=self.host, port=self.port)
            client = FastSocketClient(config)

            responses = []
            client.on_new_message(lambda msg: responses.append(msg))

            client.start()
            time.sleep(0.01)

            client.send_to_server(f"test_{i}")
            time.sleep(0.01)

            # Client will be garbage collected

            if (i + 1) % 100 == 0:
                gc.collect()
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_increase = current_memory - initial_memory
                print(f"  Iteration {i+1}: {current_memory:.2f} MB (+{memory_increase:.2f} MB)")

        # Final memory check
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory

        print("\n" + "-" * 70)
        print("RESULTS:")
        print(f"  Initial memory: {initial_memory:.2f} MB")
        print(f"  Final memory: {final_memory:.2f} MB")
        print(f"  Memory increase: {memory_increase:.2f} MB")
        print(f"  Per iteration: {memory_increase/num_iterations*1024:.2f} KB")

        if memory_increase < 10:  # Less than 10 MB increase
            print("  ✓ No significant memory leak detected")
        else:
            print("  ⚠ Possible memory leak detected")

    def run_all_tests(self):
        """Run all load tests."""
        print("\n" + "=" * 70)
        print("FASTSOCKET LOAD TESTING SUITE")
        print("=" * 70)

        # Start shared server
        self.start_server()

        try:
            # Test 1: Concurrent connections
            self.concurrent_connections_test(
                num_clients=50,
                messages_per_client=10,
                message_size=1024
            )

            # Test 2: Sustained load
            self.sustained_load_test(
                duration_seconds=10,
                messages_per_second=100
            )

            # Test 3: Memory leak test (if psutil available)
            try:
                import psutil
                self.memory_leak_test(num_iterations=500)
            except ImportError:
                print("\nSkipping memory leak test (psutil not installed)")

        finally:
            # Stop server
            self.stop_server()

        print("\n" + "=" * 70)
        print("ALL TESTS COMPLETE")
        print("=" * 70)


if __name__ == '__main__':
    tester = LoadTester(host='localhost', port=8000)
    tester.run_all_tests()
