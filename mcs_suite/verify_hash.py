import hashlib
import sys

def get_hash(filepath):
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python verify_hash.py <original_file> <cracked_file>")
        sys.exit(1)
        
    f1 = sys.argv[1]
    f2 = sys.argv[2]
    
    try:
        h1 = get_hash(f1)
        h2 = get_hash(f2)
        print("="*40)
        print(f"Original File Hash: {h1}")
        print(f"Cracked File Hash:  {h2}")
        print("="*40)
        
        if h1 == h2:
            print("[SUCCESS] The files are 100% bit-for-bit identical!")
            print("The engine completely reversed the encryption perfectly.")
        else:
            print("[FAILURE] The bytes do not match. Something modified the file.")
    except Exception as e:
        print(f"Error reading files: {e}")
