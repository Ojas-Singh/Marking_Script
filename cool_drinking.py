import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import os

def load_dat(file):
    """Load a .dat file and return a DataFrame with q, Intensity, and other columns."""
    data = pd.read_csv(file, sep="\t", comment="#", header=None)
    data.columns = ["q", "Intensity", "Other"]  # Adjust column names if needed
    return data

def extract_frame_number(filename):
    """Extract frame number from filename using regex."""
    match = re.search(r"frame_(\d+)", filename)
    if match:
        return int(match.group(1))
    return None

st.title("SAXS Frame Analysis and Plotting")

# File uploader
uploaded_files = st.file_uploader("Upload .dat Files", type=["dat"], accept_multiple_files=True)

if uploaded_files:
    st.sidebar.header("Settings")

    # Set q-limit
    q_limit = st.sidebar.slider("Set q-limit (Å⁻¹)", min_value=0.0, max_value=1.0, step=0.01, value=0.3)
    st.sidebar.write(f"Selected q-limit: {q_limit}")

    # Prepare data for plotting
    frame_data = []
    for file in uploaded_files:
        file_data = load_dat(file)
        # Filter by q-limit
        filtered_data = file_data[file_data["q"] <= q_limit]
        avg_intensity = filtered_data["Intensity"].mean()
        frame_number = extract_frame_number(os.path.basename(file.name))
        frame_data.append({"Frame": frame_number, "Avg_Intensity": avg_intensity, "Rg": 0.0})

    # Create DataFrame from collected data
    frame_df = pd.DataFrame(frame_data).sort_values(by="Frame")

    # Plot the data
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot average intensity (Primary y-axis)
    ax1.scatter(frame_df["Frame"], frame_df["Avg_Intensity"], color="black", label="SEC trace", s=10)
    ax1.set_xlabel("Frame #")
    ax1.set_ylabel("Avg. Intensity", color="black")
    ax1.tick_params(axis="y", labelcolor="black")
    ax1.legend(loc="upper left")

    # Add sample and buffer points
    sample_frames = frame_df.sample(frac=0.1, random_state=42)  # Randomly select 10% for "Sample"
    ax1.scatter(sample_frames["Frame"], sample_frames["Avg_Intensity"], color="blue", label="Sample", s=20)
    ax1.legend(loc="upper left")

    buffer_frames = frame_df.sample(frac=0.05, random_state=42)  # Randomly select 5% for "Buffer"
    ax1.scatter(buffer_frames["Frame"], buffer_frames["Avg_Intensity"], color="cyan", label="Buffer", s=20)
    ax1.legend(loc="upper left")

    # Plot radius of gyration (Secondary y-axis)
    ax2 = ax1.twinx()
    ax2.errorbar(frame_df["Frame"], frame_df["Rg"], yerr=0.2, fmt="o", color="red", label="Rg", markersize=5)
    ax2.set_ylabel("Radius of Gyration", color="red")
    ax2.tick_params(axis="y", labelcolor="red")
    ax2.legend(loc="upper right")

    plt.title("Frame Analysis: Avg. Intensity and Rg")
    plt.grid()
    st.pyplot(fig)

    # Export processed data
    st.write("Export Processed Data:")
    processed_file = "processed_frames.csv"
    frame_df.to_csv(processed_file, index=False)
    with open(processed_file, "rb") as f:
        st.download_button("Download Processed Data", data=f, file_name="processed_frames.csv", mime="text/csv")
