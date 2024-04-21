import streamlit as st

# Define the sections and their maximum marks for the experiment
sections = {
    "EQUATION BALANCING": 10,
    "YIELD CALCULATION": 25,
    "FUNCTION OF H2O2": 5,
    "SYNTHESIS EQUATION": 25,
    "% IRON CALCULATION": 10,
    "MAGNETIC MOMENT": 25
}

# Dummy feedback for each section, ideally customized based on expected student responses or common errors
dummy_feedback = {
    "EQUATION BALANCING": "Equation for the formation of diaquaoxalatoiron(II) is correctly balanced.",
    "YIELD CALCULATION": "Yield calculation is correct and includes all necessary steps.",
    "FUNCTION OF H2O2": "Correctly identified the role of H2O2 in the experiment.",
    "SYNTHESIS EQUATION": "The equation for the synthesis of potassium tris(oxalato)ferrate(III) is accurately written and balanced.",
    "% IRON CALCULATION": "Percentage of iron calculation is accurate and correctly formatted.",
    "MAGNETIC MOMENT": "Calculation of the magnetic moment and the discussion on electron distribution is comprehensive and correct."
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
    st.title('Feedback Form for Preparation of Diaquaoxalatoiron(II) and Potassium Tris(oxalato)ferrate(III) Trihydrate')

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
