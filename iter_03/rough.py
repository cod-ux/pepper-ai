import streamlit as st

# Initialize session state to track whether the continue button has been clicked
if 'continue_clicked' not in st.session_state:
    st.session_state.continue_clicked = False

# Title of the application
st.title("Editable Text Area Example")

# Display the text area and button if continue button has not been clicked
if not st.session_state.continue_clicked:
    # Initial text for the text area
    initial_text = "Enter your text here..."

    # Editable text area
    user_input = st.text_area("Edit your text below:", initial_text)

    # Button to proceed to the next step
    if st.button("Continue"):
        # Store the user input and set the continue button state to True
        st.session_state.user_input = user_input
        st.session_state.continue_clicked = True
        st.experimental_rerun()  # Rerun the app to update the state

# If continue button has been clicked, show the next step content
if st.session_state.continue_clicked:
    st.write("You entered:")
    st.write(st.session_state.user_input)
    # Add the logic for the next step here
    st.write("Proceeding to the next step...")
    
    # Example of the next step (could be anything you want)
    st.write("This is the next step content.")
