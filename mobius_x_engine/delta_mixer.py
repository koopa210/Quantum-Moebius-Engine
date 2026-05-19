import os
import struct
import lzma
import numpy as np
import time

class MDMEngine:
    def __init__(self):
        pass

    def compress(self, input_path, output_path):
        if not os.path.exists(input_path):
            return "Error: Input file not found."

        print(f"[MDM] Initializing Delta-Mixer: {input_path}")
        with open(input_path, 'rb') as f:
            raw_data = np.frombuffer(f.read(), dtype=np.uint8)

        file_size = len(raw_data)
        start_time = time.time()

        # Step 1: Bit-Plane Slicing
        bits = np.unpackbits(raw_data).reshape((-1, 8))
        planes = bits.T # (8, file_size)
        
        # Step 2: Differential XOR Mapping
        # We store Plane 7 (MSB) and then the XOR difference for all other planes
        diff_planes = [planes[7]]
        for i in range(6, -1, -1):
            diff_planes.append(np.bitwise_xor(planes[i+1], planes[i]))
        
        # Step 3: Transposition
        transposed_bits = np.array(diff_planes).flatten()
        transposed_data = np.packbits(transposed_bits)

        # Step 4: Möbius Squeeze
        print("[MDM] Executing Differential Fold...")
        c_data = lzma.compress(transposed_data.tobytes(), preset=lzma.PRESET_EXTREME)

        # Step 5: Binary Packaging
        header = struct.pack('<Q', file_size)
        
        with open(output_path, 'wb') as f:
            f.write(header)
            f.write(c_data)

        duration = time.time() - start_time
        new_size = os.path.getsize(output_path)
        reduction = (1 - (new_size / file_size)) * 100
        
        print(f"[MDM] Delta-Mix Complete in {duration:.2f}s")
        print(f"[MDM] Original Mass: {file_size} bytes")
        print(f"[MDM] Möbius Mass:   {new_size} bytes")
        print(f"[MDM] Reduction:     {reduction:.2f}%")
        return reduction

    def decompress(self, input_path, output_path):
        print(f"[MDM] Unfolding Delta-Mix: {input_path}")
        with open(input_path, 'rb') as f:
            original_size = struct.unpack('<Q', f.read(8))[0]
            c_data = f.read()
            
        # 1. LZMA Unfold
        transposed_data_packed = np.frombuffer(lzma.decompress(c_data), dtype=np.uint8)
        
        # 2. Transpose Unfold
        diff_planes = np.unpackbits(transposed_data_packed)[:original_size * 8].reshape((8, -1))
        
        # 3. Differential XOR Unfold
        # Restore Plane 7, then 6, then 5...
        planes = [None] * 8
        planes[7] = diff_planes[0]
        for i in range(6, -1, -1):
            # Plane[i] = Plane[i+1] XOR Diff[7-i]
            planes[i] = np.bitwise_xor(planes[i+1], diff_planes[7-i])
        
        # 4. Weave back to bytes
        original_bits = np.array(planes).T.flatten()
        original_data = np.packbits(original_bits)

        with open(output_path, 'wb') as f:
            f.write(original_data.tobytes())
        print(f"[MDM] Restoration Complete.")

if __name__ == "__main__":
    engine = MDMEngine()
    image_file = "../multiverse_telemetry_final.webp"
    compressed_file = "test_image_delta.mcc"
    restored_file = "test_image_restored_delta.webp"
    
    if os.path.exists(image_file):
        engine.compress(image_file, compressed_file)
        engine.decompress(compressed_file, restored_file)
        
        with open(image_file, 'rb') as f1, open(restored_file, 'rb') as f2:
            if f1.read() == f2.read():
                print("\n[VERIFICATION] 100% BIT-PERFECT PARITY ATTAINED.")
            else:
                print("\n[VERIFICATION] FAILED. DATA CORRUPTION DETECTED.")
