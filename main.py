import streamlit as st

# Define a function to create a feedback table
def create_feedback_table(feedback_data):
    feedback_table = "**CH202 2021 Beer Lambert Law Assessment Feedback**\n\n"
    feedback_table += "**Student Name:**\n"
    feedback_table += "**Student ID:**\n\n"
    feedback_table += "| Section                | Marks Awarded | Maximum Marks | Feedback                          |\n"
    feedback_table += "|------------------------|---------------|---------------|-----------------------------------|\n"

    total_marks = 0
    for section, data in feedback_data.items():
        feedback_table += f"| {section} | {data['marks']} | {data['max_marks']} | {data['feedback']} |\n"
        total_marks += data['marks']
    
    feedback_table += f"| **Total** | **{total_marks}** | **9** | **Overall Feedback:** {feedback_data['Total']['feedback']} |\n\n"
    feedback_table += "**Comments:**\n\n"
    for section, data in feedback_data.items():
        if section != "Total":
            feedback_table += f"- **{section}:** {data['feedback']}\n"
    feedback_table += "\n**Final Marks:**\n\n"

    return feedback_table

# Define the sections and their max marks
sections = {
    "TITLE AND DATE": 0.5,
    "AIM": 0.5,
    "INTRODUCTION": 1,
    "PROCEDURE": 1.5,
    "RESULTS": 2,
    "ANALYSIS": 1.5,
    "DETERMINATION & CALC.": 1,
    "CONCLUSION": 1,
    "QUESTIONS": 1,
    "Total": {"max_marks": 9, "marks": 0, "feedback": ""}  # Total is handled separately
}

# Streamlit app
def main():
    st.title("CH202 2021 Beer Lambert Law Assessment Feedback Generator")

    # Dictionary to hold the feedback data
    feedback_data = {}

    # Iterate over sections to get input from the user
    for section, max_marks in sections.items():
    with st.form(key=section):
        st.subheader(section)
        # Convert max_marks to float to match the type of min_value and step
        marks = st.number_input(f"Enter marks for {section}", min_value=0.0, max_value=float(max_marks), step=0.1)
        feedback = st.text_area(f"Enter feedback for {section}", help=f"Write the feedback for the {section} section.")
        submit_button = st.form_submit_button(label='Save')

            if submit_button:
                feedback_data[section] = {"marks": marks, "max_marks": max_marks, "feedback": feedback}

    # When all forms have been filled
    if st.button('Generate Feedback Table'):
        # If Total section has not been filled, prompt the user to fill it
        if "Total" not in feedback_data:
            st.error("Please fill in the 'Total' section.")
        else:
            # Create and display the feedback table
            feedback_table = create_feedback_table(feedback_data)
            st.text_area("Copy the feedback table below:", feedback_table, height=300)

if __name__ == "__main__":
    main()
