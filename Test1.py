import streamlit as st
# The 'import' statement brings in code from other packages
# 'streamlit' is the web app framework, we nickname it 'st' for short


from openai import OpenAI
    # This imports the OpenAI client to talk to ChatGPT
    # The 'try' block attempts to import it 


# === PAGE CONFIGURATION ===
# This MUST be the first Streamlit command in your script
st.set_page_config(
    page_title="ChatGPT Prompt Builder",  # Browser tab title 
    page_icon="🤖",                       # Browser tab icon
    layout="wide"                         # Use full screen width
)

# === INITIALIZE SESSION STATE ===
# Session state persists data between user interactions
# Think of it as the app's memory while it's running
if 'messages' not in st.session_state:
    st.session_state.messages = []  # Store conversation history

# === API KEY SETUP ===
# You can set your API key in several ways:
# 1. Directly in code (not recommended for production)
# 2. Using Streamlit secrets (recommended)
# 3. Using environment variables

# Method 1: Direct (replace with your actual key)
# api_key = "sk-your-api-key-here"

# Method 2: Using Streamlit secrets (recommended)
# Create .streamlit/secrets.toml file with: OPENAI_API_KEY = "your-key"
try:
    api_key = st.secrets["OpenAI_Token"]
except:
    api_key = st.text_input("Enter your OpenAI API key:", type="password")
    if not api_key:
        st.warning("Please enter your OpenAI API key to continue")
        st.stop()

# Initialize the OpenAI client with your API key
client = OpenAI(api_key=api_key)

# === PROMPT ENGINEERING TEMPLATES ===
# These are behind-the-scenes instructions for ChatGPT
# You can modify these to change how ChatGPT responds
prompt_templates = {
    "Professional tone": "Please respond in a professional, business-appropriate manner. ",
    "Detailed explanation": "Please provide a comprehensive and detailed explanation. ",
    "Include examples": "Please include practical examples to illustrate your points. ",
    "Keep it concise": "Please keep your response brief and to the point. ",
    "Technical language": "Please use technical terminology and assume technical knowledge. ",
    "Simple language": "Please explain in simple terms that anyone can understand. ",
    "Step by step": "Please break down your response into clear, numbered steps. ",
    "Pros and cons": "Please include both advantages and disadvantages in your analysis. ",
    "Creative approach": "Please be creative and think outside the box in your response. ",
    "Data-driven": "Please support your response with data, statistics, or research when possible. "
}

# === APP TITLE ===
st.title("ChatGPT Prompt Builder 🤖")
st.markdown("Build better prompts with pre-configured options")

# === SIDEBAR CONFIGURATION ===
# The sidebar appears on the left side of the screen
with st.sidebar:
    st.header("🛠️ Prompt Configuration")
    
    # Multiselect widget - users can choose multiple options
    selected_options = st.multiselect(
        "Select prompt modifiers:",
        options=list(prompt_templates.keys()),  # Show all available templates
        default=[],  # No options selected by default
        help="Choose how you want ChatGPT to respond"
    )
    
    # Model selection
    model_choice = st.selectbox(
        "Select GPT Model:",
        ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"],
        help="GPT-3.5 is faster and cheaper, GPT-4 is more capable"
    )
    
    # Temperature slider (controls creativity)
    temperature = st.slider(
        "Response creativity:",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="Lower = more focused, Higher = more creative"
    )
    
    # Show selected options
    if selected_options:
        st.success(f"Active modifiers: {len(selected_options)}")
        with st.expander("View selected modifiers"):
            for option in selected_options:
                st.write(f"✓ {option}")

# === MAIN CONTENT AREA ===
col1, col2 = st.columns([2, 1])  # Create two columns, left one twice as wide

with col1:
    st.header("💬 Ask Your Question")
    
    # Text area for user input
    user_question = st.text_area(
        "Enter your question:",
        placeholder="Example: Explain how machine learning works",
        height=120,  # Height in pixels
        key="user_input"  # Unique identifier for this widget
    )
    
    # Submit button
    submit_button = st.button(
        "Submit to ChatGPT",
        type="primary",  # Makes it a colored button
        use_container_width=True  # Full width button
    )

with col2:
    st.header("📋 Current Prompt")
    # Show user what prompt will be sent
    if selected_options:
        st.caption("Your prompt will include:")
        for option in selected_options:
            st.write(f"• {option}")
    else:
        st.caption("No modifiers selected")

# === PROCESS THE REQUEST ===
# This code runs when the submit button is clicked
if submit_button:
    if not user_question:
        st.error("❌ Please enter a question first!")
    else:
        # Build the complete prompt
        # Start with the prompt engineering instructions
        system_prompt = "You are a helpful AI assistant. "
        
        # Add each selected modifier
        for option in selected_options:
            system_prompt += prompt_templates[option]
        
        # Show the complete prompt being sent (for transparency)
        with st.expander("🔍 View complete prompt"):
            st.text(f"System: {system_prompt}")
            st.text(f"User: {user_question}")
        
        # Make the API call
        with st.spinner("🤔 ChatGPT is thinking..."):
            try:
                # Call the OpenAI API
                response = client.chat.completions.create(
                    model=model_choice,  # The GPT model to use
                    messages=[
                        {"role": "system", "content": system_prompt},  # Instructions
                        {"role": "user", "content": user_question}     # User's question
                    ],
                    temperature=temperature,  # Creativity level
                    max_tokens=2000  # Maximum response length
                )
                
                # Extract the response text
                answer = response.choices[0].message.content
                
                # Display the response
                st.success("✅ Response received!")
                
                # Create a nice display box for the answer
                with st.container():
                    st.markdown("### ChatGPT's Response:")
                    st.markdown(answer)
                
                # Store in session state (optional - for history)
                st.session_state.messages.append({
                    "question": user_question,
                    "answer": answer,
                    "modifiers": selected_options
                })
                
            except Exception as e:
                # Handle any errors
                st.error(f"❌ An error occurred: {str(e)}")
                st.info("Common issues: Invalid API key, rate limits, or network errors")

# === CONVERSATION HISTORY ===
# Show previous conversations (optional feature)
if st.session_state.messages:
    st.markdown("---")  # Horizontal line
    st.header("📜 Conversation History")
    
    # Display each previous Q&A
    for i, msg in enumerate(reversed(st.session_state.messages)):
        with st.expander(f"Question {len(st.session_state.messages) - i}: {msg['question'][:50]}..."):
            st.write("**Modifiers used:**", ", ".join(msg['modifiers']) if msg['modifiers'] else "None")
            st.write("**Question:**", msg['question'])
            st.write("**Answer:**", msg['answer'])

# === HELP SECTION ===
st.markdown("---")
with st.expander("ℹ️ How to use this app"):
    st.markdown("""
    ### Quick Start Guide:
    
    1. **Enter your API Key** (if not already configured)
    2. **Select prompt modifiers** from the sidebar to customize how ChatGPT responds
    3. **Choose a GPT model** (3.5 is faster, 4 is smarter)
    4. **Adjust creativity** with the temperature slider
    5. **Type your question** in the text area
    6. **Click Submit** and wait for the response
    
    ### Tips:
    - Combine multiple modifiers for better results
    - Use GPT-4 for complex questions
    - Lower temperature for factual responses
    - Higher temperature for creative tasks
    """)

# === FOOTER ===
st.markdown("---")
st.caption("Built with Streamlit and OpenAI API")
