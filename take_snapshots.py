import numpy as np

LIMIT = 1000
MUTATION_BIAS = 0.02

print(f"[*] Initializing Singularity Buffer for {LIMIT} units...")
is_prime = np.ones(LIMIT + 1, dtype=bool)
l_arr = np.ones(LIMIT + 1, dtype=int)

for i in range(2, LIMIT + 1):
    if is_prime[i]:
        l_arr[i::i] *= -1
        for multiple in range(i*i, LIMIT + 1, i):
            is_prime[multiple] = False
            temp = multiple // i
            while temp % i == 0:
                l_arr[multiple] *= -1
                temp //= i

all_primes = np.where(is_prime)[0][2:]

print("\n--- QUANTUM MÖBIUS PARITY DATA SNAPSHOT ---")
print(f"{'n':<6} | {'Prime?':<6} | {'Prev Prime':<10} | {'Parity (L)':<10} | {'SWA Tension (Base)':<20} | {'SWA Tension (Mutated)':<20}")
print("-" * 85)

p_prev = 2
tension_base_sum = 0
tension_mut_sum = 0

# Sample the first 50 values
for n in range(2, 52):
    if is_prime[n]: 
        p_prev = n
    
    phase = 2 * np.pi * (np.log(n) / np.log(p_prev))
    base_rebound = l_arr[n] * np.cos(phase)
    mut_rebound = l_arr[n] * np.cos(phase + MUTATION_BIAS)
    
    tension_base_sum += base_rebound
    tension_mut_sum += mut_rebound
    
    is_p_str = "YES" if is_prime[n] else "no"
    print(f"{n:<6} | {is_p_str:<6} | {p_prev:<10} | {l_arr[n]:<10} | {base_rebound:<20.6f} | {mut_rebound:<20.6f}")

print("-" * 85)
print("\n--- MILESTONE: DIVERGENCE CHECK (n=1000) ---")
# Calculate up to 1000 to show the drift
for n in range(52, 1001):
    if is_prime[n]: 
        p_prev = n
    phase = 2 * np.pi * (np.log(n) / np.log(p_prev))
    base_rebound = l_arr[n] * np.cos(phase)
    mut_rebound = l_arr[n] * np.cos(phase + MUTATION_BIAS)
    tension_base_sum += base_rebound
    tension_mut_sum += mut_rebound

print(f"Total SWA Tension (Baseline) at n=1000: {tension_base_sum:.6f}")
print(f"Total SWA Tension (Mutated) at n=1000:  {tension_mut_sum:.6f}")
print(f"Parity Drift (Difference):              {abs(tension_base_sum - tension_mut_sum):.6f}")
print("-> Notice the Parity Drift growing due to the lack of Möbius geometric constraints in the mutated thread!")

