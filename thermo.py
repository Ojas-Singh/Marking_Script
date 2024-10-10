import streamlit as st

# Define the sections and their maximum marks for the CH201-2 experiment
sections = {
    "STEREOCENTRE IDENTIFICATION": 2,
    "STEREOISOMERS COUNT": 2,
    "3D MODEL DRAWING": 6,
    "ENANTIOMER DRAWING": 4,
    "OPTICALLY ACTIVE STRUCTURE": 10,
    "MESO FORM STRUCTURE": 6,
    "DIASTEREOMER STRUCTURE": 4,
    "ALKENE STRUCTURES": 6
}

# Dummy feedback for each section, tailored based on typical responses expected from students
dummy_feedback = {
    "STEREOCENTRE IDENTIFICATION": "Correct identification of the stereocentres with clear reasoning.",
    "STEREOISOMERS COUNT": "Accurate calculation of possible stereoisomers.",
    "3D MODEL DRAWING": "Well-drawn 3D model with appropriate use of dash and wedge bonds.",
    "ENANTIOMER DRAWING": "Correct mirror image of the 3D structure with proper representation.",
    "OPTICALLY ACTIVE STRUCTURE": "Detailed and accurate drawing with all bonds and angles considered.",
    "MESO FORM STRUCTURE": "Correctly drawn meso structure with symmetry properly illustrated.",
    "DIASTEREOMER STRUCTURE": "Clear representation of a diastereomer with appropriate differences highlighted.",
    "ALKENE STRUCTURES": "Correct structures of alkenes with proper geometry (cis/trans or E/Z)."
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
    st.title('Feedback Form for CH201-2 Experiment')

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
