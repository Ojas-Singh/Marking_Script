import streamlit as st

# Define the sections and their maximum marks
sections = {
    "ENTHALPY OF SOLVATION": 5,
    "LATTICE ENERGY": 5,
    "ENTHALPY OF SOLUTION NH4Cl": 5,
    "ENTHALPY OF SOLUTION NH4NO3": 5,
    "SELF-HEATING CAN": 15,
    "MINIMUM MASS OF CaO": 15,
    "DISSOLUTION NATURE": 5,
    "SALT CHOICE FOR COOLING": 2,
    "HEAT TRANSFER": 15,
    "AMOUNT OF SALT": 15,
    "TEMPERATURE PLOT": 13
}

# Dummy feedback for each section
dummy_feedback = {
    "ENTHALPY OF SOLVATION": "Correct calculation of enthalpy of solvation.",
    "LATTICE ENERGY": "Lattice energy calculation is accurate.",
    "ENTHALPY OF SOLUTION NH4Cl": "Correctly calculated the enthalpy of solution for NH4Cl.",
    "ENTHALPY OF SOLUTION NH4NO3": "Correctly calculated the enthalpy of solution for NH4NO3.",
    "SELF-HEATING CAN": "Correctly calculated the energy needed for the self-heating can.",
    "MINIMUM MASS OF CaO": "Correct estimation of the minimum mass of CaO needed.",
    "DISSOLUTION NATURE": "Correctly identified the exothermic or endothermic nature of the dissolution.",
    "SALT CHOICE FOR COOLING": "Appropriate choice of salt based on cost and safety.",
    "HEAT TRANSFER": "Accurately calculated the heat transfer required.",
    "AMOUNT OF SALT": "Correct calculation of the amount of salt needed to achieve the desired temperature change.",
    "TEMPERATURE PLOT": "Correctly interpreted the temperature plot."
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
    st.title('Cool Drinking Experiment Feedback Form')

    marks_awarded = {}
    feedback_given = {}

    # Adjust the titles to include maximum marks and change the number input step
    for section, max_marks in sections.items():
        title = f"Marks for {section} (Max: {max_marks})"
        marks_awarded[section] = st.number_input(title, min_value=0.0, max_value=max_marks, step=0.1, format="%.1f")
        feedback_given[section] = st.text_area(f"Feedback for {section}", value=dummy_feedback[section], height=100)

    submitted = st.form_submit_button("Submit")

if submitted:
    feedback_table = create_feedback_table(marks_awarded, feedback_given, sections)
    st.code(feedback_table)
