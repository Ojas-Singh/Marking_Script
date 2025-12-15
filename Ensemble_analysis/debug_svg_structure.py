from glycowork.motif.draw import GlycoDraw
from glycowork.motif.processing import glytoucan_to_glycan, canonicalize_iupac
import tempfile
import os

def debug_svg():
    # glycan_id = 'G63041RA'
    # print(f"Fetching {glycan_id}...")
    iupac = "Man(a1-3)Man(b1-4)GlcNAc"
    print(f"Using hardcoded {iupac}...")
    
    try:
        iupac = canonicalize_iupac(iupac)
        print(f"Canonicalized: {iupac}")
    except Exception as e:
        print(f"Canonicalization failed: {e}")

    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as tmp:
        tmp_path = tmp.name
        
    print(f"Drawing to {tmp_path}...")
    GlycoDraw(iupac, filepath=tmp_path, suppress=True)
    
    if os.path.exists(tmp_path):
        with open(tmp_path, 'r') as f:
            content = f.read()
        print("--- SVG START ---")
        print(content[:2000]) # Print first 2000 chars
        print("--- SVG END ---")
        os.remove(tmp_path)
    else:
        print("File not generated.")

if __name__ == "__main__":
    debug_svg()
