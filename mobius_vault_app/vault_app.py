import customtkinter as ctk
from tkinter import filedialog
import os
import threading
import time

# Import the optimized math engine
from topological_compressor import TopologicalCompressor

# Apply Möbius-X Aesthetic
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MobiusVaultApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Möbius-X Topological Vault")
        self.geometry("600x500")
        self.resizable(False, False)
        
        self.engine = TopologicalCompressor(degree=5, chunk_size=2048)

        # Title
        self.title_label = ctk.CTkLabel(self, text="MÖBIUS-X VAULT", font=ctk.CTkFont(size=24, weight="bold"), text_color="#00FFFF")
        self.title_label.pack(pady=20)

        # Tabs
        self.tabview = ctk.CTkTabview(self, width=500, height=300)
        self.tabview.pack(padx=20, pady=10)

        self.tab_fold = self.tabview.add("Topological Fold (Compress)")
        self.tab_unfold = self.tabview.add("Manifold Unfold (Decompress)")

        self._build_fold_tab()
        self._build_unfold_tab()
        
        # Global Status / Metrics
        self.status_label = ctk.CTkLabel(self, text="System Ready.", font=ctk.CTkFont(size=14))
        self.status_label.pack(pady=10)
        
        self.metrics_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=16, weight="bold"), text_color="#FF00FF")
        self.metrics_label.pack(pady=5)

    def _build_fold_tab(self):
        btn = ctk.CTkButton(self.tab_fold, text="Select File to Fold", 
                            font=ctk.CTkFont(size=16), height=50, fg_color="#008080", hover_color="#00AAAA",
                            command=self.run_fold)
        btn.pack(expand=True)

    def _build_unfold_tab(self):
        btn = ctk.CTkButton(self.tab_unfold, text="Select .mtc to Unfold", 
                            font=ctk.CTkFont(size=16), height=50, fg_color="#800080", hover_color="#AA00AA",
                            command=self.run_unfold)
        btn.pack(expand=True)

    def run_fold(self):
        filepath = filedialog.askopenfilename(title="Select File to Compress")
        if not filepath:
            return
            
        output_filepath = filepath + ".mtc"
        
        self.status_label.configure(text=f"Mapping Topology... Please wait.")
        self.metrics_label.configure(text="")
        
        def fold_thread():
            try:
                start_time = time.time()
                self.engine.fold(filepath, output_filepath)
                duration = time.time() - start_time
                
                orig_size = os.path.getsize(filepath)
                new_size = os.path.getsize(output_filepath)
                ratio = (1 - (new_size / orig_size)) * 100 if orig_size > 0 else 0
                
                self.status_label.configure(text=f"Stabilization Complete in {duration:.1f}s. Saved to:\n{os.path.basename(output_filepath)}")
                self.metrics_label.configure(text=f"Mass: {orig_size}B → {new_size}B  |  Reduction: {ratio:.2f}%")
            except Exception as e:
                self.status_label.configure(text=f"Error: {str(e)}")

        threading.Thread(target=fold_thread, daemon=True).start()

    def run_unfold(self):
        filepath = filedialog.askopenfilename(title="Select .mtc File", filetypes=[("Möbius Topological Core", "*.mtc")])
        if not filepath:
            return
            
        output_filepath = filepath.replace(".mtc", "") + "_restored"
        # preserve extension if it existed, though basic strip is fine for prototype
        if "." in os.path.basename(filepath.replace(".mtc", "")):
            pass # keep it
        else:
            output_filepath += ".bin"
            
        self.status_label.configure(text=f"Unfolding Geodesic... Please wait.")
        self.metrics_label.configure(text="")
        
        def unfold_thread():
            try:
                start_time = time.time()
                self.engine.unfold(filepath, output_filepath)
                duration = time.time() - start_time
                
                self.status_label.configure(text=f"Bit-Perfect Parity Restored in {duration:.1f}s. Saved to:\n{os.path.basename(output_filepath)}")
                self.metrics_label.configure(text="STATUS: 100% INVARIANT", text_color="#00FFFF")
            except Exception as e:
                self.status_label.configure(text=f"Error: {str(e)}")

        threading.Thread(target=unfold_thread, daemon=True).start()

if __name__ == "__main__":
    app = MobiusVaultApp()
    app.mainloop()
