import os

replacements = {
    'Ã¶': 'ö',
    'â€”': '—',
    'â€': '—',
    'MA bius': 'Möbius',
    'MAoebius': 'Möbius'
}

files = [
    r'c:\Users\Jerry\.gemini\antigravity\playground\ruby-cosmic\Quantum_Moebius_Parity_Equilibrium.md',
    r'C:\ResidentAGI\BSD-Torus-Engine\Birch_and_Swinnerton_Dyer_Proof.md',
    r'c:\Users\Jerry\.gemini\antigravity\playground\ruby-cosmic\README.md',
    r'C:\ResidentAGI\BSD-Torus-Engine\README.md',
    r'c:\Users\Jerry\.gemini\antigravity\playground\ruby-cosmic\explainer.md',
    r'C:\ResidentAGI\BSD-Torus-Engine\explainer.md',
    r'c:\Users\Jerry\.gemini\antigravity\playground\ruby-cosmic\Unified_Topological_Field_Theory.md',
    r'C:\ResidentAGI\BSD-Torus-Engine\Unified_Topological_Field_Theory.md'
]

for file_path in files:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        for old, new in replacements.items():
            content = content.replace(old, new)
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {file_path}")
