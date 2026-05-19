import os
import struct
import lzma
import numpy as np
import time

class MBPMEngine:
    def __init__(self):
        self.bit_planes = [None] * 8

    def _slice_bits(self, raw_data):
        """Deconstructs 1D byte array into 8 bit-planes."""
        planes = []
        for i in range(8):
            # Extract the i-th bit from each byte
            plane = (raw_data >> i) & 1
            planes.append(np.packbits(plane))
        return planes

    def _weave_bits(self, planes, original_size):
        """Reconstructs 1D byte array from 8 bit-planes."""
        raw_data = np.zeros(original_size, dtype=np.uint8)
        for i, plane_packed in enumerate(planes):
            # Unpack the plane (might have padding)
            plane = np.unpackbits(plane_packed)[:original_size]
            raw_data |= (plane << i).astype(np.uint8)
        return raw_data

    def compress(self, input_path, output_path):
        if not os.path.exists(input_path):
            return "Error: Input file not found."

        print(f"[MBPM] Slicing Bit-Plane Manifold: {input_path}")
        with open(input_path, 'rb') as f:
            raw_data = np.frombuffer(f.read(), dtype=np.uint8)

        file_size = len(raw_data)
        start_time = time.time()

        # Step 1: Bit-Plane Slicing
        planes = self._slice_bits(raw_data)
        
        # Step 2: Adaptive Compression
        # We compress each plane independently. 
        # Structure is usually in planes 4, 5, 6, 7 (MSB)
        # Noise is in planes 0, 1, 2, 3 (LSB)
        
        compressed_planes = []
        print("[MBPM] Squeezing Manifold Layers...")
        
        for i, plane in enumerate(planes):
            # We use high-level LZMA for each plane. 
            c_plane = lzma.compress(plane.tobytes(), preset=lzma.PRESET_EXTREME)
            compressed_planes.append(c_plane)

        # Step 3: Binary Packaging
        header = struct.pack('<Q', file_size)
        
        with open(output_path, 'wb') as f:
            f.write(header)
            # Write sizes of compressed planes
            for cp in compressed_planes:
                f.write(struct.pack('<I', len(cp)))
            
            # Write compressed data
            for cp in compressed_planes:
                f.write(cp)

        duration = time.time() - start_time
        new_size = os.path.getsize(output_path)
        reduction = (1 - (new_size / file_size)) * 100
        
        print(f"[MBPM-LZMA] Bit-Plane Fold Complete in {duration:.2f}s")
        print(f"[MBPM-LZMA] Original Mass: {file_size} bytes")
        print(f"[MBPM-LZMA] Möbius Mass:   {new_size} bytes")
        print(f"[MBPM-LZMA] Reduction:     {reduction:.2f}%")
        return reduction

    def decompress(self, input_path, output_path):
        print(f"[MBPM] Unfolding Bit-Plane Manifold: {input_path}")
        with open(input_path, 'rb') as f:
            original_size = struct.unpack('<Q', f.read(8))[0]
            
            plane_sizes = []
            for _ in range(8):
                plane_sizes.append(struct.unpack('<I', f.read(4))[0])
            
            planes = []
            for size in plane_sizes:
                c_data = f.read(size)
                planes.append(np.frombuffer(lzma.decompress(c_data), dtype=np.uint8))

        # Reconstruction
        raw_data = self._weave_bits(planes, original_size)
        
        with open(output_path, 'wb') as f:
            f.write(raw_data.tobytes())
        print(f"[MBPM] Restoration Complete.")

if __name__ == "__main__":
    engine = MBPMEngine()
    image_file = "../multiverse_telemetry_final.webp"
    compressed_file = "test_image_bitplane.mcc"
    restored_file = "test_image_restored_bitplane.webp"
    
    if os.path.exists(image_file):
        engine.compress(image_file, compressed_file)
        engine.decompress(compressed_file, restored_file)
        
        with open(image_file, 'rb') as f1, open(restored_file, 'rb') as f2:
            if f1.read() == f2.read():
                print("\n[VERIFICATION] 100% BIT-PERFECT PARITY ATTAINED.")
            else:
                print("\n[VERIFICATION] FAILED. DATA CORRUPTION DETECTED.")
