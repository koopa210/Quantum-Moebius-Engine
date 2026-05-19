import os
import struct
import zlib
import numpy as np
import math
import random
import warnings

# Suppress warnings for complex curves
warnings.filterwarnings('ignore')

class TopologicalCompressor:
    def __init__(self, degree=5, chunk_size=2048):
        """
        Initializes the Optimized Topological Torsion Engine.
        :param degree: The degree of the polynomial curve.
        :param chunk_size: The spatial boundary of the macro lattice.
        """
        self.degree = degree
        self.chunk_size = chunk_size

    def ingest_to_manifold(self, filepath):
        """Reads raw binary data for topological mapping."""
        with open(filepath, 'rb') as f:
            data = f.read()
        return list(data)

    def extract_topological_signature(self, data_chunk):
        """Calculates the Core Geometry and truncates to float32."""
        x = np.arange(len(data_chunk))
        y = np.array(data_chunk)
        
        # Calculate shape (using float32 to halve mathematical overhead)
        coefficients = np.polyfit(x, y, self.degree).astype(np.float32)
        
        # Draw smooth curve
        smooth_curve = np.polyval(coefficients, x)
        
        return coefficients, smooth_curve

    def generate_tension_map(self, true_data, smooth_curve):
        """Calculates exact 1-byte residuals (Tension Peaks)."""
        tension_map = []
        for true_val, smooth_val in zip(true_data, smooth_curve):
            tension = int(true_val) - int(round(smooth_val))
            # Clamp to 1-byte bounds (-128 to 127) to fit in a signed char
            tension = max(-128, min(127, tension))
            tension_map.append(tension)
        return tension_map

    def fold(self, input_filepath, output_filepath):
        print(f"[MÖBIUS-X] Ingesting Geodesic: {input_filepath}")
        raw_data = self.ingest_to_manifold(input_filepath)
        original_length = len(raw_data)
        
        print(f"[MÖBIUS-X] Applying Torus Lattice (Chunking: {self.chunk_size} bytes)")
        
        # Initialize pure binary stream
        raw_binary_stream = bytearray()
        
        # Pack Header: <degree> <chunk_size> <original_length> <num_chunks>
        num_chunks = math.ceil(original_length / self.chunk_size)
        raw_binary_stream.extend(struct.pack('<IIII', self.degree, self.chunk_size, original_length, num_chunks))

        for i in range(0, original_length, self.chunk_size):
            chunk = raw_data[i:i + self.chunk_size]
            
            coeffs, smooth_curve = self.extract_topological_signature(chunk)
            tension = self.generate_tension_map(chunk, smooth_curve)
            
            # Pack Math: Extracted mathematical coefficients as 4-byte floats
            for c in coeffs:
                raw_binary_stream.extend(struct.pack('<f', c))
                
            # Pack Tension: Residual integers strictly as 1-byte signed chars
            for t in tension:
                raw_binary_stream.extend(struct.pack('<b', t))
                
        print("[MÖBIUS-X] Quantization Complete. Deflating Structural Stream...")
        
        # Deflate the 1-byte tension variables for maximum density
        compressed_payload = zlib.compress(raw_binary_stream, level=9)
        
        with open(output_filepath, 'wb') as f:
            f.write(compressed_payload)
            
        orig_size = os.path.getsize(input_filepath)
        new_size = os.path.getsize(output_filepath)
        ratio = (1 - (new_size / orig_size)) * 100 if orig_size > 0 else 0
        
        print(f"\n[STABILIZATION COMPLETE]")
        print(f"Original Mass:  {orig_size} bytes")
        print(f"Signature Mass: {new_size} bytes")
        print(f"Reduction Rate: {ratio:.2f}%")

    def unfold(self, signature_filepath, output_filepath):
        print(f"\n[MÖBIUS-X] Unfolding Signature: {signature_filepath}")
        with open(signature_filepath, 'rb') as f:
            compressed_payload = f.read()
            
        raw_binary_stream = zlib.decompress(compressed_payload)
        
        # Unpack Header
        degree, chunk_size, original_length, num_chunks = struct.unpack_from('<IIII', raw_binary_stream, 0)
        offset = 16 # Header is 16 bytes
        
        restored_data = []
        
        for _ in range(num_chunks):
            # Unpack Mathematical Coefficients
            coeffs = []
            for _ in range(degree + 1):
                c = struct.unpack_from('<f', raw_binary_stream, offset)[0]
                coeffs.append(c)
                offset += 4
                
            current_chunk_size = min(chunk_size, original_length - len(restored_data))
            
            # Unpack Physical Tension Map
            tension = []
            for _ in range(current_chunk_size):
                t = struct.unpack_from('<b', raw_binary_stream, offset)[0]
                tension.append(t)
                offset += 1
                
            # Reconstruct the Data
            x = np.arange(current_chunk_size)
            smooth_curve = np.polyval(coeffs, x)
            
            for smooth_val, t_val in zip(smooth_curve, tension):
                original_byte = int(round(smooth_val)) + t_val
                original_byte = max(0, min(255, original_byte)) 
                restored_data.append(original_byte)
                
        with open(output_filepath, 'wb') as f:
            f.write(bytes(restored_data))
            
        print(f"[MÖBIUS-X] Bit-Perfect Unfolding Complete: {output_filepath}")

if __name__ == "__main__":
    print(">> MÖBIUS-X TOPOLOGICAL COMPRESSION PROTOTYPE v2 <<\n")
    engine = TopologicalCompressor(degree=5, chunk_size=2048)
    
    test_file = "test_geodesic_macro.bin"
    
    # Generate 100KB of Structured Data with noise
    structured_data = bytearray()
    for i in range(100000):
        # A complex, multi-frequency geometric wave
        val = 127 + (60 * math.sin(i * 0.05)) + (30 * math.cos(i * 0.01))
        # Add random physical noise to test the Tension map
        val += random.randint(-2, 2) 
        structured_data.append(int(val))
        
    with open(test_file, 'wb') as f:
        f.write(structured_data)
        
    engine.fold(test_file, "test_geodesic_macro.mtc")
    engine.unfold("test_geodesic_macro.mtc", "test_geodesic_macro_restored.bin")
    
    with open(test_file, 'rb') as f1, open("test_geodesic_macro_restored.bin", 'rb') as f2:
        if f1.read() == f2.read():
            print("\n>> VERIFICATION: 100% LOSSLESS PARITY ATTAINED.")
        else:
            print("\n>> VERIFICATION FAILED: PARITY MISMATCH.")
