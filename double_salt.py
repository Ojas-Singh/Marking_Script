import streamlit as st

# Define the sections and their maximum marks for the Double Salt experiment
sections = {
    "DOUBLE SALT DEFINITION": 8,
    "LATTICE ENERGY DEFINITION": 8,
    "FORMATION EQUATION": 4,
    "YIELD CALCULATION": 25,
    "TAN PRECIPITATE EQUATION": 10,
    "COPPER PERCENTAGE": 20,
    "THEORETICAL %Cu": 10,
    "FREE ENERGY AND ENTHALPY CHANGE": 15
}

# Dummy feedback for each section, ideally customized based on common issues or expectations
dummy_feedback = {
    "DOUBLE SALT DEFINITION": "Correctly explained the concept of a Double Salt.",
    "LATTICE ENERGY DEFINITION": "Accurately defined Lattice Energy with appropriate examples.",
    "FORMATION EQUATION": "Equation for the formation is correctly written and balanced.",
    "YIELD CALCULATION": "Yield calculation is correct and clearly articulated.",
    "TAN PRECIPITATE EQUATION": "Reaction equation for the formation of tan precipitate is accurate.",
    "COPPER PERCENTAGE": "Correctly calculated the percentage of copper in the sample.",
    "THEORETICAL %Cu": "Comparison between theoretical and experimental copper percentage is well analyzed.",
    "FREE ENERGY AND ENTHALPY CHANGE": "Correctly calculated the free energy and enthalpy changes for the reaction."
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
    st.title('Double Salt Experiment Feedback Form')

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
