import numpy as np
import multiprocessing as mp
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os

# --- HARDWARE-TUNED CONFIGURATION ---
LIMIT = 5_000_000        # The 'jive' test range
CORES = min(16, mp.cpu_count())  # Parallelizing across available cores
MUTATION_BIAS = 0.02     # The 'Thread B' mutation to test stability

class SingularityEngine:
    def __init__(self, limit):
        self.limit = limit
        self.l_array = None
        self.prime_map = None
        self.all_primes = None

    def initialize_buffer(self):
        """Stage 1: Building the Parity Memory."""
        print(f"[*] Initializing Singularity Buffer for {self.limit} units...")
        is_prime = np.ones(self.limit + 1, dtype=bool)
        l_arr = np.ones(self.limit + 1, dtype=int)
        
        for i in range(2, self.limit + 1):
            if is_prime[i]:
                l_arr[i::i] *= -1
                for multiple in range(i*i, self.limit + 1, i):
                    is_prime[multiple] = False
                    temp = multiple // i
                    while temp % i == 0:
                        l_arr[multiple] *= -1
                        temp //= i
        self.l_array = l_arr
        self.prime_map = is_prime
        self.all_primes = np.where(is_prime)[0][2:] # Exclude 0, 1
        print(f"[+] Buffer ready. Found {len(self.all_primes)} Prime Peaks.")

    @staticmethod
    def calculate_tension(chunk_info):
        """Stage 2: Successional Wave Logic."""
        start, end, l_arr, p_map, all_primes, bias = chunk_info
        history = []
        p_idx = np.searchsorted(all_primes, start) - 1
        p_prev = all_primes[p_idx] if p_idx >= 0 else 2

        for n in range(start, end):
            if p_map[n]: p_prev = n
            # The Core Equation: Phase Shift x Möbius Twist
            phase = 2 * np.pi * (np.log(n) / np.log(p_prev))
            # Thread A (Baseline) vs Thread B (Mutated)
            rebound = l_arr[n] * np.cos(phase + bias)
            history.append(rebound)
        return history

    def run_master_sim(self):
        indices = np.linspace(2, self.limit, CORES + 1, dtype=int)
        chunks = [(indices[i], indices[i+1], self.l_array, self.prime_map, 
                   self.all_primes, 0) for i in range(CORES)]
        mutated_chunks = [(indices[i], indices[i+1], self.l_array, self.prime_map, 
                           self.all_primes, MUTATION_BIAS) for i in range(CORES)]

        with mp.Pool(CORES) as pool:
            print(f"[*] Launching Dual-Thread Möbius Simulation on {CORES} cores...")
            baseline = pool.map(self.calculate_tension, chunks)
            mutated = pool.map(self.calculate_tension, mutated_chunks)

        return (np.concatenate(baseline), np.concatenate(mutated))

    def visualize_singularity(self, baseline, mutated):
        """Stage 3 & 4: Manifold Projection and Residue Analysis."""
        fig = plt.figure(figsize=(18, 9))
        
        # 1D Successional Wave
        ax1 = fig.add_subplot(221)
        ax1.plot(baseline[:1000], color='cyan', label="Thread A (Baseline)")
        ax1.set_title("Successional Wave Architecture (SWA)")
        ax1.legend()

        # Parity Drift (The 'Wobble' Check)
        ax2 = fig.add_subplot(222)
        ax2.plot(np.cumsum(baseline), color='cyan', alpha=0.8, label="Baseline")
        ax2.plot(np.cumsum(mutated), color='magenta', alpha=0.5, label="Mutated")
        ax2.set_title("Parity Drift: Baseline vs Mutated")
        ax2.legend()

        # 3D Möbius Manifold Projection
        ax3 = fig.add_subplot(212, projection='3d')
        u = np.linspace(0, 2 * np.pi, 100)
        v = np.linspace(-1, 1, 100)
        u, v = np.meshgrid(u, v)
        x = (1 + 0.5 * v * np.cos(u / 2)) * np.cos(u)
        y = (1 + 0.5 * v * np.cos(u / 2)) * np.sin(u)
        z = 0.5 * v * np.sin(u / 2)
        
        # Map the first few ripples onto the manifold
        tension_map = baseline[:10000].reshape(100, 100)
        ax3.plot_surface(x, y, z, facecolors=plt.cm.coolwarm(tension_map), 
                        linewidth=0, antialiased=True, alpha=0.6)
        ax3.set_title("3D Möbius Singularity Drain (The Residue of Truth)")
        ax3.set_axis_off()

        plt.tight_layout()
        out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'moebius_singularity.png')
        plt.savefig(out_path)
        print(f"[+] Saved visualization to {out_path}")

if __name__ == "__main__":
    lab = SingularityEngine(LIMIT)
    lab.initialize_buffer()
    base, mut = lab.run_master_sim()
    lab.visualize_singularity(base, mut)
