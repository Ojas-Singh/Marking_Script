import streamlit as st
import os
import ensemble_parser
import analysis
import glycan_visualizer
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import networkx as nx
import tempfile

st.set_page_config(page_title="Glycan Ensemble Analysis", layout="wide")

st.title("Glycan Ensemble SASA Analysis")

# Sidebar: File Selection
st.sidebar.header("Data Input")
uploaded_file = st.sidebar.file_uploader("Upload Ensemble PDB", type=["pdb"])

# Local fallback
LOCAL_PDB = "Ensemble_analysis/ensemble.pdb"
pdb_path = None

if uploaded_file is not None:
    # Save to temp
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdb") as tmp:
        tmp.write(uploaded_file.getbuffer())
        pdb_path = tmp.name
elif os.path.exists(LOCAL_PDB):
    st.sidebar.info(f"Using local file: `{LOCAL_PDB}`")
    pdb_path = LOCAL_PDB
else:
    st.warning("Please upload a PDB file or ensure 'ensemble.pdb' is in the directory.")
    st.stop()

# Load Data
@st.cache_resource
def load_data(path):
    traj = ensemble_parser.load_trajectory(path)
    metadata = ensemble_parser.parse_ensemble_remarks(path)
    return traj, metadata

try:
    with st.spinner("Loading Trajectory and Metadata..."):
        traj, metadata = load_data(pdb_path)
except Exception as e:
    st.error(f"Error loading PDB: {e}")
    st.stop()

# Process Chains
chains_with_glycans = list(metadata.keys())
if not chains_with_glycans:
    st.error("No Glycan metadata found in REMARKS.")
    st.stop()

# Selection UI
st.sidebar.subheader("Configuration")
selected_chain_id = st.sidebar.selectbox("Select Glycan Chain", chains_with_glycans)

glycan_info = metadata[selected_chain_id]
glycan_id = glycan_info.get('glycan_id', 'Unknown')

st.header(f"Chain {selected_chain_id} - Glycan: {glycan_id}")

# 1. Visualize Glycan
st.subheader("Glycan Structure")
svg_string, glycan_graph = glycan_visualizer.generate_glycan_svg(glycan_id)

if svg_string:
    # Display SVG
    # We ideally want it interactive.
    # For now, just display.
    # To center:
    col_img, col_plot = st.columns([1, 1])
    
    with col_img:
        st.caption("2D Structure (GlycoDraw)")
        # Use components to render SVG
        # st.image doesn't render SVG strings easily usually? 
        # Actually it does if passed as bytes or path.
        # But st.markdown with unsafe_allow_html is better for raw SVG string.
        st.markdown(f'<div style="text-align: center; background-color: white; padding: 10px; border-radius: 10px;">{svg_string}</div>', unsafe_allow_html=True)
else:
    st.warning(f"Could not generate visualization for {glycan_id}")

# 2. Build Residue Graph from PDB to populate dropdown
# Cache this?
pdb_graph = ensemble_parser.build_pdb_graph(traj[0], selected_chain_id)

if pdb_graph is None:
    st.error("Could not build PDB graph for selected chain.")
    st.stop()

# Extract residue options
# Nodes are indices. Data has 'name' and 'resSeq'.
residue_options = []
for node, data in pdb_graph.nodes(data=True):
    res_name = data.get('name', 'UNK')
    res_seq = data.get('resSeq', '?')
    label = f"{res_name} {res_seq} (Idx: {node})"
    residue_options.append((node, label))

# Sort by resSeq
residue_options.sort(key=lambda x: x[1])

# Display PDB Graph for reference
with col_img:
    st.subheader("Reference Graph")
    st.caption("Detailed connectivity from PDB")
    
    # Draw graph with labels
    fig_graph, ax_graph = plt.subplots(figsize=(6, 4))
    pos = nx.spring_layout(pdb_graph, seed=42) # Consistent layout
    
    # Labels: Name + Seq
    labels = {}
    for node, data in pdb_graph.nodes(data=True):
        labels[node] = f"{data.get('name', '')}\n{data.get('resSeq', '')}"
    
    nx.draw(pdb_graph, pos, ax=ax_graph, with_labels=True, labels=labels, 
            node_color='lightgreen', node_size=1500, font_size=9, font_weight='bold')
    st.pyplot(fig_graph)

# Dropdown for residue selection
with col_plot:
    st.subheader("SASA Analysis")
    
    selected_node_idx = st.selectbox(
        "Select Residue to Analyze", 
        options=[opt[0] for opt in residue_options],
        format_func=lambda x: [opt[1] for opt in residue_options if opt[0] == x][0]
    )

    # 3. Calculate SASA
    if selected_node_idx is not None:
        with st.spinner("Calculating SASA..."):
            sasa_values = analysis.calculate_residue_sasa(traj, selected_node_idx)
        
        # Plot
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.kdeplot(sasa_values, ax=ax, fill=True, color='skyblue')
        ax.set_title(f"SASA Density: {[opt[1] for opt in residue_options if opt[0] == selected_node_idx][0]}")
        ax.set_xlabel("SASA (nm²)")
        ax.set_ylabel("Density")
        st.pyplot(fig)
        
        st.metric("Mean SASA", f"{sasa_values.mean():.3f} nm²")
        st.metric("Std Dev", f"{sasa_values.std():.3f} nm²")

# Clean up temp file if uploaded
if uploaded_file is not None and pdb_path:
    # We can't delete it while used? OS dependent.
    # Streamlit re-runs script, so it's tricky.
    # NamedTemporaryFile delete=False persists.
    pass