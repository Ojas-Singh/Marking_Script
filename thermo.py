import streamlit as st

# Define the sections and their maximum marks for the new marking scheme
sections = {
    "Introduction": 5,
    "Experimental Section": 2,
    "Results and Discussion": 4,
    "Conclusion": 1.5
}

# Dummy feedback for each section, tailored based on typical responses expected from students
dummy_feedback = {
    "Introduction": "Ensure the introduction states the position, problem, two possibilities, and a proposal.",
    "Experimental Section": "Written in third-person past tense, with correct format and unit usage.",
    "Results and Discussion": "Graph and table titles, units, and equivalence points should be well presented.",
    "Conclusion": "Clearly summarize the results, reference the introduction, and suggest future work."
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
        marks_str = f"{marks_awarded[section]}/{max_mark}"
        rows += (
            f"| {section.ljust(section_width)} | "
            f"{marks_str.center(marks_width)} | "
            f"{feedback_given[section].ljust(feedback_width)} |\n"
        )
    
    total_marks = sum(marks_awarded.values())
    total_max = sum(sections.values())
    total_marks_str = f"{total_marks}/{total_max}"
    
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
    st.title('Feedback Form for Experiment Reports')

    marks_awarded = {}
    feedback_given = {}

    # Adjust the titles to include maximum marks and change to slider input
    for section, max_marks in sections.items():
        title = f"Marks for {section} (Max: {max_marks})"
        marks_awarded[section] = st.slider(
            title, 
            min_value=0, 
            max_value=int(max_marks), 
            step=1
        )
        feedback_given[section] = st.text_area(f"Feedback for {section}", value=dummy_feedback[section], height=100)

    # Create a submit button in the form using the "with" syntax
    submitted = st.form_submit_button("Submit")

if submitted:
    feedback_table = create_feedback_table(marks_awarded, feedback_given, sections)
    st.code(feedback_table)
