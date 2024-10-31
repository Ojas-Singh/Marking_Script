import streamlit as st

# Define the sections and their maximum marks for the Bromination of trans-Stilbene experiment
sections = {
    "BROMINE QUANTITY CALCULATION": 8,
    "TLC EXPERIMENTS - MOBILE PHASE": 18,
    "MELTING POINT INFORMATION": 8,
    "3-D STRUCTURES OF PRODUCTS": 10,
    "REACTION MECHANISM": 8,
    "OPTICAL ACTIVITY USING POLARIMETER": 2
}

# Dummy feedback customized for each section based on the expected answers
dummy_feedback = {
    "BROMINE QUANTITY CALCULATION": "Accurate calculation of bromine quantity needed for complete reaction.",
    "TLC EXPERIMENTS - MOBILE PHASE": "Appropriate analysis of TLC data and selection of suitable mobile phase.",
    "MELTING POINT INFORMATION": "Correctly recorded melting points and compared with literature values.",
    "3-D STRUCTURES OF PRODUCTS": "Detailed and accurate 3-D structures of products provided.",
    "REACTION MECHANISM": "Mechanism accurately drawn with proper curly arrow notation.",
    "OPTICAL ACTIVITY USING POLARIMETER": "Correct explanation on the optical inactivity of meso isomer."
}

# Function to create a well-aligned feedback table
def create_feedback_table(marks_awarded, feedback_given, sections):
    section_width = max(len(s) for s in sections) + 2  # Longest section name + padding
    marks_width = 10  # "x.x/xx" format
    feedback_width = 60  # Fixed width for feedback

    header = (
        f"| {'Section'.ljust(section_width)} | "
        f"{'Marks'.center(marks_width)} | "
        f"{'Feedback'.ljust(feedback_width)} |\n"
        f"|{'-' * section_width}|{'-' * marks_width}|{'-' * feedback_width}|\n"
    )

    rows = ""
    for section, max_mark in sections.items():
        marks_str = f"{marks_awarded[section]:.1f}/{max_mark:.1f}"
        rows += (
            f"| {section.ljust(section_width)} | "
            f"{marks_str.center(marks_width)} | "
            f"{feedback_given[section].ljust(feedback_width)} |\n"
        )
    
    total_marks = sum(marks_awarded.values())
    total_max = sum(sections.values())
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
    for section, max_marks in sections.items():
        title = f"Marks for {section} (Max: {max_marks})"
        marks_awarded[section] = st.number_input(title, min_value=0.0, max_value=float(max_marks), step=0.1, format="%.1f")
        feedback_given[section] = st.text_area(f"Feedback for {section}", value=dummy_feedback[section], height=100)

    # Create a submit button in the form using the "with" syntax
    submitted = st.form_submit_button("Submit")

if submitted:
    feedback_table = create_feedback_table(marks_awarded, feedback_given, sections)
    st.code(feedback_table)
