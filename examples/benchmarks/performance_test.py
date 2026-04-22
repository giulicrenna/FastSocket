"""
Performance Benchmark for FastSocket

This benchmark measures throughput, latency, and overhead for different
data sizes and configurations.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import time
import statistics
from fastsocket import ChunkManager, FileTransfer
import socket
from typing import List, Tuple


class PerformanceBenchmark:
    """Benchmark suite for FastSocket components."""

    def __init__(self):
        self.results = {}

    def benchmark_chunking(self, data_sizes: List[int], chunk_sizes: List[int]):
        """Benchmark ChunkManager performance."""
        print("=" * 70)
        print("CHUNKING PERFORMANCE BENCHMARK")
        print("=" * 70)

        for chunk_size in chunk_sizes:
            manager = ChunkManager(chunk_size=chunk_size, use_headers=True)
            print(f"\nChunk Size: {chunk_size} bytes")
            print("-" * 70)

            for data_size in data_sizes:
                # Generate test data
                test_data = b'X' * data_size

                # Benchmark split
                start = time.perf_counter()
                chunks = manager.split_data(test_data)
                split_time = time.perf_counter() - start

                # Benchmark reassemble
                start = time.perf_counter()
                reassembled = manager.reassemble_chunks(chunks)
                reassemble_time = time.perf_counter() - start

                # Verify
                assert reassembled == test_data

                # Calculate stats
                num_chunks, overhead = manager.estimate_chunks(data_size)
                overhead_pct = (overhead / data_size) * 100

                print(f"\nData Size: {data_size:>10} bytes ({data_size/1024:.1f} KB)")
                print(f"  Chunks: {len(chunks):>6}")
                print(f"  Overhead: {overhead:>6} bytes ({overhead_pct:.3f}%)")
                print(f"  Split time: {split_time*1000:.3f} ms")
                print(f"  Reassemble time: {reassemble_time*1000:.3f} ms")
                print(f"  Total time: {(split_time + reassemble_time)*1000:.3f} ms")
                print(f"  Throughput: {data_size/(split_time + reassemble_time)/1024/1024:.2f} MB/s")

    def benchmark_throughput(self, iterations: int = 100):
        """Benchmark raw throughput."""
        print("\n" + "=" * 70)
        print("THROUGHPUT BENCHMARK")
        print("=" * 70)

        data_sizes = [1024, 10240, 102400, 1048576]  # 1KB to 1MB
        chunk_manager = ChunkManager(chunk_size=8192)

        for data_size in data_sizes:
            test_data = b'Y' * data_size
            times = []

            print(f"\nData Size: {data_size} bytes ({data_size/1024:.1f} KB)")
            print(f"Iterations: {iterations}")
            print("-" * 70)

            for i in range(iterations):
                start = time.perf_counter()
                chunks = chunk_manager.split_data(test_data)
                reassembled = chunk_manager.reassemble_chunks(chunks)
                elapsed = time.perf_counter() - start
                times.append(elapsed)

            # Statistics
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            std_dev = statistics.stdev(times) if len(times) > 1 else 0

            throughput_avg = data_size / avg_time / 1024 / 1024
            throughput_max = data_size / min_time / 1024 / 1024

            print(f"  Average time: {avg_time*1000:.3f} ms")
            print(f"  Min time: {min_time*1000:.3f} ms")
            print(f"  Max time: {max_time*1000:.3f} ms")
            print(f"  Std dev: {std_dev*1000:.3f} ms")
            print(f"  Average throughput: {throughput_avg:.2f} MB/s")
            print(f"  Peak throughput: {throughput_max:.2f} MB/s")

    def benchmark_overhead_analysis(self):
        """Analyze overhead for different configurations."""
        print("\n" + "=" * 70)
        print("OVERHEAD ANALYSIS")
        print("=" * 70)

        chunk_sizes = [1024, 4096, 8192, 16384, 32768]
        data_size = 1024 * 1024  # 1 MB

        print(f"\nData Size: {data_size} bytes (1 MB)")
        print("-" * 70)
        print(f"{'Chunk Size':<15} {'Chunks':<10} {'Overhead':<15} {'% Overhead':<15} {'Total':<15}")
        print("-" * 70)

        for chunk_size in chunk_sizes:
            manager = ChunkManager(chunk_size=chunk_size, use_headers=True)
            num_chunks, overhead = manager.estimate_chunks(data_size)
            overhead_pct = (overhead / data_size) * 100
            total = data_size + overhead

            print(f"{chunk_size:<15} {num_chunks:<10} {overhead:<15} {overhead_pct:<15.4f} {total:<15}")

    def benchmark_hash_computation(self):
        """Benchmark hash computation speeds."""
        print("\n" + "=" * 70)
        print("HASH COMPUTATION BENCHMARK")
        print("=" * 70)

        import hashlib
        algorithms = ['md5', 'sha1', 'sha256', 'sha512']
        data_sizes = [1024 * 100, 1024 * 1024, 10 * 1024 * 1024]  # 100KB, 1MB, 10MB

        for data_size in data_sizes:
            test_data = b'Z' * data_size
            print(f"\nData Size: {data_size/1024/1024:.2f} MB")
            print("-" * 70)

            for algo in algorithms:
                times = []
                for _ in range(10):
                    start = time.perf_counter()
                    h = hashlib.new(algo)
                    h.update(test_data)
                    digest = h.hexdigest()
                    elapsed = time.perf_counter() - start
                    times.append(elapsed)

                avg_time = statistics.mean(times)
                throughput = data_size / avg_time / 1024 / 1024

                print(f"  {algo:<10} : {avg_time*1000:>8.3f} ms  ({throughput:>8.2f} MB/s)")

    def benchmark_memory_efficiency(self):
        """Demonstrate memory-efficient iteration."""
        print("\n" + "=" * 70)
        print("MEMORY EFFICIENCY TEST")
        print("=" * 70)

        import sys
        data_size = 10 * 1024 * 1024  # 10 MB
        chunk_size = 8192

        # Method 1: Load all chunks into memory
        print("\nMethod 1: Load all chunks into memory")
        manager = ChunkManager(chunk_size=chunk_size)
        test_data = b'M' * data_size

        start = time.perf_counter()
        chunks = manager.split_data(test_data)
        memory_used = sys.getsizeof(chunks) + sum(sys.getsizeof(c) for c in chunks)
        elapsed = time.perf_counter() - start

        print(f"  Time: {elapsed*1000:.3f} ms")
        print(f"  Memory: {memory_used/1024/1024:.2f} MB")
        print(f"  Chunks in memory: {len(chunks)}")

        # Method 2: Iterator (memory efficient)
        print("\nMethod 2: Iterator (memory efficient)")
        start = time.perf_counter()
        chunk_count = 0
        for chunk in manager.iter_chunks(test_data):
            chunk_count += 1
            # Process chunk without storing all in memory
            pass
        elapsed = time.perf_counter() - start

        print(f"  Time: {elapsed*1000:.3f} ms")
        print(f"  Memory: Constant (only one chunk at a time)")
        print(f"  Chunks processed: {chunk_count}")

    def run_all_benchmarks(self):
        """Run all benchmark suites."""
        print("\n" + "=" * 70)
        print("FASTSOCKET PERFORMANCE BENCHMARKS")
        print("=" * 70)
        print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Run benchmarks
        self.benchmark_chunking(
            data_sizes=[1024, 10240, 102400, 1048576],
            chunk_sizes=[4096, 8192]
        )

        self.benchmark_throughput(iterations=100)

        self.benchmark_overhead_analysis()

        self.benchmark_hash_computation()

        self.benchmark_memory_efficiency()

        print("\n" + "=" * 70)
        print("BENCHMARKS COMPLETE")
        print("=" * 70)
        print(f"Finished at: {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == '__main__':
    benchmark = PerformanceBenchmark()
    benchmark.run_all_benchmarks()
