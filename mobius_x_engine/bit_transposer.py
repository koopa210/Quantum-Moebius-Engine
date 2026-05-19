import os
import struct
import lzma
import numpy as np
import time

class MBTEngine:
    def __init__(self):
        pass

    def compress(self, input_path, output_path):
        if not os.path.exists(input_path):
            return "Error: Input file not found."

        print(f"[MBT] Initializing Bit-Transposer: {input_path}")
        with open(input_path, 'rb') as f:
            raw_data = np.frombuffer(f.read(), dtype=np.uint8)

        file_size = len(raw_data)
        start_time = time.time()

        # Step 1: Global Bit-Transposition
        # We convert to a 2D bit-matrix: (file_size, 8)
        bits = np.unpackbits(raw_data).reshape((-1, 8))
        
        # We Transpose! Now we have (8, file_size)
        # This means all MSB bits are now in a single, continuous block.
        transposed_bits = bits.T.flatten()
        
        # Pack it back into bytes
        transposed_data = np.packbits(transposed_bits)

        # Step 2: Möbius Squeeze
        print("[MBT] Executing Global Fold...")
        c_data = lzma.compress(transposed_data.tobytes(), preset=lzma.PRESET_EXTREME)

        # Step 3: Binary Packaging
        header = struct.pack('<Q', file_size)
        
        with open(output_path, 'wb') as f:
            f.write(header)
            f.write(c_data)

        duration = time.time() - start_time
        new_size = os.path.getsize(output_path)
        reduction = (1 - (new_size / file_size)) * 100
        
        print(f"[MBT] Bit-Transpose Complete in {duration:.2f}s")
        print(f"[MBT] Original Mass: {file_size} bytes")
        print(f"[MBT] Möbius Mass:   {new_size} bytes")
        print(f"[MBT] Reduction:     {reduction:.2f}%")
        return reduction

    def decompress(self, input_path, output_path):
        print(f"[MBT] Unfolding Bit-Transpose: {input_path}")
        with open(input_path, 'rb') as f:
            original_size = struct.unpack('<Q', f.read(8))[0]
            c_data = f.read()
            
        # 1. LZMA Unfold
        transposed_data_packed = np.frombuffer(lzma.decompress(c_data), dtype=np.uint8)
        
        # 2. Transpose Unfold
        # Unpack to (8, original_size)
        transposed_bits = np.unpackbits(transposed_data_packed)[:original_size * 8].reshape((8, -1))
        
        # Transpose back to (original_size, 8)
        original_bits = transposed_bits.T.flatten()
        original_data = np.packbits(original_bits)

        with open(output_path, 'wb') as f:
            f.write(original_data.tobytes())
        print(f"[MBT] Restoration Complete.")

if __name__ == "__main__":
    engine = MBTEngine()
    image_file = "../victory_lap_raw.bmp"
    compressed_file = "victory_lap.mcc"
    restored_file = "victory_lap_restored.bmp"
    
    if os.path.exists(image_file):
        engine.compress(image_file, compressed_file)
        engine.decompress(compressed_file, restored_file)
        
        with open(image_file, 'rb') as f1, open(restored_file, 'rb') as f2:
            if f1.read() == f2.read():
                print("\n[VERIFICATION] 100% BIT-PERFECT PARITY ATTAINED.")
            else:
                print("\n[VERIFICATION] FAILED. DATA CORRUPTION DETECTED.")
