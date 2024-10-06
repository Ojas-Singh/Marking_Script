import streamlit as st
from io import StringIO, BytesIO
import tempfile
import os
from pymol import cmd, finish_launching
import shutil

# Initialize PyMOL
# finish_launching(['pymol', '-cq'])  # '-c' for no GUI, '-q' for quiet

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

def perform_mutation(pdb_path, mutations, output_path):
    """
    Uses PyMOL to mutate multiple residues to new residues and saves the result.
    `mutations` is a list of tuples in the format (chain, res_num, new_res).
    """
    try:
        cmd.load(pdb_path, 'structure')
        for mutation in mutations:
            chain, res_num, new_res = mutation
            selection = f'/structure//{chain}/{res_num}/'
            cmd.wizard("mutagenesis")
            cmd.refresh_wizard()
            cmd.get_wizard().set_mode(new_res)
            cmd.get_wizard().do_select(selection)
            cmd.get_wizard().apply()
        cmd.save(output_path)  # Save the final mutated file
        cmd.delete('all')  # Clean up PyMOL session
    except Exception as e:
        raise RuntimeError(f"Error in PyMOL mutation: {e}")

def main():
    st.title("PDB Residue Mutator (Multiple Mutations)")
    st.write("""
        Upload a PDB file, select multiple residues to mutate, specify mutations, and download the mutated PDB file.
    """)

    uploaded_file = st.file_uploader("Upload your PDB file", type=["pdb"])

    if uploaded_file is not None:
        pdb_content = uploaded_file.read().decode('utf-8')
        residues = get_residues(pdb_content)

        # Display residues in a selectbox for multiple selection
        st.subheader("Select Residues to Mutate")
        residue_options = [f"Chain {res[0]} | Residue {res[1]} | {res[2]}" for res in residues]
        selected_residues = st.multiselect("Select Residue(s)", residue_options)

        # Ensure that at least one residue is selected
        if selected_residues:
            # Mutation selection for each selected residue
            st.subheader("Select Mutations")
            mutation_combos = []
            for selected_residue in selected_residues:
                parts = selected_residue.split('|')
                chain = parts[0].split()[-1].strip()
                res_num = parts[1].split()[-1].strip()

                # Select a mutation for each selected residue
                amino_acids = [
                    'ALA', 'ARG', 'ASN', 'ASP', 'CYS',
                    'GLN', 'GLU', 'GLY', 'HIS', 'ILE',
                    'LEU', 'LYS', 'MET', 'PHE', 'PRO',
                    'SER', 'THR', 'TRP', 'TYR', 'VAL'
                ]
                new_residue = st.selectbox(f"Select mutation for Chain {chain}, Residue {res_num}", amino_acids, key=f"{chain}_{res_num}")
                mutation_combos.append((chain, res_num, new_residue))

            if st.button("Mutate"):
                with st.spinner('Performing mutations...'):
                    # Create a temporary directory
                    with tempfile.TemporaryDirectory() as tmpdirname:
                        pdb_path = os.path.join(tmpdirname, 'original.pdb')
                        mutated_pdb_path = os.path.join(tmpdirname, 'mutated.pdb')  # Define mutated file path here

                        # Write the original PDB to the temporary directory
                        with open(pdb_path, 'w') as f:
                            f.write(pdb_content)

                        try:
                            # Perform mutations one by one
                            perform_mutation(pdb_path, mutation_combos, mutated_pdb_path)

                            # Ensure the mutated file exists before trying to read it
                            if os.path.exists(mutated_pdb_path):
                                with open(mutated_pdb_path, 'rb') as f:
                                    mutated_pdb = f.read()

                                st.success("Mutation successful!")
                                st.download_button(
                                    label="Download Mutated PDB",
                                    data=mutated_pdb,
                                    file_name='mutated.pdb',
                                    mime='chemical/x-pdb'
                                )
                            else:
                                st.error("The mutated PDB file could not be found.")
                        except Exception as e:
                            st.error(f"An error occurred during mutation: {e}")

if __name__ == "__main__":
    main()
