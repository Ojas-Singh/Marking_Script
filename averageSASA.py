import streamlit as st
from Bio.PDB import PDBParser, PDBIO, Select
from io import StringIO, BytesIO
import numpy as np

# Custom Select class to include all atoms
class AllAtoms(Select):
    def accept_atom(self, atom):
        return True

def parse_pdb(file):
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure('structure', file)
    return structure

def get_atom_key(atom):
    """
    Create a unique key for each atom based on chain, residue, and atom name.
    """
    return (
        atom.get_parent().get_parent().id,  # Chain ID
        atom.get_parent().id[1],            # Residue number
        atom.get_name()                     # Atom name
    )

def average_bvalues(structures):
    """
    Average B-values across multiple structures.
    Assumes all structures have the same atoms in the same order.
    """
    atom_bvals = {}
    atom_order = []

    for idx, structure in enumerate(structures):
        for model in structure:
            for chain in model:
                for residue in chain:
                    for atom in residue:
                        key = get_atom_key(atom)
                        if idx == 0:
                            atom_order.append(key)
                            atom_bvals[key] = [atom.get_bfactor()]
                        else:
                            if key in atom_bvals:
                                atom_bvals[key].append(atom.get_bfactor())
                            else:
                                st.warning(f"Atom {key} not found in all structures.")
                                # Handle missing atoms by skipping or filling with NaN
                                atom_bvals[key] = atom_bvals.get(key, []) + [np.nan]

    # Compute average, ignoring NaN
    averaged_bvals = {}
    for key in atom_order:
        bvals = atom_bvals.get(key, [])
        if bvals:
            averaged_bvals[key] = np.nanmean(bvals)
        else:
            averaged_bvals[key] = 0.0  # Default value if no B-values

    return averaged_bvals, atom_order

def create_averaged_structure(structure, averaged_bvals):
    """
    Create a new structure with averaged B-values.
    """
    # Clone the structure to avoid modifying the original
    from copy import deepcopy
    new_structure = deepcopy(structure)

    for model in new_structure:
        for chain in model:
            for residue in chain:
                for atom in residue:
                    key = get_atom_key(atom)
                    if key in averaged_bvals:
                        atom.set_bfactor(averaged_bvals[key])
    return new_structure

def structure_to_pdb(structure):
    """
    Convert a Biopython structure to PDB format string.
    """
    io = PDBIO()
    io.set_structure(structure)
    string_io = StringIO()
    io.save(string_io, select=AllAtoms())
    return string_io.getvalue()

def main():
    st.title("Average B-values from Multiple PDB Files")

    st.markdown("""
    Upload multiple PDB files to calculate the average B-values (temperature factors) across them.
    The app will generate a new PDB file with the averaged B-values.
    """)

    uploaded_files = st.file_uploader("Choose PDB files", type=["pdb"], accept_multiple_files=True)

    if uploaded_files:
        if len(uploaded_files) < 2:
            st.warning("Please upload at least two PDB files to compute averages.")
        else:
            with st.spinner("Processing PDB files..."):
                try:
                    structures = [parse_pdb(file) for file in uploaded_files]
                    averaged_bvals, atom_order = average_bvalues(structures)

                    # Use the first structure as a template
                    template_structure = structures[0]
                    averaged_structure = create_averaged_structure(template_structure, averaged_bvals)
                    pdb_string = structure_to_pdb(averaged_structure)

                    st.success("Averaged B-values computed successfully!")

                    # Provide download link
                    st.download_button(
                        label="Download Averaged PDB",
                        data=pdb_string,
                        file_name="averaged_bvalues.pdb",
                        mime="chemical/x-pdb"
                    )

                except Exception as e:
                    st.error(f"An error occurred: {e}")

    st.markdown("""
    ---
    **Note:**
    - Ensure that all uploaded PDB files have the same number of atoms and the atoms are in the same order.
    - The app matches atoms based on Chain ID, Residue Number, and Atom Name.
    """)

if __name__ == "__main__":
    main()
