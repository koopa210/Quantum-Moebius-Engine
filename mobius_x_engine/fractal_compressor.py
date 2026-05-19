import os
import struct
import zlib
import numpy as np
import time
import hashlib

class MFMEngine:
    def __init__(self, block_size=16, threshold=40):
        # We use 16 bytes for 1D data. 
        # For a true fractal search, square blocks like 4x4 or 8x8 are better for 2D data.
        self.block_size = block_size 
        self.threshold = threshold
        self.master_pieces = []
        self.instructions = []
        self.tension_maps = []
        self.window_size = 512

    def _reset(self):
        self.master_pieces = []
        self.instructions = []
        self.tension_maps = []

    def _apply_transforms(self, block):
        """Generates the Symmetry Family of a block."""
        family = []
        # 0: Original
        family.append((0, block))
        
        # 1: Bit-Inverted (Möbius Inversion)
        family.append((1, np.bitwise_not(block)))
        
        # 2: Flipped (Reverse)
        family.append((2, np.flip(block)))
        
        # 3: Byte-Shifted (Simulated rotation for 1D)
        family.append((3, np.roll(block, self.block_size // 2)))
        
        return family

    def compress(self, input_path, output_path):
        self._reset()
        if not os.path.exists(input_path):
            return "Error: Input file not found."

        print(f"[MFM] Folding Geodesic: {input_path}")
        with open(input_path, 'rb') as f:
            raw_data = np.frombuffer(f.read(), dtype=np.uint8)

        file_size = len(raw_data)
        start_time = time.time()

        # Partitioning
        all_blocks = []
        for i in range(0, file_size, self.block_size):
            block = raw_data[i : i + self.block_size]
            if len(block) < self.block_size:
                block = np.pad(block, (0, self.block_size - len(block)), mode='constant')
            all_blocks.append(block)
        
        all_blocks = np.array(all_blocks)
        num_blocks = len(all_blocks)
        master_matrix = np.empty((0, self.block_size), dtype=np.uint8)
        
        print(f"[MFM] Scanning Symmetry Manifolds ({num_blocks} blocks)...")

        for i, block in enumerate(all_blocks):
            if i % 5000 == 0:
                print(f"[MFM] Fold Progress: {i}/{num_blocks}...")

            best_match_id = -1
            best_transform = 0
            min_dist = float('inf')

            if len(master_matrix) > 0:
                # Optimized Symmetry Search
                # We check the block's family against the existing masters
                lookback = master_matrix[-self.window_size:]
                
                # We generate the family for the CURRENT block
                family = self._apply_transforms(block)
                
                for t_type, t_block in family:
                    distances = np.sum(np.abs(lookback.astype(np.int16) - t_block.astype(np.int16)), axis=1)
                    min_idx = np.argmin(distances)
                    if distances[min_idx] < min_dist:
                        min_dist = distances[min_idx]
                        if min_dist < self.threshold:
                            best_match_id = (len(master_matrix) - len(lookback)) + min_idx
                            best_transform = t_type
                            break # Found a 'good enough' match

            if best_match_id != -1:
                # Symmetry Match Found!
                # We must reconstruct the transformed master to calculate the tension
                master = self.master_pieces[best_match_id]
                # Note: We need to apply the INVERSE transform to the master, 
                # or just transform the block. Here we transform the block and match to master.
                # So Tension = Block_Transformed - Master
                family = self._apply_transforms(block)
                transformed_block = family[best_transform][1]
                
                tension = transformed_block.astype(np.int16) - master.astype(np.int16)
                self.instructions.append((best_match_id, best_transform, len(self.tension_maps)))
                self.tension_maps.append(tension.astype(np.int8))
            else:
                # Unique Geometric Piece
                self.master_pieces.append(block)
                master_matrix = np.vstack([master_matrix, block])
                self.instructions.append((len(self.master_pieces) - 1, 0, -1)) # id, transform=0, tension=-1

        # Binary Packaging
        print(f"[MFM] Finalizing Fractal Map...")
        header = struct.pack('<IQQI', self.block_size, file_size, len(self.master_pieces), len(self.instructions))

        with open(output_path, 'wb') as f:
            f.write(header)
            for master in self.master_pieces:
                f.write(master.tobytes())

            logic_stream = bytearray()
            idx_fmt = '<H' if len(self.master_pieces) < 65535 else '<I'
            for m_id, t_type, tens_id in self.instructions:
                logic_stream.extend(struct.pack(idx_fmt, m_id))
                logic_stream.extend(struct.pack('<B', t_type))
                logic_stream.extend(struct.pack('<i', tens_id))

            tension_stream = bytearray()
            for t_map in self.tension_maps:
                tension_stream.extend(t_map.tobytes())

            compressed_payload = zlib.compress(logic_stream + tension_stream, level=9)
            f.write(struct.pack('<I', len(compressed_payload)))
            f.write(compressed_payload)

        duration = time.time() - start_time
        new_size = os.path.getsize(output_path)
        reduction = (1 - (new_size / file_size)) * 100
        
        print(f"[MFM] Fractal Fold Complete in {duration:.2f}s")
        print(f"[MFM] Original Mass: {file_size} bytes")
        print(f"[MFM] Möbius Mass:   {new_size} bytes")
        print(f"[MFM] Reduction:     {reduction:.2f}%")
        return reduction

    def decompress(self, input_path, output_path):
        print(f"[MFM] Unfolding Fractal: {input_path}")
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
        inst_size = idx_size + 1 + 4
        
        inst_data = logic_data[:instruction_count * inst_size]
        tens_data = logic_data[instruction_count * inst_size:]

        restored_data = bytearray()
        tension_offset = 0
        
        for i in range(instruction_count):
            start = i * inst_size
            m_id = struct.unpack_from(idx_fmt, inst_data, start)[0]
            t_type = struct.unpack_from('<B', inst_data, start + idx_size)[0]
            tens_id = struct.unpack_from('<i', inst_data, start + idx_size + 1)[0]
            
            # 1. Get Master
            piece = master_pieces[m_id].astype(np.int16)
            
            # 2. Add Tension
            if tens_id != -1:
                tension = np.frombuffer(tens_data[tension_offset : tension_offset + block_size], dtype=np.int8).astype(np.int16)
                piece = piece + tension
                tension_offset += block_size
            
            # 3. Apply INVERSE Transform
            # family[t_type] = (t_type, transformed_block)
            # In our case, t_block was matched to master. So Master = Transform(Block) + Tension
            # So Block = InverseTransform(Master - Tension)
            
            final_piece = piece.astype(np.uint8)
            if t_type == 1: # Inverted
                final_piece = np.bitwise_not(final_piece)
            elif t_type == 2: # Flipped
                final_piece = np.flip(final_piece)
            elif t_type == 3: # Shifted
                final_piece = np.roll(final_piece, - (self.block_size // 2))
                
            restored_data.extend(final_piece.tobytes())

        with open(output_path, 'wb') as f:
            f.write(restored_data[:original_size])
        print(f"[MFM] Restoration Complete.")

if __name__ == "__main__":
    engine = MFMEngine(block_size=16, threshold=45)
    image_file = "../multiverse_telemetry_final.webp"
    compressed_file = "test_image_fractal.mcc"
    restored_file = "test_image_restored_fractal.webp"
    
    if os.path.exists(image_file):
        engine.compress(image_file, compressed_file)
        engine.decompress(compressed_file, restored_file)
        
        with open(image_file, 'rb') as f1, open(restored_file, 'rb') as f2:
            if f1.read() == f2.read():
                print("\n[VERIFICATION] 100% BIT-PERFECT PARITY ATTAINED.")
            else:
                print("\n[VERIFICATION] FAILED. DATA CORRUPTION DETECTED.")
