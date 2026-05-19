import os
import hashlib
import struct
import time

class MPPEngine:
    def __init__(self, block_size=16):
        self.block_size = block_size
        self.library = {} # hash -> binary data
        self.library_ordered = [] # list of binary data for indexing
        self.puzzle_map = [] # list of library indices

    def _reset(self):
        self.library = {}
        self.library_ordered = []
        self.puzzle_map = []

    def compress(self, input_path, output_path):
        self._reset()
        if not os.path.exists(input_path):
            return "Error: Input file not found."

        print(f"[MPP] Ingesting: {input_path} (Block Size: {self.block_size}B)")
        with open(input_path, 'rb') as f:
            raw_data = f.read()

        file_size = len(raw_data)
        
        # Partitioning and Dictionary Building
        start_time = time.time()
        for i in range(0, file_size, self.block_size):
            block = raw_data[i : i + self.block_size]
            block_hash = hashlib.md5(block).digest() # MD5 is faster than SHA256 for internal mapping

            if block_hash not in self.library:
                self.library[block_hash] = len(self.library_ordered)
                self.library_ordered.append(block)
            
            self.puzzle_map.append(self.library[block_hash])

        # Binary Packaging
        # Header: block_size (I), original_size (Q), library_count (I), map_count (I)
        header_format = '<IQQI'
        header = struct.pack(header_format, self.block_size, file_size, len(self.library_ordered), len(self.puzzle_map))

        with open(output_path, 'wb') as f:
            f.write(header)
            
            # Write the Library (The Dictionary of Pieces)
            for piece in self.library_ordered:
                # We need to store the actual length of the piece because the last piece might be shorter
                f.write(struct.pack('<B', len(piece)))
                f.write(piece)

            # Write the Puzzle Map (The Indices)
            # Use 'H' (unsigned short, max 65k) or 'I' (unsigned int) depending on library size
            if len(self.library_ordered) < 65535:
                index_format = '<H'
            else:
                index_format = '<I'
            
            for index in self.puzzle_map:
                f.write(struct.pack(index_format, index))

        duration = time.time() - start_time
        orig_size = os.path.getsize(input_path)
        new_size = os.path.getsize(output_path)
        reduction = (1 - (new_size / orig_size)) * 100 if orig_size > 0 else 0

        print(f"[MPP] Compression Complete in {duration:.2f}s")
        print(f"[MPP] Original Mass: {orig_size} bytes")
        print(f"[MPP] Puzzle Mass:   {new_size} bytes")
        print(f"[MPP] Reduction:     {reduction:.2f}%")
        
        return {
            "original_size": orig_size,
            "compressed_size": new_size,
            "reduction": reduction,
            "duration": duration
        }

    def decompress(self, input_path, output_path):
        print(f"[MPP] Unfolding: {input_path}")
        with open(input_path, 'rb') as f:
            # Read Header
            header_format = '<IQQI'
            header_size = struct.calcsize(header_format)
            block_size, original_size, library_count, map_count = struct.unpack(header_format, f.read(header_size))

            # Read Library
            library = []
            for _ in range(library_count):
                piece_len = struct.unpack('<B', f.read(1))[0]
                library.append(f.read(piece_len))

            # Read Map
            puzzle_map = []
            if library_count < 65535:
                index_format = '<H'
            else:
                index_format = '<I'
            
            index_size = struct.calcsize(index_format)
            for _ in range(map_count):
                index = struct.unpack(index_format, f.read(index_size))[0]
                puzzle_map.append(index)

        # Reconstruction
        with open(output_path, 'wb') as f:
            for index in puzzle_map:
                f.write(library[index])

        print(f"[MPP] Restoration Complete: {output_path}")

if __name__ == "__main__":
    import sys
    engine = MPPEngine(block_size=16)
    
    # Simple Benchmark Test
    test_file = "benchmark_test.txt"
    compressed_file = "benchmark_test.mpp"
    restored_file = "benchmark_restored.txt"
    
    # Create a repetitive test file
    content = b"ABCDEFGH12345678" * 1000 # 16KB of repetitive data
    with open(test_file, 'wb') as f:
        f.write(content)
    
    output_filepath = compressed_file # Local var for the script logic
    engine.compress(test_file, compressed_file)
    engine.decompress(compressed_file, restored_file)
    
    # Verification
    with open(test_file, 'rb') as f1, open(restored_file, 'rb') as f2:
        if f1.read() == f2.read():
            print("\n[VERIFICATION] 100% BIT-PERFECT PARITY ATTAINED.")
        else:
            print("\n[VERIFICATION] FAILED. DATA CORRUPTION DETECTED.")
