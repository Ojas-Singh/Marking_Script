# app.py

import streamlit as st
from io import StringIO, BytesIO
import tempfile
import os
from pymol import cmd, finish_launching
import shutil

# Initialize PyMOL
finish_launching(['pymol', '-cq'])  # '-c' for no GUI, '-q' for quiet

def get_residues(pdb_content):
    """
    Parses the PDB content and extracts a list of residues.
    Returns a list of tuples: (chain, residue number, residue name).
    """
    residues = []
    for line in pdb_content.splitlines():
        if line.startswith("ATOM") or line.startswith("HETATM"):
            chain = line[21]
            res_num = line[22:26].strip()
            res_name = line[17:20].strip()
            residue = (chain, res_num, res_name)
            if residue not in residues:
                residues.append(residue)
    return residues

def perform_mutation(pdb_path, chain, res_num, new_res):
    """
    Uses PyMOL to mutate a specified residue to a new residue.
    """
    cmd.load(pdb_path, 'structure')
    selection = f'/structure//{chain}/{res_num}/'
    cmd.wizard("mutagenesis")
    cmd.refresh_wizard()
    cmd.get_wizard().set_mode(new_res)
    cmd.get_wizard().do_select(selection)
    cmd.get_wizard().apply()
    cmd.save('mutated.pdb')
    cmd.delete('all')

def main():
    st.title("PDB Residue Mutator")
    st.write("""
        Upload a PDB file, select a residue to mutate, specify the mutation, and download the mutated PDB file.
    """)

    uploaded_file = st.file_uploader("Upload your PDB file", type=["pdb"])

    if uploaded_file is not None:
        pdb_content = uploaded_file.read().decode('utf-8')
        residues = get_residues(pdb_content)

        # Display residues in a selectbox
        st.subheader("Select Residue to Mutate")
        residue_options = [f"Chain {res[0]} | Residue {res[1]} | {res[2]}" for res in residues]
        selected_residue = st.selectbox("Residue", residue_options)

        # Mutation selection
        st.subheader("Select Mutation")
        # For simplicity, provide a list of standard amino acids
        amino_acids = [
            'ALA', 'ARG', 'ASN', 'ASP', 'CYS',
            'GLN', 'GLU', 'GLY', 'HIS', 'ILE',
            'LEU', 'LYS', 'MET', 'PHE', 'PRO',
            'SER', 'THR', 'TRP', 'TYR', 'VAL'
        ]
        new_residue = st.selectbox("Mutation", amino_acids)

        if st.button("Mutate"):
            with st.spinner('Performing mutation...'):
                # Extract chain and residue number
                parts = selected_residue.split('|')
                chain = parts[0].split()[-1].strip()
                res_num = parts[1].split()[-1].strip()

                # Create a temporary directory
                with tempfile.TemporaryDirectory() as tmpdirname:
                    pdb_path = os.path.join(tmpdirname, 'original.pdb')
                    with open(pdb_path, 'w') as f:
                        f.write(pdb_content)
                    
                    try:
                        perform_mutation(pdb_path, chain, res_num, new_residue)
                        mutated_pdb_path = os.path.join(tmpdirname, 'mutated.pdb')
                        with open(mutated_pdb_path, 'rb') as f:
                            mutated_pdb = f.read()
                        
                        st.success("Mutation successful!")
                        st.download_button(
                            label="Download Mutated PDB",
                            data=mutated_pdb,
                            file_name='mutated.pdb',
                            mime='chemical/x-pdb'
                        )
                    except Exception as e:
                        st.error(f"An error occurred during mutation: {e}")

if __name__ == "__main__":
    main()
