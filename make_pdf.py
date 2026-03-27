from fpdf import FPDF
import re

with open("Quantum_Moebius_Parity_Equilibrium.md", "r", encoding="utf-8") as f:
    raw_text = f.read()

text = raw_text.replace("**", "").replace("__", "")
text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)

pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", size=11)
cleaned_text = text.encode('latin-1', 'replace').decode('latin-1')

pdf.multi_cell(0, 5, txt=cleaned_text)
pdf.output("Quantum_Moebius_Parity_Equilibrium.pdf")
print("PDF Generation Complete.")
