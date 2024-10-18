import streamlit as st
import pandas as pd
import numpy as np
import pickle
import seaborn as sns
import matplotlib.pyplot as plt

# Load the optimized weights
@st.cache_data
def load_weights():
    with open('optimized_pca_weights.pkl', 'rb') as f:
        optimized_weights = pickle.load(f)
    return optimized_weights

optimized_weights = load_weights()
phi_weights_opt = optimized_weights[:11]  # First 11 weights for phi
psi_weights_opt = optimized_weights[11:]  # Next 11 weights for psi

# Load the PCA-transformed data and other datasets
@st.cache_data
def load_data():
    pca_transformed_data = pd.read_csv('filtered_data_surrounding_sequence_pca1.csv')
    pocket_data = pd.read_csv('updated_pocket.csv')
    experimental_data = pd.read_csv('experimental.csv')
    with open('new_pca_model_optimized.pkl', 'rb') as f:
        pca = pickle.load(f)
    return pca_transformed_data, pocket_data, experimental_data, pca

pca_transformed_data, pocket_data, experimental_data, pca = load_data()

# Function to extract phi-psi data, convert to sin and cos, and apply weights
def extract_middle_phi_psi_sin_cos_weighted(angles_str, phi_weights, psi_weights):
    angle_pairs = angles_str.split(');')
    sin_cos_values = []
    
    # Only process the 11 middle pairs (2nd to 12th)
    for i, pair in enumerate(angle_pairs):  
        try:
            pair = pair.replace('(', '').replace(')', '').strip()
            if ';' not in pair or not pair.strip():
                return None
            phi, psi = map(float, pair.split(';'))
            
            # Convert phi and psi to sine and cosine values
            sin_phi = np.sin(np.radians(phi)) * phi_weights[i]
            cos_phi = np.cos(np.radians(phi)) * phi_weights[i]
            sin_psi = np.sin(np.radians(psi)) * psi_weights[i]
            cos_psi = np.cos(np.radians(psi)) * psi_weights[i]
            
            sin_cos_values.extend([sin_phi, cos_phi, sin_psi, cos_psi])
        except ValueError:
            return None
    return sin_cos_values

# Function to compute partial matches for a sequence
def partial_sequence_match(input_sequence, sequences):
    matches = []
    for seq in sequences:
        is_match = True
        for i, char in enumerate(input_sequence):
            if char and seq[i] != char:  # If a character is provided and doesn't match
                is_match = False
                break
        if is_match:
            matches.append(seq)
    return matches

# Function to apply weights to the pocket data and transform using PCA
def transform_pocket_data(pocket_data, phi_weights, psi_weights, pca_model):
    pocket_phi_psi_sin_cos_weighted = []
    for row in pocket_data['Phi_Psi_List']:
        weighted_features = extract_middle_phi_psi_sin_cos_weighted(row, phi_weights, psi_weights)
        if weighted_features is not None:
            pocket_phi_psi_sin_cos_weighted.append(weighted_features)
    
    if not pocket_phi_psi_sin_cos_weighted:
        return pd.DataFrame(columns=['PCA1'])
    
    pocket_phi_psi_sin_cos_weighted = np.array(pocket_phi_psi_sin_cos_weighted)
    pocket_pca_transformed = pca_model.transform(pocket_phi_psi_sin_cos_weighted)
    pocket_df = pd.DataFrame(pocket_pca_transformed, columns=['PCA1', 'PCA2'])
    return pocket_df

# Streamlit App Title
st.title("Matching Sequences Structures w.r.t OST Pocket")


