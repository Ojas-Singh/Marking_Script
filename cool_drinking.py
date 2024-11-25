import streamlit as st
import pandas as pd
import numpy as np
import os

def load_dat(file):
    """Load a .dat file and return a DataFrame with q, Intensity, and other columns."""
    data = pd.read_csv(file, sep="\t", comment="#", header=None)
    data.columns = ["q", "Intensity", "Other"]  # Adjust column names if needed
    return data

st.title("SAXS Data Processor with Averaging")

# File uploader
uploaded_files = st.file_uploader("Upload .dat Files", type=["dat"], accept_multiple_files=True)

if uploaded_files:
    st.sidebar.header("Settings")
    
    # Set q-limit
    q_limit = st.sidebar.slider("Set q-limit (Å⁻¹)", min_value=0.0, max_value=1.0, step=0.01, value=0.3)
    st.sidebar.write(f"Selected q-limit: {q_limit}")
    
    # Process files
    merged_data = pd.DataFrame()
    for file in uploaded_files:
        file_data = load_dat(file)
        # Filter by q-limit
        filtered_data = file_data[file_data["q"] <= q_limit]
        filtered_data["File"] = os.path.basename(file.name)  # Add filename as a column
        merged_data = pd.concat([merged_data, filtered_data], ignore_index=True)

    # Show merged data
    st.write("Merged Data:")
    st.dataframe(merged_data)

    # Average Intensity for same q-values
    averaged_data = merged_data.groupby("q", as_index=False)["Intensity"].mean()

    # Show averaged data
    st.write("Averaged Data (Intensity averaged across files for the same q):")
    st.dataframe(averaged_data)

    # Plot averaged data
    st.write("Plot of Averaged Intensity vs q:")
    st.line_chart(averaged_data.set_index("q")["Intensity"], use_container_width=True)

    # Export averaged data
    st.write("Export Averaged Data:")
    averaged_file = "averaged_data.dat"
    averaged_data.to_csv(averaged_file, sep="\t", index=False)
    with open(averaged_file, "rb") as f:
        st.download_button("Download Averaged Data", data=f, file_name="averaged_data.dat", mime="text/plain")
