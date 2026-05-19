import os
import struct
import zlib
import numpy as np
import time
from scipy.fftpack import dct, idct

class SMCEngine:
    def __init__(self, block_size=8, threshold=0.1):
        self.block_size = block_size
        self.threshold = threshold # Quantization factor for the manifold
        self.manifold_data = [] # List of (compressed_dct_coeffs, tension_map)

    def _reset(self):
        self.manifold_data = []

    def _dct2(self, block):
        """2D Discrete Cosine Transform."""
        return dct(dct(block.T, norm='ortho').T, norm='ortho')

    def _idct2(self, block):
        """Inverse 2D Discrete Cosine Transform."""
        return idct(idct(block.T, norm='ortho').T, norm='ortho')

    def compress(self, input_path, output_path):
        self._reset()
        if not os.path.exists(input_path):
            return "Error: Input file not found."

        print(f"[SMC] Mapping Frequency Manifold: {input_path}")
        with open(input_path, 'rb') as f:
            raw_data = np.frombuffer(f.read(), dtype=np.uint8)

        file_size = len(raw_data)
        start_time = time.time()

        # Phase 1: Frequency Decomposition
        # We treat the 1D stream as a 2D surface of block_size x block_size
        num_pixels_per_block = self.block_size * self.block_size
        
        print(f"[SMC] Folding into {num_pixels_per_block}-byte Spectral Windows...")
        
        output_stream = bytearray()
        
        for i in range(0, file_size, num_pixels_per_block):
            chunk = raw_data[i : i + num_pixels_per_block]
            
            # Padding
            if len(chunk) < num_pixels_per_block:
                chunk = np.pad(chunk, (0, num_pixels_per_block - len(chunk)), mode='constant')
            
            block = chunk.reshape((self.block_size, self.block_size)).astype(float)
            
            # 1. Transform to Frequency Domain
            coeffs = self._dct2(block)
            
            # 2. Topological Quantization (The Squeeze)
            # We keep only the significant coefficients to form the 'Signal'
            # Low-frequency coefficients are in the top-left (0,0)
            # For the prototype, we'll keep the top 1/4 of coefficients and zero the rest
            mask = np.zeros((self.block_size, self.block_size))
            mask[:self.block_size//2, :self.block_size//2] = 1
            
            signal_coeffs = coeffs * mask
            
            # 3. Resonant Recovery (The Tension)
            # Reconstruct the 'Smooth' signal from the partial coefficients
            reconstructed_signal = self._idct2(signal_coeffs)
            reconstructed_signal = np.clip(reconstructed_signal, 0, 255).astype(np.uint8)
            
            # Tension = Original - Reconstructed
            tension = block.astype(np.int16) - reconstructed_signal.astype(np.int16)
            
            # Store the Signal (top-left coeffs) and the Tension (residuals)
            # To make it efficient, we only store the non-zero coefficients
            compact_coeffs = signal_coeffs[:self.block_size//2, :self.block_size//2].flatten()
            
            output_stream.extend(compact_coeffs.astype(np.float32).tobytes())
            output_stream.extend(tension.astype(np.int8).tobytes())

        # Phase 2: Binary Packaging
        print("[SMC] Resonating Entropy Streams...")
        header = struct.pack('<IQQ', self.block_size, file_size, 0)
        
        # We use zlib to squeeze the sparse tension maps and the spectral coefficients
        compressed_payload = zlib.compress(output_stream, level=9)
        
        with open(output_path, 'wb') as f:
            f.write(header)
            f.write(compressed_payload)

        duration = time.time() - start_time
        new_size = os.path.getsize(output_path)
        reduction = (1 - (new_size / file_size)) * 100
        
        print(f"[SMC] Spectral Fold Complete in {duration:.2f}s")
        print(f"[SMC] Original Mass: {file_size} bytes")
        print(f"[SMC] Möbius Mass:   {new_size} bytes")
        print(f"[SMC] Reduction:     {reduction:.2f}%")
        return reduction

    def decompress(self, input_path, output_path):
        print(f"[SMC] Unfolding Spectral Manifold: {input_path}")
        with open(input_path, 'rb') as f:
            header = f.read(struct.calcsize('<IQQ'))
            block_size, original_size, _ = struct.unpack('<IQQ', header)
            
            payload = zlib.decompress(f.read())

        num_pixels_per_block = block_size * block_size
        num_coeffs = (block_size // 2) * (block_size // 2)
        
        # Step size in the binary payload
        # 1 float32 (4 bytes) per coeff + 1 int8 (1 byte) per pixel
        step = (num_coeffs * 4) + num_pixels_per_block
        
        restored_data = bytearray()
        
        for i in range(0, len(payload), step):
            chunk = payload[i : i + step]
            if len(chunk) < step: break
            
            # 1. Extract Signal Coeffs
            coeffs_raw = chunk[:num_coeffs * 4]
            compact_coeffs = np.frombuffer(coeffs_raw, dtype=np.float32).reshape((block_size//2, block_size//2))
            
            # Reconstruct the full DCT matrix
            signal_coeffs = np.zeros((block_size, block_size))
            signal_coeffs[:block_size//2, :block_size//2] = compact_coeffs
            
            # 2. Extract Tension Map
            tension_raw = chunk[num_coeffs * 4 : step]
            tension = np.frombuffer(tension_raw, dtype=np.int8).reshape((block_size, block_size)).astype(np.int16)
            
            # 3. Resonant Synthesis
            reconstructed_signal = self._idct2(signal_coeffs)
            reconstructed_signal = np.clip(reconstructed_signal, 0, 255).astype(np.uint8)
            
            # Original = Reconstructed + Tension
            final_block = reconstructed_signal.astype(np.int16) + tension
            final_block = np.clip(final_block, 0, 255).astype(np.uint8)
            
            restored_data.extend(final_block.flatten().tobytes())

        with open(output_path, 'wb') as f:
            f.write(restored_data[:original_size])
        print(f"[SMC] Restoration Complete.")

if __name__ == "__main__":
    engine = SMCEngine(block_size=8)
    image_file = "../multiverse_telemetry_final.webp"
    compressed_file = "test_image_spectral.mcc"
    restored_file = "test_image_restored_spectral.webp"
    
    if os.path.exists(image_file):
        engine.compress(image_file, compressed_file)
        engine.decompress(compressed_file, restored_file)
        
        with open(image_file, 'rb') as f1, open(restored_file, 'rb') as f2:
            if f1.read() == f2.read():
                print("\n[VERIFICATION] 100% BIT-PERFECT PARITY ATTAINED.")
            else:
                print("\n[VERIFICATION] FAILED. DATA CORRUPTION DETECTED.")
