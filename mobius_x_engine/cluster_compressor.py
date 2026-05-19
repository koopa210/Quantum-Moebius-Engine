import os
import struct
import zlib
import numpy as np
import time

class MCCEngine:
    def __init__(self, block_size=16, threshold=50):
        self.block_size = block_size
        self.threshold = threshold
        self.master_pieces = []
        self.instructions = []
        self.tension_maps = []
        self.window_size = 512 # Number of masters to look back at

    def _reset(self):
        self.master_pieces = []
        self.instructions = []
        self.tension_maps = []

    def compress(self, input_path, output_path):
        self._reset()
        if not os.path.exists(input_path):
            return "Error: Input file not found."

        print(f"[MCC-Opt] Ingesting: {input_path}")
        with open(input_path, 'rb') as f:
            raw_data = np.frombuffer(f.read(), dtype=np.uint8)

        file_size = len(raw_data)
        start_time = time.time()

        # Pre-convert to numpy for speed
        all_blocks = []
        for i in range(0, file_size, self.block_size):
            block = raw_data[i : i + self.block_size]
            if len(block) < self.block_size:
                block = np.pad(block, (0, self.block_size - len(block)), mode='constant')
            all_blocks.append(block)
        
        all_blocks = np.array(all_blocks)
        num_blocks = len(all_blocks)
        
        master_matrix = np.empty((0, self.block_size), dtype=np.uint8)
        
        print(f"[MCC-Opt] Processing {num_blocks} blocks...")

        for i, block in enumerate(all_blocks):
            if i % 10000 == 0:
                print(f"[MCC-Opt] Block {i}/{num_blocks}...")

            best_match_id = -1
            min_dist = float('inf')

            if len(master_matrix) > 0:
                # Optimized Vector Search
                # Only look at the last N masters
                lookback = master_matrix[-self.window_size:]
                distances = np.sum(np.abs(lookback.astype(np.int16) - block.astype(np.int16)), axis=1)
                
                min_idx = np.argmin(distances)
                if distances[min_idx] < self.threshold:
                    min_dist = distances[min_idx]
                    best_match_id = (len(master_matrix) - len(lookback)) + min_idx

            if best_match_id != -1:
                # Shadow found
                tension = block.astype(np.int16) - master_matrix[best_match_id].astype(np.int16)
                self.instructions.append((best_match_id, len(self.tension_maps)))
                self.tension_maps.append(tension.astype(np.int8))
            else:
                # New Master
                self.master_pieces.append(block)
                master_matrix = np.vstack([master_matrix, block])
                self.instructions.append((len(self.master_pieces) - 1, -1))

        # Binary Packaging
        print(f"[MCC-Opt] Packaging...")
        header = struct.pack('<IQQI', self.block_size, file_size, len(self.master_pieces), len(self.instructions))

        with open(output_path, 'wb') as f:
            f.write(header)
            for master in self.master_pieces:
                f.write(master.tobytes())

            instruction_stream = bytearray()
            idx_fmt = '<H' if len(self.master_pieces) < 65535 else '<I'
            for master_id, tension_id in self.instructions:
                instruction_stream.extend(struct.pack(idx_fmt, master_id))
                instruction_stream.extend(struct.pack('<i', tension_id))

            tension_stream = bytearray()
            for t_map in self.tension_maps:
                tension_stream.extend(t_map.tobytes())

            compressed_logic = zlib.compress(instruction_stream + tension_stream, level=9)
            f.write(struct.pack('<I', len(compressed_logic)))
            f.write(compressed_logic)

        duration = time.time() - start_time
        new_size = os.path.getsize(output_path)
        reduction = (1 - (new_size / file_size)) * 100
        
        print(f"[MCC-Opt] Fold Complete in {duration:.2f}s")
        print(f"[MCC-Opt] Original Mass: {file_size} bytes")
        print(f"[MCC-Opt] Möbius Mass:   {new_size} bytes")
        print(f"[MCC-Opt] Reduction:     {reduction:.2f}%")
        return reduction

    def decompress(self, input_path, output_path):
        print(f"[MCC-Opt] Unfolding: {input_path}")
        with open(input_path, 'rb') as f:
            header = f.read(struct.calcsize('<IQQI'))
            block_size, original_size, master_count, instruction_count = struct.unpack('<IQQI', header)

            master_pieces = []
            for _ in range(master_count):
                master_pieces.append(np.frombuffer(f.read(block_size), dtype=np.uint8))

            logic_len = struct.unpack('<I', f.read(4))[0]
            logic_data = zlib.decompress(f.read(logic_len))

        idx_fmt = '<H' if master_count < 65535 else '<I'
        idx_size = struct.calcsize(idx_fmt)
        inst_len = instruction_count * (idx_size + 4)
        inst_data = logic_data[:inst_len]
        tens_data = logic_data[inst_len:]

        restored_data = bytearray()
        tension_offset = 0
        
        for i in range(instruction_count):
            start = i * (idx_size + 4)
            master_id = struct.unpack_from(idx_fmt, inst_data, start)[0]
            tension_id = struct.unpack_from('<i', inst_data, start + idx_size)[0]
            
            master = master_pieces[master_id].astype(np.int16)
            if tension_id == -1:
                piece = master
            else:
                tension = np.frombuffer(tens_data[tension_offset : tension_offset + block_size], dtype=np.int8).astype(np.int16)
                piece = master + tension
                tension_offset += block_size
            
            restored_data.extend(piece.astype(np.uint8).tobytes())

        with open(output_path, 'wb') as f:
            f.write(restored_data[:original_size])
        print(f"[MCC-Opt] Restoration Complete.")

if __name__ == "__main__":
    engine = MCCEngine(block_size=16, threshold=40)
    image_file = "../multiverse_telemetry_final.webp"
    compressed_file = "test_image_opt.mcc"
    restored_file = "test_image_restored.webp"
    
    if os.path.exists(image_file):
        engine.compress(image_file, compressed_file)
        engine.decompress(compressed_file, restored_file)
        
        with open(image_file, 'rb') as f1, open(restored_file, 'rb') as f2:
            if f1.read() == f2.read():
                print("\n[VERIFICATION] 100% BIT-PERFECT PARITY ATTAINED.")
            else:
                print("\n[VERIFICATION] FAILED. DATA CORRUPTION DETECTED.")
