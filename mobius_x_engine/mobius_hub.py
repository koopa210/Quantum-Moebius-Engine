import os
import tkinter as tk
import customtkinter as ctk
from steam_discovery import SteamScanner
from bit_transposer import MBTEngine # We use our most successful engine
import threading
import time

# System Settings
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MobiusGameHub(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Möbius Game Hub | Structural Manifold Command")
        self.geometry("1100x700")

        # Core Engines
        self.scanner = SteamScanner()
        self.engine = MBTEngine()
        self.games = []

        # UI Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="MÖBIUS-X", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.pack(pady=30)

        self.lib_btn = ctk.CTkButton(self.sidebar, text="Library", command=self.show_library)
        self.lib_btn.pack(pady=10, padx=20)

        self.bench_btn = ctk.CTkButton(self.sidebar, text="Benchmarks", command=self.show_benchmarks)
        self.bench_btn.pack(pady=10, padx=20)

        self.settings_btn = ctk.CTkButton(self.sidebar, text="Settings", command=self.show_settings)
        self.settings_btn.pack(pady=10, padx=20)

        # Main Area
        self.main_frame = ctk.CTkScrollableFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Top Bar
        self.top_bar = ctk.CTkFrame(self.main_frame, height=60, fg_color="transparent")
        self.top_bar.pack(fill="x", pady=(0, 20))

        self.title_label = ctk.CTkLabel(self.top_bar, text="Topological Library", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(side="left")

        self.refresh_btn = ctk.CTkButton(self.top_bar, text="⟳ Refresh Library", width=140, command=self.refresh_library)
        self.refresh_btn.pack(side="right")

        # Game Grid
        self.game_grid = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.game_grid.pack(fill="both", expand=True)

        # Initial Scan
        self.refresh_library()

    def refresh_library(self):
        # Clear existing
        for widget in self.game_grid.winfo_children():
            widget.destroy()

        def scan_thread():
            self.refresh_btn.configure(text="Scanning...", state="disabled")
            self.games = self.scanner.scan()
            self.after(0, self.populate_grid)

        threading.Thread(target=scan_thread).start()

    def populate_grid(self):
        self.refresh_btn.configure(text="⟳ Refresh Library", state="normal")
        
        if not self.games:
            empty_label = ctk.CTkLabel(self.game_grid, text="No Steam games detected. Ensure Steam is installed or check your library paths.", font=ctk.CTkFont(size=14))
            empty_label.pack(pady=100)
            return

        for i, game in enumerate(self.games):
            card = ctk.CTkFrame(self.game_grid, width=300, height=180, corner_radius=10)
            card.grid(row=i//3, column=i%3, padx=15, pady=15)
            card.grid_propagate(False)

            title = ctk.CTkLabel(card, text=game["name"], font=ctk.CTkFont(size=16, weight="bold"), wraplength=250)
            title.pack(pady=(20, 10))

            size_label = ctk.CTkLabel(card, text=f"Installed Size: {game['size_gb']} GB", font=ctk.CTkFont(size=12))
            size_label.pack()

            mobius_marker = os.path.join(game['path'], ".mobius_active")
            is_folded = os.path.exists(mobius_marker)

            if is_folded:
                # Folded State UI
                launch_btn = ctk.CTkButton(card, text="🚀 Launch (Accelerated)", fg_color="#2E8B57", hover_color="#3CB371",
                                           command=lambda g=game: self.launch_game(g))
                launch_btn.pack(pady=(15, 5), padx=20, fill="x")
                
                restore_btn = ctk.CTkButton(card, text="↺ Restore Assets", fg_color="transparent", border_width=1, border_color="#555555",
                                            command=lambda g=game: self.unfold_game(g))
                restore_btn.pack(pady=0, padx=20, fill="x")
            else:
                # Unfolded State UI
                fold_btn = ctk.CTkButton(card, text="Fold Manifold", fg_color="#6B3FA0", hover_color="#8B5FBF", 
                                         command=lambda g=game: self.fold_game(g))
                fold_btn.pack(pady=(20, 0), padx=20, fill="x")

    def get_target_file(self, game_path):
        """Finds the largest file to fold, ideally avoiding tiny files."""
        largest_file = None
        max_size = 0
        for root, _, files in os.walk(game_path):
            for file in files:
                if file.endswith('.mcc') or file == '.mobius_active':
                    continue
                full_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(full_path)
                    if size > max_size:
                        # For prototype sanity, let's avoid files over 500MB as Python LZMA is slow
                        if size < 500 * 1024 * 1024: 
                            max_size = size
                            largest_file = full_path
                except:
                    pass
        return largest_file

    def fold_game(self, game):
        print(f"Folding {game['name']} at {game['path']}...")
        
        # UI Feedback
        progress_popup = ctk.CTkToplevel(self)
        progress_popup.title(f"Folding {game['name']}")
        progress_popup.geometry("400x200")
        progress_popup.attributes('-topmost', True)

        label = ctk.CTkLabel(progress_popup, text=f"Scanning assets...", pady=20)
        label.pack()

        def run_fold():
            target = self.get_target_file(game['path'])
            if not target:
                label.configure(text="No suitable assets found to fold.")
                time.sleep(2)
                progress_popup.destroy()
                return

            label.configure(text=f"Folding: {os.path.basename(target)}\nThis may take a moment...")
            mcc_target = target + ".mcc"
            
            try:
                reduction = self.engine.compress(target, mcc_target)
                os.remove(target) # Delete original
                
                with open(os.path.join(game['path'], ".mobius_active"), "w") as f:
                    f.write(target)
                    
                label.configure(text=f"Möbius Signature Generated\n(Reduction: {reduction:.2f}%)")
            except Exception as e:
                label.configure(text=f"Error during fold: {e}")
                
            time.sleep(2)
            progress_popup.destroy()
            self.after(0, self.refresh_library)

        threading.Thread(target=run_fold).start()

    def launch_game(self, game):
        marker = os.path.join(game['path'], ".mobius_active")
        if os.path.exists(marker):
            try:
                with open(marker, "r") as f:
                    target = f.read().strip()
                
                mcc_target = target + ".mcc"
                if os.path.exists(mcc_target):
                    print(f"JIT Decompressing {target}...")
                    self.engine.decompress(mcc_target, target)
                    os.remove(marker)
                    os.remove(mcc_target)
            except Exception as e:
                print(f"Error during JIT Unfold: {e}")

        print(f"Launching {game['name']} via Steam protocol...")
        try:
            os.startfile(f"steam://rungameid/{game['id']}")
        except AttributeError:
            import subprocess
            subprocess.run(["cmd", "/c", "start", f"steam://rungameid/{game['id']}"])
            
        self.refresh_library()

    def unfold_game(self, game):
        print(f"Restoring {game['name']}...")
        marker = os.path.join(game['path'], ".mobius_active")
        if os.path.exists(marker):
            try:
                with open(marker, "r") as f:
                    target = f.read().strip()
                mcc_target = target + ".mcc"
                if os.path.exists(mcc_target):
                    self.engine.decompress(mcc_target, target)
                    os.remove(mcc_target)
                os.remove(marker)
            except Exception as e:
                print(f"Could not restore assets: {e}")
        self.refresh_library()

    def show_library(self):
        pass

    def show_benchmarks(self):
        pass

    def show_settings(self):
        pass

if __name__ == "__main__":
    app = MobiusGameHub()
    app.mainloop()
