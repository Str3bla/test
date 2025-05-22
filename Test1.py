import streamlit as st
import openai
from openai import OpenAI

# Page configuration - this must be the first Streamlit command
st.set_page_config(
    page_title="ChatGPT Prompt Builder",
    page_icon="🤖",
    layout="wide"
)

# Initialize OpenAI client
# You'll need to set your API key here or use Streamlit secrets
client = OpenAI(api_key=st.secrets["OpenAI_Token"])

# Title of the app
st.title("ChatGPT Prompt Builder 🤖")

# Sidebar for multiselect options
with st.sidebar:
    st.header("Prompt Options")
    
    # Example multiselect - we'll customize this based on your needs
    selected_options = st.multiselect(
        "Select prompt modifiers:",
        ["Professional tone", "Detailed explanation", "Include examples", 
         "Keep it concise", "Technical language", "Simple language"]
    )
    
    # Display selected options
    if selected_options:
        st.write("Selected:", selected_options)

# Main content area
st.header("Ask ChatGPT")

# Text input for user's question
user_question = st.text_area(
    "Enter your question:",
    placeholder="Type your question here...",
    height=100
)

# Submit button
if st.button("Submit to ChatGPT", type="primary"):
    if user_question:
        # Build the prompt with engineering
        # This is where we'll add your custom prompt engineering
        
        with st.spinner("Thinking..."):
            try:
                # Make API call to ChatGPT
                # We'll add the actual implementation here
                
                # Display response
                st.success("Response received!")
                # Response will be displayed here
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter a question first!")

# Instructions or help text
with st.expander("How to use this app"):
    st.write("""
    1. Select prompt modifiers from the sidebar
    2. Enter your question in the text area
    3. Click 'Submit to ChatGPT' to get a response
    """)
