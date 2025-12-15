import networkx as nx
from networkx.algorithms import isomorphism
# from glycowork.glycan_data.loader import lib # Not using lib directly anymore
from glycowork.motif.graph import glycan_to_nxGraph
from glycowork.motif.processing import glytoucan_to_glycan
import pandas as pd

def get_glycan_graph(glytoucan_id):
    """
    Retrieves the IUPAC string for a GlyTouCan ID and converts it to a NetworkX graph.
    """
    try:
        print(f"Fetching IUPAC for {glytoucan_id}...")
        iupac = glytoucan_to_glycan(glytoucan_id)
        
        if iupac:
            print(f"IUPAC found: {iupac}")
            g = glycan_to_nxGraph(iupac)
            return g, iupac
        else:
            print(f"ID {glytoucan_id} returned no IUPAC string.")
            return None, None
            
    except Exception as e:
        print(f"Error fetching glycan graph: {e}")
        return None, None

def match_pdb_to_glycan(pdb_graph, glycan_graph):
    """
    Matches the PDB residue graph to the Glycowork glycan graph.
    Returns a dictionary mapping {Glycowork_Node_ID : PDB_Residue_Index}.
    """
    
    # Define node match function
    # PDB nodes have 'name' (3-letter code, e.g., MAN, NAG)
    # Glycowork nodes usually have 'string_labels' or similar representing monosaccharide type.
    
    # We need a translation layer.
    # e.g. MAN -> Man, NAG -> GlcNAc
    # This might require a heuristic map.
    
    pdb_to_iupac_map = {
        'NAG': 'GlcNAc',
        'MAN': 'Man',
        'BMA': 'Man', # Beta-mannose often BMA in PDB
        'FUC': 'Fuc',
        'GAL': 'Gal',
        'GLA': 'Gal', # Sometimes
        'SIA': 'Neu5Ac',
        'NGN': 'Neu5Gc',
        # Add more as needed
    }
    
    def node_match(n1, n2):
        # n1 is from G1 (PDB), attributes: {'name': 'MAN', ...}
        # n2 is from G2 (Glycowork), attributes: {'string_labels': 'Man', ...} (check actual attr name)
        
        # Glycowork graphs typically put the monosaccharide name in 'string_labels' or 'labels'?
        # Let's assume 'string_labels' based on recent glycowork versions, or 'labels'.
        # We'll check both or be flexible.
        
        pdb_res = n1.get('name', '')
        glyco_lbl = n2.get('string_labels', n2.get('labels', ''))
        
        # Translate PDB to IUPAC-ish
        # We check if the standardized PDB name maps to the Glycowork label
        # Simple containment or equality check
        
        expected_type = pdb_to_iupac_map.get(pdb_res, pdb_res)
        
        # Glycowork labels might include linkage info? "Man(a1-3)"? 
        # Usually nodes are just monosaccharides.
        
        return expected_type.lower() in glyco_lbl.lower()

    GM = isomorphism.GraphMatcher(pdb_graph, glycan_graph, node_match=node_match)
    
    if GM.is_isomorphic():
        # Returns mapping G1_node -> G2_node
        # We want to know which PDB node corresponds to which Glyco node
        print("Isomorphic match found!")
        return GM.mapping
    elif GM.subgraph_is_isomorphic():
         print("Subgraph match found!")
         return GM.mapping
    else:
        print("No match found.")
        return None