# Function to input a sequence in Streamlit
def input_sequence_form(seq_number):
    if seq_number == 1:
        st.markdown(f'<p style="color:blue; font-weight:bold;">Input Sequence {seq_number}</p>', unsafe_allow_html=True)
    else:
        st.markdown(f'<p style="color:red; font-weight:bold;">Input Sequence {seq_number}</p>', unsafe_allow_html=True)
    
    input_sequence = [''] * 13  # Start with 13 empty values
    cols = st.columns(13)
    for i in range(13):
        if i == 5:  # Lock 'N' in the 6th position
            cols[i].text_input(f"  {i - 5}", "N", disabled=True, key=f"seq_{seq_number}_{i}")
            input_sequence[i] = 'N'
        else:
            input_sequence[i] = cols[i].text_input(f"   {i -5}", "", key=f"seq_{seq_number}_{i}")
    return input_sequence

# Input for two sequences
input_sequence1 = input_sequence_form(1)
input_sequence2 = input_sequence_form(2)


# Function to format the sequence with LaTeX for legend in monospaced font and bold 'N'
def format_sequence_for_legend(input_sequence):
    formatted_sequence = []
    for i, char in enumerate(input_sequence):
        if i == 5:
            formatted_sequence.append(r"\mathbf{N}")  # Bold the 'N' at position 6 using LaTeX \mathbf
        elif char == '':
            formatted_sequence.append('X')  # Replace empty characters with 'X'
        else:
            formatted_sequence.append(char)
    
    # Wrap the entire sequence in \mathtt{} for monospaced font
    return r"\mathtt{" + ''.join(formatted_sequence) + "}"

def process_sequence(input_sequence, seq_number):
    if any(char for i, char in enumerate(input_sequence) if i != 5 and char):
        # Convert input sequence to string
        input_sequence_str = ''.join(input_sequence)
        
        # Find all sequences in the dataset that match the input
        sequences = pca_transformed_data['Surrounding_sequence']
        matching_sequences = partial_sequence_match(input_sequence, sequences)
        
        # Prepare KDE data lists
        pca1_matching_seq = []
        if matching_sequences:
            # Extract PCA1 values for matching sequences
            matching_seq_data = pca_transformed_data[pca_transformed_data['Surrounding_sequence'].isin(matching_sequences)]
            pca1_matching_seq = matching_seq_data['PCA1'].tolist()
        
        return pca1_matching_seq
    else:
        return []

# Process both sequences and format for legend
pca1_matching_seq1 = process_sequence(input_sequence1, 1)
formatted_seq1 = format_sequence_for_legend(input_sequence1)

pca1_matching_seq2 = process_sequence(input_sequence2, 2)
formatted_seq2 = format_sequence_for_legend(input_sequence2)

# Transform and extract PCA1 values for pocket data
pocket_df = transform_pocket_data(pocket_data, phi_weights_opt, psi_weights_opt, pca)
if not pocket_df.empty:
    pca1_pocket = pocket_df['PCA1'].tolist()
else:
    pca1_pocket = []

# Calculate the mean or peak value for pocket data
pocket_mean = np.mean(pca1_pocket) if pca1_pocket else 0  # Use mean as an example

# Create plot with KDE for matching sequences and a line for pocket data
fig, ax = plt.subplots(figsize=(10, 6))

# Plot KDE for matching sequences
if pca1_matching_seq1:
    sns.kdeplot(pca1_matching_seq1, ax=ax, label=f"Sequences 1: {r'${}$'.format(formatted_seq1)}", bw_adjust=0.5, color="blue")
if pca1_matching_seq2:
    sns.kdeplot(pca1_matching_seq2, ax=ax, label=f"Sequences 2: {r'${}$'.format(formatted_seq2)}", bw_adjust=0.5, color="red")

# Plot a vertical line at the mean of pocket data
ax.axvline(pocket_mean, color='orange', linestyle='--', label=f"OST Pocket")

# Add title and labels
# ax.set_title("KDE for Matching Sequences and Line for Pocket Data", fontsize=16)
ax.set_xlabel("Protein Fold Landscape w.r.t OST Pocket", fontsize=14)
ax.set_ylabel("Density", fontsize=14)

# Add legend
ax.legend()

# Render the plot in Streamlit
st.pyplot(fig)
