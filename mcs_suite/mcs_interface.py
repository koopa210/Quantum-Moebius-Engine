import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import time
import os
from mcs_engine import MCSEngine

class MCSInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Möbius Cryptanalytic Suite (M-CS) v1.0")
        self.root.geometry("800x650")
        self.root.configure(bg="#0B0F19")
        
        self.engine = MCSEngine()
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background="#0B0F19", borderwidth=0)
        style.configure("TNotebook.Tab", background="#1A2235", foreground="#00E5FF", padding=[15, 5], font=('Consolas', 10, 'bold'))
        style.map("TNotebook.Tab", background=[("selected", "#00E5FF")], foreground=[("selected", "#0B0F19")])
        
        style.configure("TFrame", background="#0B0F19")
        style.configure("TButton", background="#1A2235", foreground="#00E5FF", borderwidth=1, font=('Consolas', 10, 'bold'))
        style.map("TButton", background=[("active", "#00E5FF")], foreground=[("active", "#0B0F19")])
        
        style.configure("TLabel", background="#0B0F19", foreground="#E2E8F0", font=('Consolas', 10))
        style.configure("Header.TLabel", foreground="#00E5FF", font=('Consolas', 14, 'bold'))
        style.configure("Alert.TLabel", foreground="#FF3366", font=('Consolas', 12, 'bold'))
        style.configure("TRadiobutton", background="#0B0F19", foreground="#00E5FF", font=('Consolas', 10))
        
        # Main Notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Tabs
        self.tab_audit = ttk.Frame(self.notebook)
        self.tab_crack = ttk.Frame(self.notebook)
        self.tab_encrypt = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_audit, text=" [ AUDIT MODE ] ")
        self.notebook.add(self.tab_crack, text=" [ CRACK ASSIST / PoC ] ")
        self.notebook.add(self.tab_encrypt, text=" [ ENCRYPT ] ")
        
        self._build_audit_tab()
        self._build_crack_tab()
        self._build_encrypt_tab()
        
    def _build_audit_tab(self):
        ttk.Label(self.tab_audit, text="TOPOLOGICAL CRYPTANALYTIC AUDIT", style="Header.TLabel").pack(pady=20)
        
        self.lbl_audit_file = ttk.Label(self.tab_audit, text="No file selected")
        self.lbl_audit_file.pack(pady=5)
        
        ttk.Button(self.tab_audit, text="SELECT ENCRYPTED TARGET", command=self.select_audit_file).pack(pady=10)
        
        # Results frame
        self.audit_results = tk.Text(self.tab_audit, height=15, width=80, bg="#111827", fg="#00E5FF", font=('Consolas', 10), bd=1, relief="solid")
        self.audit_results.pack(pady=20)
        self.audit_results.insert(tk.END, ">>> WAITING FOR TARGET INGESTION...\n")
        self.audit_results.config(state=tk.DISABLED)

    def _build_crack_tab(self):
        ttk.Label(self.tab_crack, text="VULNERABILITY TARGETING (SMART CRACK)", style="Header.TLabel").pack(pady=20)
        ttk.Label(self.tab_crack, text="Reduces keyspace by isolating anomalies. Contains Full Crack PoC for Toy Ciphers.", foreground="#94A3B8").pack()
        
        self.lbl_crack_file = ttk.Label(self.tab_crack, text="No target selected")
        self.lbl_crack_file.pack(pady=10)
        
        ttk.Button(self.tab_crack, text="LOAD TARGET", command=self.select_crack_file).pack(pady=5)
        
        frame_btns = ttk.Frame(self.tab_crack)
        frame_btns.pack(pady=10)
        
        ttk.Button(frame_btns, text="SCAN VULNERABILITIES (AES/RSA)", command=self.run_crack_scan).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_btns, text="FULL CRACK (TOY CIPHER PoC)", command=self.run_full_crack_poc).pack(side=tk.LEFT, padx=5)
        
        self.crack_results = tk.Text(self.tab_crack, height=14, width=80, bg="#111827", fg="#FF3366", font=('Consolas', 10), bd=1, relief="solid")
        self.crack_results.pack(pady=10)
        
    def _build_encrypt_tab(self):
        ttk.Label(self.tab_encrypt, text="GEOMETRIC ENCRYPTION ENGINE", style="Header.TLabel").pack(pady=20)
        
        self.lbl_enc_file = ttk.Label(self.tab_encrypt, text="No file selected")
        self.lbl_enc_file.pack(pady=10)
        
        ttk.Button(self.tab_encrypt, text="SELECT FILE", command=self.select_enc_file).pack(pady=5)
        
        ttk.Label(self.tab_encrypt, text="Passkey (4 bytes for Toy Cipher):").pack(pady=5)
        self.ent_key = ttk.Entry(self.tab_encrypt, show="*", width=40, font=('Consolas', 10))
        self.ent_key.pack(pady=5)
        
        self.enc_mode = tk.StringVar(value="UTF-T")
        ttk.Radiobutton(self.tab_encrypt, text="Secure UTF-T Möbius Folding (Quantum Resistant)", variable=self.enc_mode, value="UTF-T").pack(pady=5)
        ttk.Radiobutton(self.tab_encrypt, text="Legacy Toy Cipher (Vulnerable to PoC Crack)", variable=self.enc_mode, value="TOY").pack(pady=5)
        
        frame_btns = ttk.Frame(self.tab_encrypt)
        frame_btns.pack(pady=20)
        
        ttk.Button(frame_btns, text="FOLD (ENCRYPT)", command=self.run_encrypt).pack(side=tk.LEFT, padx=10)
        ttk.Button(frame_btns, text="UNFOLD (DECRYPT)", command=self.run_decrypt).pack(side=tk.LEFT, padx=10)

    # --- Actions ---
    
    def select_audit_file(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            self.lbl_audit_file.config(text=os.path.basename(filepath))
            self.run_audit(filepath)
            
    def run_audit(self, filepath):
        self.audit_results.config(state=tk.NORMAL)
        self.audit_results.delete(1.0, tk.END)
        self._write_audit(">>> INGESTING TARGET...\n")
        self.root.update()
        time.sleep(0.5)
        self._write_audit(">>> MAPPING TO MÖBIUS MANIFOLD...\n")
        self.root.update()
        
        results = self.engine.audit_file(filepath)
        
        out = f"""
[+] AUDIT COMPLETE

>> ENTROPY INDEX:       {results['entropy']} / 8.0
>> ESTIMATED ALGORITHM: {results['algorithm_guess']}
>> GENUS VARIANCE:      {results['genus_variance']}
>> VULNERABILITY SCORE: {results['vulnerability_score']}

[!] TOPOLOGICAL FINGERPRINT (KEY COLLISION HASH):
    {results['fingerprint']}
"""
        self._write_audit(out)

    def _write_audit(self, text):
        self.audit_results.config(state=tk.NORMAL)
        self.audit_results.insert(tk.END, text)
        self.audit_results.see(tk.END)
        self.audit_results.config(state=tk.DISABLED)

    def select_crack_file(self):
        self.crack_filepath = filedialog.askopenfilename()
        if self.crack_filepath:
            self.lbl_crack_file.config(text=os.path.basename(self.crack_filepath))

    def run_crack_scan(self):
        if not hasattr(self, 'crack_filepath') or not self.crack_filepath:
            messagebox.showerror("Error", "Select a target first.")
            return
            
        self.crack_results.config(state=tk.NORMAL)
        self.crack_results.delete(1.0, tk.END)
        self.crack_results.insert(tk.END, ">>> SCANNING MANIFOLD FOR RED-TENSION ANOMALIES...\n")
        self.root.update()
        time.sleep(1) 
        
        weaknesses = self.engine.crack_assist(self.crack_filepath)
        
        if not weaknesses:
            self.crack_results.insert(tk.END, "[-] No extreme vulnerabilities found in sample.\n")
        else:
            self.crack_results.insert(tk.END, "[!] VULNERABILITIES ISOLATED. CRACK PATH IDENTIFIED:\n\n")
            for offset, byte, dev in weaknesses:
                self.crack_results.insert(tk.END, f"    OFFSET: {offset} | RAW_BYTE: 0x{byte:02x} | TENSION_DEVIATION: {dev}%\n")
            self.crack_results.insert(tk.END, "\n>>> BRUTE FORCE VECTOR REDUCED. TARGET THESE OFFSETS.\n")
        self.crack_results.config(state=tk.DISABLED)

    def run_full_crack_poc(self):
        """Proof of concept crack for the legacy toy cipher."""
        if not hasattr(self, 'crack_filepath') or not self.crack_filepath:
            messagebox.showerror("Error", "Select a target first.")
            return
            
        self.crack_results.config(state=tk.NORMAL)
        self.crack_results.delete(1.0, tk.END)
        self.crack_results.insert(tk.END, ">>> INITIATING FULL CRYPTANALYTIC PoC CRACK...\n")
        self.crack_results.insert(tk.END, ">>> MAPPING TOPOLOGICAL FREQUENCY DEVIATIONS...\n")
        self.root.update()
        time.sleep(1)
        
        out_path = self.crack_filepath.replace(".toy", "") + ".cracked"
        extracted_key = self.engine.full_crack_poc(self.crack_filepath, out_path)
        
        if extracted_key:
            self.crack_results.insert(tk.END, f"\n[!] KEY EXTRACTED: {extracted_key}\n")
            self.crack_results.insert(tk.END, f"[+] FILE DECRYPTED AND SAVED TO:\n    {os.path.basename(out_path)}\n")
        else:
            self.crack_results.insert(tk.END, "[-] CRACK FAILED. File may not be a Toy Cipher.\n")
            
        self.crack_results.config(state=tk.DISABLED)

    def select_enc_file(self):
        self.enc_filepath = filedialog.askopenfilename()
        if self.enc_filepath:
            self.lbl_enc_file.config(text=os.path.basename(self.enc_filepath))

    def run_encrypt(self):
        if not hasattr(self, 'enc_filepath'): return
        key = self.ent_key.get()
        if not key:
            messagebox.showwarning("Warning", "Enter a passkey.")
            return
            
        mode = self.enc_mode.get()
        if mode == "UTF-T":
            out_path = self.enc_filepath + ".mtc"
            self.engine.topological_encrypt(self.enc_filepath, out_path, key)
            messagebox.showinfo("Success", f"File Folded (UTF-T) to:\n{out_path}")
        else:
            if len(key) != 4:
                messagebox.showwarning("Warning", "Toy cipher requires exactly a 4-character key for PoC.")
                return
            out_path = self.enc_filepath + ".toy"
            self.engine.toy_encrypt(self.enc_filepath, out_path, key)
            messagebox.showinfo("Success", f"File Encrypted (Legacy Toy) to:\n{out_path}")
        
    def run_decrypt(self):
        if not hasattr(self, 'enc_filepath'): return
        key = self.ent_key.get()
        if not key:
            messagebox.showwarning("Warning", "Enter a passkey.")
            return
            
        # Decrypt only works on UTF-T, the Toy Cipher is meant to be cracked
        if self.enc_mode.get() != "UTF-T":
            messagebox.showinfo("Info", "To decrypt the Toy Cipher, please use the FULL CRACK PoC feature in the Crack Assist tab to prove the theory!")
            return
            
        out_path = self.enc_filepath.replace(".mtc", "")
        if out_path == self.enc_filepath:
            out_path += ".unfolded"
            
        self.engine.topological_decrypt(self.enc_filepath, out_path, key)
        messagebox.showinfo("Success", f"File Unfolded to:\n{out_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MCSInterface(root)
    root.mainloop()
