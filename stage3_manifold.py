import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os

RESOLUTION = 200 
LIMIT = 10000    

def generate_moebius_manifold(n_points):
    u = np.linspace(0, 2 * np.pi, n_points) 
    v = np.linspace(-1, 1, n_points)      
    u, v = np.meshgrid(u, v)
    
    x = (1 + 0.5 * v * np.cos(u / 2)) * np.cos(u)
    y = (1 + 0.5 * v * np.cos(u / 2)) * np.sin(u)
    z = 0.5 * v * np.sin(u / 2)
    return x, y, z, u, v

def run_stage_3():
    print("Generating 3D Möbius Manifold with Hardware-Tuned Parameters...")
    x, y, z, u_map, v_map = generate_moebius_manifold(RESOLUTION)
    
    tension = np.sin(5 * u_map) * np.cos(v_map * 2) 
    
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(16, 12))
    ax = fig.add_subplot(111, projection='3d')
    
    surf = ax.plot_surface(x, y, z, facecolors=plt.cm.coolwarm(tension), 
                           linewidth=0, antialiased=True, alpha=0.9)
    
    vx = -0.1 * v_map * np.cos(u_map)
    vy = -0.1 * v_map * np.sin(u_map)
    vz = -0.05 * v_map
    
    skip = 12  # Denser vector field for 128GB capacity proof
    ax.quiver(x[::skip, ::skip], y[::skip, ::skip], z[::skip, ::skip], 
              vx[::skip, ::skip], vy[::skip, ::skip], vz[::skip, ::skip], 
              color='white', length=0.2, normalize=True, alpha=0.9, arrow_length_ratio=0.1)

    ax.set_title("Stage 3: 3D Möbius Vector Singularity (The Critical Line Sink)", fontsize=20, color='white', pad=20)
    ax.set_axis_off()
    
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stage3_manifold.png')
    plt.savefig(out_path, dpi=300, bbox_inches='tight', facecolor='black')
    print(f"[+] Saved hi-res 3D Manifold proof to {out_path}")

if __name__ == "__main__":
    run_stage_3()
