import streamlit as st

# Define the sections and their maximum marks for the Bromination of trans-Stilbene experiment
sections = {
    "Bromine Quantity Calculation": 8,
    "TLC Experiments - Mobile Phase": {
        "Why DCM is not a good mobile phase": 4,
        "High Rf values for DCM": 4,
        "Why hexane is not a good mobile phase": 2,
        "Low Rf values for hexane": 2,
        "Best mixed solvent mobile phase": 2,
        "Recording Rf values": 2,
        "Difference between Rf for alkene and dibromoalkane": 2,
        "Identity and purity assessment via TLC": 4,
    },
    "Melting Point Information": {
        "Experimental melting points": 3,
        "Literature values with citations": 3,
        "Comparison and conclusion on purity": 4,
    },
    "3-D Structures of Products": {
        "Drawing 3-D structures": 4,
        "Identifying meso and enantiomers": 2,
        "(R)/(S) configuration assignment": 4,
    },
    "Reaction Mechanism": {
        "Starting material structure": 1,
        "Intermediate structure with proper notation": 2,
        "Curly arrow notation for attack on bromonium ion": 2,
        "Final product structure": 1,
        "Discussion on meso-formation": 2,
    },
    "Optical Activity Using Polarimeter": 2,
}

# Dummy feedback for each subsection
dummy_feedback = {
    "Bromine Quantity Calculation": "Accurate calculation of bromine quantity needed for complete reaction.",
    "Why DCM is not a good mobile phase": "Explained correctly why DCM is not suitable.",
    "High Rf values for DCM": "Correct explanation of high Rf values due to DCM.",
    "Why hexane is not a good mobile phase": "Described why hexane is unsuitable as a mobile phase.",
    "Low Rf values for hexane": "Explained the low Rf values when using hexane.",
    "Best mixed solvent mobile phase": "Identified the best solvent mix for the experiment.",
    "Recording Rf values": "Accurately recorded Rf values with expected precision.",
    "Difference between Rf for alkene and dibromoalkane": "Correctly explained Rf differences.",
    "Identity and purity assessment via TLC": "Thorough assessment of identity and purity based on TLC results.",
    "Experimental melting points": "Recorded experimental melting points accurately.",
    "Literature values with citations": "Included correct literature values with proper citations.",
    "Comparison and conclusion on purity": "Analyzed purity based on melting points effectively.",
    "Drawing 3-D structures": "Detailed and accurate 3-D structures of products.",
    "Identifying meso and enantiomers": "Correctly identified meso and enantiomers.",
    "(R)/(S) configuration assignment": "Accurately assigned (R)/(S) configuration for chiral centers.",
    "Starting material structure": "Correct structure of the starting material shown.",
    "Intermediate structure with proper notation": "Proper notation of the intermediate structure with charge on Br.",
    "Curly arrow notation for attack on bromonium ion": "Accurate curly arrow notation showing Br- attack.",
    "Final product structure": "Correct final product structure.",
    "Discussion on meso-formation": "Good explanation of why the product forms as a meso-structure.",
    "Optical Activity Using Polarimeter": "Correctly explained optical inactivity of the meso isomer."
}

# Function to create a well-aligned feedback table
def create_feedback_table(marks_awarded, feedback_given, sections):
    section_width = max(len(s) for s in dummy_feedback) + 2  # Longest section name + padding
    marks_width = 10  # "x.x/xx" format
    feedback_width = 60  # Fixed width for feedback

    header = (
        f"| {'Section'.ljust(section_width)} | "
        f"{'Marks'.center(marks_width)} | "
        f"{'Feedback'.ljust(feedback_width)} |\n"
        f"|{'-' * section_width}|{'-' * marks_width}|{'-' * feedback_width}|\n"
    )

    rows = ""
    for section, content in sections.items():
        if isinstance(content, dict):  # Handle subsections
            for subsection, max_mark in content.items():
                marks_str = f"{marks_awarded[section][subsection]:.1f}/{max_mark:.1f}"
                rows += (
                    f"| {subsection.ljust(section_width)} | "
                    f"{marks_str.center(marks_width)} | "
                    f"{feedback_given[section][subsection].ljust(feedback_width)} |\n"
                )
        else:  # Handle top-level sections without subsections
            marks_str = f"{marks_awarded[section]:.1f}/{content:.1f}"
            rows += (
                f"| {section.ljust(section_width)} | "
                f"{marks_str.center(marks_width)} | "
                f"{feedback_given[section].ljust(feedback_width)} |\n"
            )
    
    total_marks = sum(
        sum(subsection.values()) if isinstance(subsection, dict) else subsection
        for section, subsection in marks_awarded.items()
    )
    total_max = sum(
        sum(content.values()) if isinstance(content, dict) else content
        for content in sections.values()
    )
    total_marks_str = f"{total_marks:.1f}/{total_max:.1f}"
    
    footer = (
        f"| {'Total'.ljust(section_width)} | "
        f"{total_marks_str.center(marks_width)} | "
        f"{' ' * feedback_width} |\n"
        f"|{'=' * (section_width + marks_width + feedback_width + 5)}|\n"
    )

    feedback_table = header + rows + footer

    return feedback_table

# Streamlit form for input
with st.form(key='feedback_form'):
    st.title('Bromination of trans-Stilbene Experiment Feedback Form')

    marks_awarded = {}
    feedback_given = {}

    # Adjust the titles to include maximum marks and change the number input step
    for section, content in sections.items():
        if isinstance(content, dict):  # If section has subsections
            marks_awarded[section] = {}
            feedback_given[section] = {}
            st.header(section)
            for subsection, max_marks in content.items():
                title = f"Marks for {subsection} (Max: {max_marks})"
                marks_awarded[section][subsection] = st.number_input(title, min_value=0.0, max_value=float(max_marks), step=1.0, format="%.1f")
                feedback_given[section][subsection] = st.text_area(f"Feedback for {subsection}", value=dummy_feedback[subsection], height=100)
        else:  # Top-level section without subsections
            title = f"Marks for {section} (Max: {content})"
            marks_awarded[section] = st.number_input(title, min_value=0.0, max_value=float(content), step=0.1, format="%.1f")
            feedback_given[section] = st.text_area(f"Feedback for {section}", value=dummy_feedback[section], height=100)

    # Create a submit button in the form using the "with" syntax
    submitted = st.form_submit_button("Submit")

if submitted:
    feedback_table = create_feedback_table(marks_awarded, feedback_given, sections)
    st.code(feedback_table)
