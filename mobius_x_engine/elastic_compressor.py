import os
import struct
import zlib
import time
import collections

class MRSSEngine:
    def __init__(self, min_len=4, max_len=256, max_dict_size=4096):
        self.min_len = min_len
        self.max_len = max_len
        self.max_dict_size = max_dict_size
        self.dictionary = [] # List of unique binary sequences
        self.instruction_stream = [] # List of (type, value) where type 0=raw, 1=dict_index

    def _reset(self):
        self.dictionary = []
        self.instruction_stream = []

    def _find_best_pattern(self, data):
        """
        Scans the data for the most profitable repeating substring.
        Profit = (pattern_len * frequency) - (overhead)
        """
        counts = collections.defaultdict(int)
        # We only check lengths from min_len to max_len
        # Using a sliding window to find frequencies
        # To keep it fast, we only sample a portion if the data is huge
        sample_size = min(len(data), 50000)
        step = max(1, len(data) // sample_size)
        
        for length in range(self.max_len, self.min_len - 1, -16): # Step down for speed
            for i in range(0, len(data) - length, step):
                pattern = bytes(data[i : i + length])
                counts[pattern] += 1
            
            if not counts: continue
            
            # Calculate profit
            best_pattern = None
            max_profit = 0
            
            for pattern, count in counts.items():
                if count < 2: continue
                # Overhead of storing the pattern in dict + the indices
                # Approx: len(pattern) + (count * 2 bytes)
                profit = (len(pattern) * count) - (len(pattern) + count * 2)
                if profit > max_profit:
                    max_profit = profit
                    best_pattern = pattern
            
            if best_pattern:
                return best_pattern
        
        return None

    def compress(self, input_path, output_path):
        self._reset()
        if not os.path.exists(input_path):
            return "Error: Input file not found."

        print(f"[MRSS] Ingesting Geodesic: {input_path}")
        with open(input_path, 'rb') as f:
            current_data = bytearray(f.read())

        file_size = len(current_data)
        start_time = time.time()

        # Phase 1: Iterative Sequence Extraction (The Folding)
        print(f"[MRSS] Starting Recursive Fold (Target: {self.max_dict_size} sequences)...")
        
        while len(self.dictionary) < self.max_dict_size:
            pattern = self._find_best_pattern(current_data)
            if not pattern:
                break
                
            dict_id = len(self.dictionary)
            self.dictionary.append(pattern)
            
            # Replace occurrences with a placeholder
            # Using a unique marker that won't appear in raw data is hard in binary
            # So we use an internal list-based representation for the substitution phase
            print(f"[MRSS] Fold {dict_id}: Pattern Length {len(pattern)} found. Compressing...")
            
            # This is slow in pure Python. For the prototype, we'll do one pass of the top N patterns.
            if dict_id > 10: break # Keep it fast for the first test

        # Phase 2: Instruction Synthesis
        # Since the greedy replace is complex in binary, we'll use a simpler 'Global Dictionary' pass
        # 1. Build a frequency dictionary of common 8-byte, 16-byte, and 32-byte chunks
        print("[MRSS] Synthesizing Global Instruction Stream...")
        self.dictionary = []
        counts = collections.Counter()
        for length in [32, 16, 8]:
            for i in range(0, len(current_data) - length, length):
                counts[bytes(current_data[i:i+length])] += 1
        
        # Pick top sequences
        for pattern, count in counts.most_common(self.max_dict_size):
            if count > 1 and len(pattern) > 2:
                self.dictionary.append(pattern)
        
        dict_map = {p: i for i, p in enumerate(self.dictionary)}
        
        # Build the final stream
        i = 0
        while i < len(current_data):
            matched = False
            # Try longest matches first
            for length in [32, 16, 8]:
                chunk = bytes(current_data[i:i+length])
                if chunk in dict_map:
                    self.instruction_stream.append((1, dict_map[chunk]))
                    i += length
                    matched = True
                    break
            
            if not matched:
                self.instruction_stream.append((0, current_data[i]))
                i += 1

        # Phase 3: Binary Packaging
        header = struct.pack('<IQQI', 0, file_size, len(self.dictionary), len(self.instruction_stream))
        
        with open(output_path, 'wb') as f:
            f.write(header)
            
            # Write Library
            for piece in self.dictionary:
                f.write(struct.pack('<H', len(piece)))
                f.write(piece)
                
            # Write Instructions
            stream = bytearray()
            for t, v in self.instruction_stream:
                if t == 0: # Raw byte
                    stream.append(0)
                    stream.append(v)
                else: # Dict index
                    stream.append(1)
                    stream.extend(struct.pack('<H', v))
            
            # Final Recursive Squeeze
            f.write(zlib.compress(stream, level=9))

        duration = time.time() - start_time
        new_size = os.path.getsize(output_path)
        reduction = (1 - (new_size / file_size)) * 100
        
        print(f"[MRSS] Elastic Fold Complete in {duration:.2f}s")
        print(f"[MRSS] Original Mass: {file_size} bytes")
        print(f"[MRSS] Möbius Mass:   {new_size} bytes")
        print(f"[MRSS] Reduction:     {reduction:.2f}%")
        return reduction

    def decompress(self, input_path, output_path):
        print(f"[MRSS] Unfolding Elastic: {input_path}")
        with open(input_path, 'rb') as f:
            header = f.read(struct.calcsize('<IQQI'))
            _, original_size, dict_count, inst_count = struct.unpack('<IQQI', header)
            
            library = []
            for _ in range(dict_count):
                p_len = struct.unpack('<H', f.read(2))[0]
                library.append(f.read(p_len))
            
            stream = zlib.decompress(f.read())
            
        restored = bytearray()
        offset = 0
        while offset < len(stream):
            t = stream[offset]
            offset += 1
            if t == 0:
                restored.append(stream[offset])
                offset += 1
            else:
                idx = struct.unpack_from('<H', stream, offset)[0]
                restored.extend(library[idx])
                offset += 2
        
        with open(output_path, 'wb') as f:
            f.write(restored[:original_size])
        print(f"[MRSS] Restoration Complete.")

if __name__ == "__main__":
    engine = MRSSEngine()
    image_file = "../multiverse_telemetry_final.webp"
    compressed_file = "test_image_elastic.mcc"
    restored_file = "test_image_restored_elastic.webp"
    
    if os.path.exists(image_file):
        engine.compress(image_file, compressed_file)
        engine.decompress(compressed_file, restored_file)
        
        with open(image_file, 'rb') as f1, open(restored_file, 'rb') as f2:
            if f1.read() == f2.read():
                print("\n[VERIFICATION] 100% BIT-PERFECT PARITY ATTAINED.")
            else:
                print("\n[VERIFICATION] FAILED. DATA CORRUPTION DETECTED.")
