import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
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

st.title("SAXS Frame Analysis with Plotly")

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
        frame_data.append({"Frame": frame_number, "Avg_Intensity": avg_intensity, "Rg": np.random.uniform(3, 5)})

    # Create DataFrame from collected data
    frame_df = pd.DataFrame(frame_data).sort_values(by="Frame")

    # Add sample and buffer points
    sample_frames = frame_df.sample(frac=0.1, random_state=42)  # Randomly select 10% for "Sample"
    buffer_frames = frame_df.sample(frac=0.05, random_state=42)  # Randomly select 5% for "Buffer"

    # Create a Plotly figure
    fig = go.Figure()

    # Add SEC trace (black points)
    fig.add_trace(go.Scatter(
        x=frame_df["Frame"],
        y=frame_df["Avg_Intensity"],
        mode="markers",
        marker=dict(color="black", size=6),
        name="SEC trace"
    ))

    # Add sample points (blue)
    fig.add_trace(go.Scatter(
        x=sample_frames["Frame"],
        y=sample_frames["Avg_Intensity"],
        mode="markers",
        marker=dict(color="blue", size=8),
        name="Sample"
    ))

    # Add buffer points (cyan)
    fig.add_trace(go.Scatter(
        x=buffer_frames["Frame"],
        y=buffer_frames["Avg_Intensity"],
        mode="markers",
        marker=dict(color="cyan", size=8),
        name="Buffer"
    ))

    # Add radius of gyration (Rg) with error bars (red points)
    fig.add_trace(go.Scatter(
        x=frame_df["Frame"],
        y=frame_df["Rg"],
        mode="markers",
        marker=dict(color="red", size=6),
        error_y=dict(
            type="data",
            array=np.full(len(frame_df), 0.2),  # Constant error bar
            visible=True
        ),
        name="Rg"
    ))

    # Customize layout
    fig.update_layout(
        title="Frame Analysis: Avg. Intensity and Rg",
        xaxis_title="Frame #",
        yaxis_title="Avg. Intensity",
        yaxis=dict(title="Avg. Intensity"),
        yaxis2=dict(
            title="Radius of Gyration",
            overlaying="y",
            side="right"
        ),
        legend=dict(orientation="h", x=0.5, y=-0.2, xanchor="center"),
        template="plotly_white"
    )

    # Display the plot
    st.plotly_chart(fig, use_container_width=True)

    # Export processed data
    st.write("Export Processed Data:")
    processed_file = "processed_frames.csv"
    frame_df.to_csv(processed_file, index=False)
    with open(processed_file, "rb") as f:
        st.download_button("Download Processed Data", data=f, file_name="processed_frames.csv", mime="text/csv")
