"""
ChunkManager Standalone Demo

This example demonstrates ChunkManager functionality without networking.
Shows chunking, reassembly, iteration, and estimation features.
"""

from FastSocket import ChunkManager

def demo_basic_chunking():
    """Demonstrate basic chunking and reassembly."""
    print('\n' + '='*60)
    print('1. Basic Chunking and Reassembly')
    print('='*60)

    manager = ChunkManager(chunk_size=1024)

    # Create test data
    test_data = b'Hello World! ' * 500  # ~6.5KB
    print(f'Original data: {len(test_data)} bytes')

    # Split into chunks
    chunks = manager.split_data(test_data)
    print(f'Split into: {len(chunks)} chunks')
    print(f'Chunk sizes: {[len(c) for c in chunks]}')

    # Reassemble
    reassembled = manager.reassemble_chunks(chunks)
    print(f'Reassembled: {len(reassembled)} bytes')
    print(f'Data intact: {reassembled == test_data}')

def demo_chunk_iteration():
    """Demonstrate chunk iteration for memory-efficient processing."""
    print('\n' + '='*60)
    print('2. Chunk Iteration (Memory Efficient)')
    print('='*60)

    manager = ChunkManager(chunk_size=512)
    large_data = b'X' * 5000

    print(f'Processing {len(large_data)} bytes in chunks...')

    chunk_count = 0
    for chunk in manager.iter_chunks(large_data):
        chunk_count += 1
        # Process each chunk individually (memory efficient)
        # print(f'  Chunk {chunk_count}: {len(chunk)} bytes')

    print(f'Processed {chunk_count} chunks without loading all into memory')

def demo_estimation():
    """Demonstrate chunk estimation for planning transfers."""
    print('\n' + '='*60)
    print('3. Transfer Estimation')
    print('='*60)

    manager = ChunkManager(chunk_size=4096, use_headers=True)

    # Estimate different data sizes
    sizes = [1024, 10240, 102400, 1048576, 10485760]  # 1KB to 10MB

    print(f'Chunk size: {manager.chunk_size} bytes')
    print(f'Header size: {manager._header_size} bytes per chunk\n')

    for size in sizes:
        num_chunks, overhead = manager.estimate_chunks(size)
        total = size + overhead
        overhead_pct = (overhead / size) * 100

        print(f'Data size: {size:>10} bytes ({size/1024:>8.2f} KB)')
        print(f'  Chunks: {num_chunks:>5}')
        print(f'  Overhead: {overhead:>6} bytes ({overhead_pct:>5.2f}%)')
        print(f'  Total: {total:>10} bytes\n')

def demo_with_without_headers():
    """Compare headerless vs header-based chunking."""
    print('\n' + '='*60)
    print('4. Header vs Headerless Mode')
    print('='*60)

    test_data = b'Test data ' * 100  # ~1KB

    # With headers
    manager_headers = ChunkManager(chunk_size=256, use_headers=True)
    chunks_h, overhead_h = manager_headers.estimate_chunks(len(test_data))

    # Without headers
    manager_no_headers = ChunkManager(chunk_size=256, use_headers=False)
    chunks_nh, overhead_nh = manager_no_headers.estimate_chunks(len(test_data))

    print(f'Data size: {len(test_data)} bytes\n')

    print('WITH HEADERS (recommended):')
    print(f'  - Chunks: {chunks_h}')
    print(f'  - Overhead: {overhead_h} bytes')
    print(f'  - Automatic termination detection')
    print(f'  - Safer for arbitrary data sizes\n')

    print('WITHOUT HEADERS:')
    print(f'  - Chunks: {chunks_nh}')
    print(f'  - Overhead: {overhead_nh} bytes')
    print(f'  - Must know data size in advance')
    print(f'  - Slightly less bandwidth')

def demo_string_vs_bytes():
    """Show handling of both string and bytes."""
    print('\n' + '='*60)
    print('5. String vs Bytes Handling')
    print('='*60)

    manager = ChunkManager(chunk_size=100)

    # String input
    string_data = 'Hello World! ' * 50
    string_chunks = manager.split_data(string_data)
    print(f'String input: {len(string_data)} chars → {len(string_chunks)} chunks')
    print(f'  First chunk type: {type(string_chunks[0])}')

    # Bytes input
    bytes_data = b'Hello World! ' * 50
    bytes_chunks = manager.split_data(bytes_data)
    print(f'Bytes input: {len(bytes_data)} bytes → {len(bytes_chunks)} chunks')
    print(f'  First chunk type: {type(bytes_chunks[0])}')

    print('\nBoth are converted to bytes internally for transmission')

if __name__ == '__main__':
    print('\n' + '='*60)
    print(' ChunkManager Demonstration')
    print('='*60)

    demo_basic_chunking()
    demo_chunk_iteration()
    demo_estimation()
    demo_with_without_headers()
    demo_string_vs_bytes()

    print('\n' + '='*60)
    print(' Demo Complete!')
    print('='*60)
    print()
