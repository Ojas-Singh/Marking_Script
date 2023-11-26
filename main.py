import streamlit as st

# Define the sections and their maximum marks
sections = {
    "TITLE AND DATE": 0.5,
    "AIM": 0.5,
    "INTRODUCTION": 1.0,
    "PROCEDURE": 1.5,
    "RESULTS": 2.0,
    "ANALYSIS": 1.5,
    "DETERMINATION & CALC.": 1.0,
    "CONCLUSION": 1.0,
    "QUESTIONS": 1.0
}

# Dummy feedback for each section
dummy_feedback = {
    "TITLE AND DATE": "Title and date appropriately provided.",
    "AIM": "Aim is clearly defined.",
    "INTRODUCTION": "Introduction provides necessary background.",
    "PROCEDURE": "Procedure is detailed and follows past perfect tense.",
    "RESULTS": "Results are well-presented with correct charts.",
    "ANALYSIS": "Analysis includes correctly drawn graphs with labeled axes.",
    "DETERMINATION & CALC.": "Calculations are accurate with proper units.",
    "CONCLUSION": "Conclusion is concise and reflects the results.",
    "QUESTIONS": "Questions are answered thoroughly."
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
    st.title('Feedback Form')

    marks_awarded = {}
    feedback_given = {}

    # Adjust the titles to include maximum marks and change the number input step
    for section, max_marks in sections.items():
        title = f"Marks for {section} (Max: {max_marks})"
        marks_awarded[section] = st.number_input(title, min_value=0.0, max_value=float(max_marks)+0.1, step=0.1, format="%.2f")
        feedback_given[section] = st.text_area(f"Feedback for {section}", value=dummy_feedback[section], height=100)

    submitted = st.form_submit_button("Submit")

if submitted:
    feedback_table = create_feedback_table(marks_awarded, feedback_given, sections)
    st.code(feedback_table)