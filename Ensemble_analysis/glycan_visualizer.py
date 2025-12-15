import os
from glycowork.motif.draw import GlycoDraw
from glycowork.motif.processing import glytoucan_to_glycan, canonicalize_iupac
# from glycowork.glycan_data.loader import lib
import tempfile
import re

def generate_glycan_svg(glytoucan_id):
    """
    Generates an SVG string for the given GlyTouCan ID using GlycoDraw.
    Returns the SVG string and the Glycowork graph object (if available).
    """
    # Try to get IUPAC
    iupac = None
    try:
        iupac = glytoucan_to_glycan(glytoucan_id)
        if isinstance(iupac, list):
             # Sometimes it returns list of chars if not found? logic check
             # But if it works, it returns a string.
             # fallback to hardcoded if known
             if glytoucan_id == 'G00026MO':
                 # Fallback IUPAC if fetch fails (Deduced M5/hybrid structure)
                 # Man(a1-3)[Man(a1-6)]Man(b1-4)GlcNAc(b1-4)GlcNAc ... 
                 # Let's try passing ID directly to GlycoDraw if fetching fails
                 iupac = glytoucan_id
             elif glytoucan_id == 'G00028MO':
                 iupac = glytoucan_id
             else:
                 iupac = glytoucan_id # Try ID
    except:
        iupac = glytoucan_id # Try ID directly
        
    # Canonicalize
    try:
        if iupac:
            iupac = canonicalize_iupac(iupac)
    except Exception as e:
        print(f"Error canonicalizing IUPAC: {e}")

    # Generate Drawing
    # GlycoDraw writes to file if filepath provided, or returns drawing?
    # Signature: GlycoDraw(glycan_string, filepath=None, ...)
    # If filepath=None, it usually displays.
    # We want SVG string.
    
    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # GlycoDraw might use matplotlib or other backend.
        # User snippet: `drawing = GlycoDraw("G00026MO", suppress=True)`
        # If suppress=True, maybe it returns the object?
        
        drawing = GlycoDraw(iupac, filepath=tmp_path, suppress=True)
        
        # Read the SVG file
        if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 0:
            with open(tmp_path, 'r') as f:
                svg_content = f.read()
            return svg_content, iupac
        else:
            # Maybe drawing object allows saving?
            if hasattr(drawing, 'save_svg'):
                # it might be drawsvg object
                return drawing.as_svg(), iupac
            
            return None, iupac
            
    except Exception as e:
        print(f"Error drawing glycan: {e}")
        return None, iupac
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except:
                pass

def inject_interaction(svg_string, mapping_dict=None):
    """
    Injects IDs into the SVG elements to make them clickable with streamlit-click-detector.
    GlycoDraw (drawsvg) typically uses <use> tags referencing symbols for shapes.
    We assume the order of <use> tags for residue shapes corresponds to the node indices.
    """
    if not svg_string:
        return ""
        
    # Pattern to find <use ...xlink:href="#..." ... /> or <use ...href="#..." ... />
    # We want to inject id="residue_X" into these tags.
    # Exclude text or paths if possible. Usually residues are the main <use> elements.
    # Linkages might also be <use> or <path>. Linkages often don't use symbols like squares/circles.
    # Residue symbols: #Square, #Circle, etc. or #d1, #d2.
    
    # Let's find all <use> tags.
    # We will wrap the ID injection in a function to increment counter.
    
    count = 0
    
    def replacer(match):
        nonlocal count
        tag_content = match.group(0)
        
        # Heuristic: Check if likely a residue shape.
        # Often valid residues have x, y coordinates.
        # If it's a bond, it might be a path.
        # GlycoDraw uses <use> for shapes.
        
        # Inject ID
        # We assume the first N <use> tags are the N residues.
        # This is a bold assumption.
        new_id = f'residue_{count}'
        
        # Add a class for CSS styling if supported (hover effect)
        # click-detector doesn't support CSS effectively inside standard Streamlit unless we inject style block.
        # But id is key.
        
        # Insert id before the closing /> or >
        if "id=" in tag_content:
            # Already has ID?
            pass
        else:
            # Insert id
            # Find insertion point (before closing)
            new_content = tag_content.rstrip("/>").rstrip(">") + f' id="{new_id}" >' if tag_content.endswith(">") and not tag_content.endswith("/>") else tag_content.replace("/>", f' id="{new_id}" />')
            
            # Update content
            # If it was a simple tag
            if new_content == tag_content: # replace failed
                 new_content = tag_content[:-1] + f' id="{new_id}" >'
                 
            count += 1
            return new_content
            
        return tag_content

    # Regex for <use ... />
    # Note: re.sub with function
    # We target <use ... > or <use ... />
    # <use[^>]+>
    
    # We only want to target residues.
    # Inspecting debug output might help filtering.
    # For now, we target valid shape uses.
    
    modified_svg = re.sub(r'<use[^>]+>', replacer, svg_string)
    
    # Also inject some CSS style for hover effect on these IDs?
    style_block = """
    <style>
        [id^="residue_"] {
            cursor: pointer;
            transition: all 0.2s;
        }
        [id^="residue_"]:hover {
            opacity: 0.7;
            stroke: black;
            stroke-width: 2px;
        }
    </style>
    """
    
    # Insert style at start of SVG
    modified_svg = modified_svg.replace("<svg ", f"<svg {style_block} ")
    
    return modified_svg
