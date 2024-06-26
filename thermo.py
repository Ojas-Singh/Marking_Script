import streamlit as st

# Define the sections and their maximum marks for the Thermochromic Compounds experiment
sections = {
    "THERMOCHROMISM DEFINITION": 15,
    "REACTION EQUATION": 5,
    "YIELD CALCULATION": 35,
    "COLOUR CHANGE": 20,
    "GEOMETRIC STRUCTURES": 10,
    "PHASE TRANSITION EXAMPLES": 15
}

# Dummy feedback for each section, tailored based on typical responses expected from students
dummy_feedback = {
    "THERMOCHROMISM DEFINITION": "Excellent explanation of thermochromism, covering all necessary scientific principles.",
    "REACTION EQUATION": "The reaction equation is correctly balanced and clearly written.",
    "YIELD CALCULATION": "Yield calculation is accurate, includes proper stoichiometric ratios and units.",
    "COLOUR CHANGE": "Detailed description of the colour change process and correct identification of temperature range.",
    "GEOMETRIC STRUCTURES": "Correctly named the possible geometric structures for the metal complex.",
    "PHASE TRANSITION EXAMPLES": "Well-explained examples of solid-to-solid phase transitions, including appropriate scientific details."
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
    st.title('Feedback Form for Thermochromic Compounds Experiment')

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
