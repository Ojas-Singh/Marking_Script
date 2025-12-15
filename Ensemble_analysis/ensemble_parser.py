import mdtraj as md
import networkx as nx
import re

def parse_ensemble_remarks(pdb_file_path):
    """
    Parses the custom REMARK lines in the ensemble PDB to extract glycan metadata.
    Returns a dictionary keyed by Chain ID containing Glycan ID and other metadata.
    """
    metadata = {}
    
    # We only need to read the remarks from the first model/frame generally, 
    # but the format implies it might be repeated. 
    # Let's read until we hit the first MODEL or ATOM record.
    with open(pdb_file_path, 'r') as f:
        for line in f:
            if line.startswith("MODEL") or line.startswith("ATOM"):
                break
            if line.startswith("REMARK"):
                # Example: REMARK    Chain B Glycan: G00026MO
                match_glycan = re.search(r"Chain\s+(\w+)\s+Glycan:\s+(\w+)", line)
                if match_glycan:
                    chain_id, glycan_id = match_glycan.groups()
                    if chain_id not in metadata:
                        metadata[chain_id] = {}
                    metadata[chain_id]['glycan_id'] = glycan_id
                
                # We can extract other fields if needed, like cluster_index, etc.
                
    return metadata

def load_trajectory(pdb_file_path):
    """
    Loads the PDB file using MDTraj.
    """
    traj = md.load(pdb_file_path)
    return traj

def build_pdb_graph(traj, chain_id):
    """
    Builds a NetworkX graph for a specific chain in the PDB topology.
    Nodes are PDB residue indices (0-indexed relative to whole structure or chain? let's use residue object).
    Edges are bonds.
    """
    G = nx.Graph()
    
    # Get the chain object
    # MDTraj chains are indexed numerically. We need to map chain_id (str) to index.
    # MDTraj doesn't easily expose chain 'IDs' (like 'A', 'B') directly in all versions 
    # as easily as one might hope, but we can iterate.
    
    target_chain = None
    # Topology tables usually have chainID column if loaded from PDB
    # But md.Topology chains are just objects. 
    # We can rely on the fact that typical PDBs have chain IDs. 
    # Let's search for the chain.
    
    # Efficient way: create a map first
    chain_map = {}
    for chain in traj.topology.chains:
        # mdtraj 1.9+ might use chain.chain_id if available, or we check the first atom
        # But 'chain.index' is just 0, 1, 2...
        # 'chainID' is often stored in atom metadata
        cid = chain.atom(0).segment_id # Sometimes segment_id hold chain ID in some parsers?
        # Actually standard PDB reader in mdtraj stores chainID.
        # Let's check residue 0 of the chain.
        # PDB parsing in mdtraj is sometimes tricky with chain IDs.
        # A safer fallback is usually chain.index but we have 'B', 'C' from remarks.
        
        # NOTE: In MDTraj > 1.9, top.to_dataframe() gives a DataFrame with 'chainID' column.
        pass

    # Let's use the table approach to find the index corresponding to chain_id
    df_atoms, df_bonds = traj.topology.to_dataframe()
    
    # Filter atoms by chainID
    if 'chainID' not in df_atoms.columns:
        # Fallback if mdtraj fails to parse chainIDs correctly (unlikely for proper PDBs)
        # We might need to guess or assume order.
        # But let's assume it works.
        # If segmentID is present, check that.
        pass

    # Actually, let's just use the dataframe index to filter
    chain_atoms = df_atoms[df_atoms['chainID'] == chain_id]
    
    if chain_atoms.empty:
        # Try finding by index if user passes int? No, metadata key is 'B'.
        # Maybe chainID is not populated. 
        # Let's print unique chainIDs for debugging if this fails, but for now specific logic:
        pass
        
    # Get bonds
    # MDTraj topology bonds are between atoms.
    # We want a RESIDUE graph. 
    # Two residues are connected if any of their atoms are connected.
    
    # Get residue objects for this chain
    # We need to map chain_id to mdtraj chain index
    # Let's iterate atoms and find the chain index
    # Get bond
    # MDTraj topology bonds are between atoms.
    # We want a RESIDUE graph. 
    # Two residues are connected if any of their atoms are connected.
    
    # Get residue objects for this chain
    # We need to map chain_id to mdtraj chain index
    
    # Check if chainID is in columns
    if 'chainID' not in df_atoms.columns:
        print("Warning: chainID column not found in topology dataframe.")
        return None

    chain_atoms_rows = df_atoms[df_atoms['chainID'] == chain_id]
    
    if chain_atoms_rows.empty:
        # Fallback: MDTraj might have converted Chain IDs to integers (0, 1, 2...)
        # Try mapping 'A'->0, 'B'->1, etc. or just try integer conversion.
        # Heuristic: If chain_id is 'A', 'B', etc., try to find corresponding integer index.
        # But we don't strictly know 'A' is 0. 
        # However, usually PDB order is preserved.
        
        # Let's try to infer from metadata keys if possible, but here we only have single chain_id.
        # Let's try to map A->0, B->1.
        
        predicted_index = -1
        if len(chain_id) == 1 and chain_id.isalpha():
            predicted_index = ord(chain_id.upper()) - ord('A')
            
        if predicted_index >= 0:
             chain_atoms_rows = df_atoms[df_atoms['chainID'] == predicted_index]
    
    if chain_atoms_rows.empty:
        print(f"Chain {chain_id} (or mapped index) not found in topology.")
        return None
    
    # Get the MDTraj "Residue" objects for this chain
    # We can get the first atom's index, then get its chain object
    first_atom_idx = chain_atoms_rows.index[0] # dataframe index corresponds to atom index
    chain_obj = traj.topology.atom(first_atom_idx).residue.chain
    chain_idx = chain_obj.index
    
    for residue in chain_obj.residues:
        # Node ID: residue.index (global index) or we can use a custom ID
        # Let's use residue object or index. Index is safer for mdtraj lookups.
        G.add_node(residue.index, name=residue.name, resSeq=residue.resSeq)
    
    # Determine connectivity
    # If topology has bonds, use them.
    # Check if there are any bonds in the chain
    # But usually if CONECT is missing, there are 0 bonds.
    
    chain_bonds = []
    # Check existing bonds
    # Iterate all topology bonds
    bonds_found = False
    for bond in traj.topology.bonds:
        r1 = bond[0].residue
        r2 = bond[1].residue
        if r1.chain.index == chain_idx and r2.chain.index == chain_idx:
            chain_bonds.append((bond[0], bond[1]))
            bonds_found = True
            
    if not bonds_found:
        # Infer bonds by distance
        # print("Inferring bonds by distance < 1.65 Angstroms...")
        # Get atom indices and coordinates
        atoms = list(chain_obj.atoms)
        atom_indices = [a.index for a in atoms]
        xyz = traj.xyz[0, atom_indices, :] * 10.0 # Convert nm to Angstroms
        
        # Simple N^2 check
        import numpy as np
        coords = xyz
        n_atoms = len(atoms)
        threshold = 2.0 # Increased to catch stretched bonds
        threshold_sq = threshold ** 2
        
        for i in range(n_atoms):
            for j in range(i + 1, n_atoms):
                # Dist check
                d2 = np.sum((coords[i] - coords[j])**2)
                if d2 < threshold_sq:
                    # Found a bond
                    a1 = atoms[i]
                    a2 = atoms[j]
                    chain_bonds.append((a1, a2))

    # Build Residue Graph from Atom Bonds
    for a1, a2 in chain_bonds:
        r1 = a1.residue
        r2 = a2.residue
        if r1 != r2:
             G.add_edge(r1.index, r2.index)
                
    return G
