import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def load_dat(file):
    """Load a .dat file and return a DataFrame with q, Intensity, and other columns."""
    data = pd.read_csv(file, sep="\t", comment="#", header=None)
    data.columns = ["q", "Intensity", "Other"]  # Adjust column names if needed
    return data

st.title("SAXS Data Processor")

# File uploader
uploaded_files = st.file_uploader("Upload .dat Files", type=["dat"], accept_multiple_files=True)

if uploaded_files:
    st.sidebar.header("Settings")
    
    # Set q-limit
    q_limit = st.sidebar.slider("Set q-limit (Å⁻¹)", min_value=0.0, max_value=1.0, step=0.01, value=0.3)
    st.sidebar.write(f"Selected q-limit: {q_limit}")
    
    # Process files
    merged_data = pd.DataFrame()
    colors = plt.cm.tab10(np.linspace(0, 1, len(uploaded_files)))  # Unique colors for each file
    for file, color in zip(uploaded_files, colors):
        file_data = load_dat(file)
        # Filter by q-limit
        filtered_data = file_data[file_data["q"] <= q_limit]
        filtered_data["File"] = os.path.basename(file.name)  # Add filename as a column
        filtered_data["Color"] = color
        merged_data = pd.concat([merged_data, filtered_data], ignore_index=True)

    # Show merged data
    st.write("Merged Data:")
    st.dataframe(merged_data)

    # Plot merged data as scatter plots
    st.write("Combined Scatter Plot:")
    plt.figure(figsize=(10, 6))
    for name, group in merged_data.groupby("File"):
        plt.scatter(group["q"], group["Intensity"], label=name, alpha=0.7)
    plt.xlabel("q (Å⁻¹)")
    plt.ylabel("Intensity")
    plt.title("SAXS Intensity vs q (Combined)")
    plt.legend()
    plt.grid()
    st.pyplot(plt)

    # Export merged data
    st.write("Export Merged Data:")
    merged_file = "merged_data.dat"
    merged_data.to_csv(merged_file, sep="\t", index=False)
    with open(merged_file, "rb") as f:
        st.download_button("Download Merged Data", data=f, file_name="merged_data.dat", mime="text/plain")
