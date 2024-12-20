import streamlit as st
import pandas as pd
import numpy as np
import pickle
import seaborn as sns
import matplotlib.pyplot as plt

# Load the optimized weights (cache this to avoid reloading)
@st.cache_data
def load_weights():
    with open('optimized_pca_weights.pkl', 'rb') as f:
        optimized_weights = pickle.load(f)
    return optimized_weights

optimized_weights = load_weights()
phi_weights_opt = optimized_weights[:11]  # First 11 weights for phi
psi_weights_opt = optimized_weights[11:]  # Next 11 weights for psi

# Load the PCA-transformed data and other datasets (no pocket data loading anymore)
@st.cache_data
def load_data():
    pca_transformed_data = pd.read_csv('filtered_data_surrounding_sequence_pca1.csv')
    with open('new_pca_model_optimized.pkl', 'rb') as f:
        pca = pickle.load(f)
    return pca_transformed_data, pca

pca_transformed_data, pca = load_data()

# Function to input a sequence in Streamlit (no need to change this part)
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

# Format sequence for the legend (no change here)
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

# Fix the pocket mean to 0.53 as requested
pocket_mean = 2.30

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Gaussian kernel function
def gaussian_kernel(u, sigma):
    return (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(- (u ** 2) / (2 * sigma ** 2))

# Scoring function using KDE and Gaussian kernel weighting
def compute_score(f_x, x_values, x0, sigma):
    """
    Calculate a weighted score based on the proximity of KDE distribution to a reference point (x0).
    
    Parameters:
    - f_x: KDE density values at points x_values
    - x_values: x-axis values corresponding to f_x
    - x0: Reference point (pocket mean)
    - sigma: Bandwidth parameter for the Gaussian kernel
    
    Returns:
    - score: Higher score indicates closer alignment with pocket mean
    """
    # Calculate Gaussian kernel weights centered on x0
    K = gaussian_kernel(x_values - x0, sigma)
    
    # Compute the weighted score as the integral of the product f_x * K
    weighted_score = np.trapz(f_x * K, x_values)
    return weighted_score

# Function to retrieve KDE values from Seaborn
def get_kde_values(data, bw_adjust=0.5):
    """
    Calculate KDE values for a given data using Seaborn.
    
    Parameters:
    - data: Data points for which KDE needs to be computed
    - bw_adjust: Bandwidth adjustment for KDE
    
    Returns:
    - x_values, kde_values: x and y values for the KDE
    """
    kde_plot = sns.kdeplot(data, bw_adjust=bw_adjust)
    x_values, kde_values = kde_plot.get_lines()[0].get_data()
    plt.close()  # Close the plot as we only need the data
    return x_values, kde_values

# Calculate KDE for each sequence and pocket data
x_values_seq1, kde_values_seq1 = get_kde_values(pca1_matching_seq1)
x_values_seq2, kde_values_seq2 = get_kde_values(pca1_matching_seq2)



# Set the bandwidth parameter for Gaussian kernel
sigma = 0.1  # Adjust based on desired sensitivity

# Compute scores for each sequence
score_seq1 = compute_score(kde_values_seq1, x_values_seq1, pocket_mean, sigma)
score_seq2 = compute_score(kde_values_seq2, x_values_seq2, pocket_mean, sigma)
# Display scores in the Streamlit app
st.write(f"Score for Sequence 1: {score_seq1}")
st.write(f"Score for Sequence 2: {score_seq2}")

# Create plot with KDE for matching sequences and a line for fixed pocket data
fig, ax = plt.subplots(figsize=(10, 6))

# Plot KDE for matching sequences
if pca1_matching_seq1:
    sns.kdeplot(pca1_matching_seq1, ax=ax, label=f"Sequences 1: {r'${}$'.format(formatted_seq1)}", bw_adjust=0.5, color="blue")
if pca1_matching_seq2:
    sns.kdeplot(pca1_matching_seq2, ax=ax, label=f"Sequences 2: {r'${}$'.format(formatted_seq2)}", bw_adjust=0.5, color="red")

# Plot a vertical line at the fixed mean of 0.53 for pocket data
ax.axvline(pocket_mean, color='orange', linestyle='--', label=f"OST Pocket (Fixed at 0.53)")

# Add title and labels
ax.set_xlabel("Protein Fold Landscape w.r.t OST Pocket", fontsize=14)
ax.set_ylabel("Density", fontsize=14)

# Add legend
ax.legend()

# Render the plot in Streamlit
st.pyplot(fig)
