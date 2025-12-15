import mdtraj as md
import numpy as np

def calculate_residue_sasa(traj, residue_index, probe_radius=0.14):
    """
    Calculates the SASA for a specific residue across all frames in the trajectory.
    Returns an array of SASA values (nm^2).
    """
    # shrake_rupley returns (n_frames, n_atoms)
    # We need to compute SASA for the whole complex (or just the chain?), 
    # extract atoms belonging to the residue, and sum/average them?
    # Usually residue SASA is the sum of atomic SASAs in that residue.
    
    sasa = md.shrake_rupley(traj, probe_radius=probe_radius, mode='atom')
    
    # Get atom indices for the residue
    # We assume 'residue_index' is the global index in the topology
    residue = traj.topology.residue(residue_index)
    atom_indices = [atom.index for atom in residue.atoms]
    
    # Sum SASA for these atoms
    # sasa shape: (n_frames, n_atoms)
    residue_sasa = sasa[:, atom_indices].sum(axis=1)
    
    return residue_sasa
