import streamlit as st
from openai import OpenAI

import pandas as pd
import plotly.express as px

# === PAGE CONFIGURATION ===
# This MUST be the first Streamlit command in your script
st.set_page_config(
    page_title="ChatGPT Prompt Builder",  # Browser tab title
    page_icon="🤖",                       # Browser tab icon
    layout="centered"                     # Use centered screen width
)

# === INITIALIZE SESSION STATE ===
# Session state persists data between user interactions
# Think of it as the app's memory while it's running
if 'messages' not in st.session_state:
    st.session_state.messages = []  # Store conversation history

# === PROMPT ENGINEERING TEMPLATES ===
# These are behind-the-scenes instructions for ChatGPT
# You can modify these to change how ChatGPT responds
prompt_templates = {
    "The Straight Shooter": "Prepared, responsive, and focused on role clarity. Gives clear information, respects your time, and expects a smooth process. Needs efficiency, alignment confirmation, and clear timelines. ",
    "The Strategist": "Sees hiring as part of a broader org design or long-term plan. Talks about future goals, team structure, and alignment. Needs help defining the ideal profile and expects pushback on unrealistic asks. ",
    "The Checklist Manager": "Fixated on rigid requirements and credentials. Often says, They must have XYZ years of… or lists specific companies. Needs structure, validation, and strict alignment to their checklist. ",
    "The Unprepared or Indifferent": "Busy, distracted, or disengaged. Often lacks a Job Description, vague about the role, and minimally involved. Needs structured support, proactive reminders, and intake handholding. ",
    "The Technical Expert": "Deep domain knowledge, often focused on technical depth. May use jargon, fixate on tests, and downplay soft skills. Needs help translating expertise into realistic hiring signals. ",
    "The Pressure Cooker": "Operating under urgency or executive pressure. Often says, We needed someone yesterday, with many open roles. Needs fast traction, updates, and a sense of progress. ",
    "The Skeptic or Past-Burned": "Cautious from past bad hires or TA experiences. Micromanages, slow to trust, and may challenge recruiter input. Needs transparency, reliability, and re-earning of credibility. ",
    "The Overconfident Marketer": "Assumes the role or company will attract talent on its own. Skips sourcing detail and minimizes candidate concerns. Needs grounded market insight and candidate-centric perspective. ",
    "The Aspirational Builder": "Sets a high bar, seeking A+ players to elevate the team. Talks about elite hiring and upgrading the team. Needs sourcing creativity, competitive intel, and strong calibration. "
}

# === APP TITLE ===

st.markdown(
        """
        <div style='display: flex; align-items: baseline; gap: 8px;'>
            <span style='font-size: 2rem; font-weight: 700;'>Your Copilot for Hiring Manager Calls</span>
            <span style='font-size: 1.25rem; font-weight: 400;'>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("Smarter Intakes. Better Hires.")

# === GOOGLE SHEETS DATA IMPORT AND VISUALIZATION ===
st.header("📊 Applicant Pipeline Analysis")

# Google Sheets URL input
google_sheets_url = st.text_input(
    "Enter Google Sheets URL (make sure it's publicly accessible):",
    placeholder="https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit#gid=0",
    help="Your sheet must be shared publicly or 'Anyone with the link can view'"
)

# Process the Google Sheets URL
if google_sheets_url:
    try:
        # Convert Google Sheets URL to CSV export URL
        if '/edit' in google_sheets_url:
            sheet_id = google_sheets_url.split('/d/')[1].split('/')[0]
        else:
            sheet_id = google_sheets_url.split('/d/')[1].split('/')[0]
        
        # Construct CSV export URL
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        
        # Read the CSV data
        df = pd.read_csv(csv_url)
        
        # Expected columns
        expected_columns = [
            'Applicant ID', 'Application Date', 'Recruiter Name', 'Last Name', 
            'Gender', 'Date of Birth', 'Phone Number', 'Email', 'Address', 
            'City', 'State', 'Zip Code', 'Country', 'Education Level', 
            'Years of Experience', 'Desired Salary', 'Job Title', 'Status'
        ]
        
        # Check if all expected columns exist
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            st.warning(f"⚠️ Missing columns: {', '.join(missing_columns)}")
        
        # Filter data based on selected status
        if 'Status' in df.columns and ta_metric_1_choice:
            filtered_df = df[df['Status'] == ta_metric_1_choice]
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Applicants", len(df))
            with col2:
                st.metric(f"{ta_metric_1_choice} Status", len(filtered_df))
            with col3:
                if len(df) > 0:
                    percentage = (len(filtered_df) / len(df)) * 100
                    st.metric("Percentage", f"{percentage:.1f}%")
            
            # Create gender distribution chart for filtered status
            if 'Gender' in filtered_df.columns and len(filtered_df) > 0:
                # Group by gender and count
                gender_counts = filtered_df['Gender'].value_counts().reset_index()
                gender_counts.columns = ['Gender', 'Count']
                
                # Create bar chart using Plotly
                fig = px.bar(
                    gender_counts, 
                    x='Gender', 
                    y='Count',
                    title=f'Gender Distribution for Status: {ta_metric_1_choice}',
                    labels={'Count': 'Number of Applicants'},
                    color='Gender',
                    color_discrete_map={
                        'Male': '#3498db',
                        'Female': '#e74c3c',
                        'Other': '#95a5a6',
                        'Prefer not to say': '#7f8c8d'
                    }
                )
                
                # Update layout
                fig.update_layout(
                    showlegend=False,
                    height=400,
                    xaxis_title="Gender",
                    yaxis_title="Count"
                )
                
                # Display the chart
                st.plotly_chart(fig, use_container_width=True)
                
                # Show data table
                with st.expander("View detailed data"):
                    st.dataframe(gender_counts)
            else:
                st.info("No data available for the selected status or Gender column is missing.")
        else:
            st.error("Status column not found in the data.")
            
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Make sure your Google Sheet is publicly accessible and the URL is correct.")

st.divider()

# === SIDEBAR CONFIGURATION ===
# The sidebar appears on the left side of the screen
with st.sidebar:

    st.sidebar.markdown(
        """
        <div style='text-align: center; margin-top: -30px; margin-bottom: 20px;'>
            <span style='font-size: 2rem; font-weight: 700;'>Intakeology</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.header("📋 Job Profile")

    # TEST JOB PROFILE SELECTBOX
    job_function_choice = st.multiselect(
        "Select Job Function:",
        ["Finance","Information Technology","Call Center","Sales","Back Office"]
    )

    st.divider()

    st.header("💼 Hiring Manager")
 
    # Define your placeholder value
    default_placeholder = "Hiring Manager"

    # Show the input field with pre-filled value
    user_input_hiring_manager = st.text_input(
        "Enter your hiring manager name:",
        value=default_placeholder
    )

    # Check if the input is still unchanged or empty
    if user_input_hiring_manager.strip() == default_placeholder or not user_input_hiring_manager.strip():
        st.warning("⚠️ Make sure to personalize before sending.")

    # Use in output
    hiring_manager_name = user_input_hiring_manager.strip() or default_placeholder

    # Hiring Manager Persona selection
    selected_options = st.selectbox(
        "Select Hiring Manager Persona:",
        options=list(prompt_templates),  # Show all available templates,
        help="What is the type of hiring manager you're going to talk to?"
    )

    st.markdown(
    f"<p style='font-size:0.85rem; font-style:italic; color:#555;'>{prompt_templates[selected_options]}</p>",
    unsafe_allow_html=True
    )

    st.divider()

    st.header("🧑 Recruiting Configuration")

    # TEST METRIC SELECTBOX
    recruiter_choice = st.selectbox(
        "Select Recruiter Name:",
        ["Beth","John","Anthony","Sam"]
    )

    # TEST METRIC SELECTBOX
    ta_metric_1_choice = st.selectbox(
        "Select Status:",
        ["Applied","In Review","Interviewing","Offered","Rejected"]
    )

    st.divider()

    st.header("🛠️ System Configuration")

        # ChatGPT Model selection
    model_choice = st.selectbox(
        "Select GPT Model:",
        ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"],
        help="GPT-3.5 is faster and cheaper, GPT-4 is more capable"
    )

    # Method 2: Using Streamlit secrets (recommended)
    # Create .streamlit/secrets.toml file with: OPENAI_API_KEY = "your-key"
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.", icon="🗝️")

# Initialize the OpenAI client outside the sidebar
# This ensures it's available for the submit button
client = None
if openai_api_key:
    client = OpenAI(api_key=openai_api_key)

# === MAIN CONTENT AREA ===
col1, col2 = st.columns([2, 1])  # Create two columns, left one twice as wide. the right column is blank for now

with col1:
    st.header("💬 Ask Your Question")
    
    # Text area for user input
    user_question = st.text_area(
        "Enter your question:",
        placeholder="Example: What are the key skills we should prioritize for this role?",
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
    st.header(" ")
    # Show user what prompt will be sent

# === PROCESS THE REQUEST ===
# This code runs when the submit button is clicked
if submit_button:
    if not user_question:
        st.error("❌ Please enter a question first!")
    elif not client:
        st.error("❌ Please enter your OpenAI API key in the sidebar!")
    else:
        # Build a comprehensive system prompt with all context
        system_prompt = f"""You are a helpful Talent Acquisition AI Assistant who is an expert in the hiring manager job intake process. 

CONTEXT FOR THIS INTERACTION:
- Job Function(s): {', '.join(job_function_choice) if job_function_choice else 'Not specified'}
- Hiring Manager: {hiring_manager_name}
- Hiring Manager Persona: {selected_options}
- Persona Details: {prompt_templates[selected_options]}
- Recruiter: {recruiter_choice}
- Key Metric Focus: {ta_metric_1_choice}

Given this context, provide tailored advice that:
1. Addresses the specific hiring manager personality type
2. Considers the job function requirements
3. Helps {recruiter_choice} optimize for {ta_metric_1_choice}
4. Provides actionable strategies for this specific intake call with {hiring_manager_name}

Remember to adapt your communication style and recommendations based on the hiring manager persona described above."""
        
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
                    "persona": selected_options,
                    "context": {
                        "job_functions": job_function_choice,
                        "hiring_manager": hiring_manager_name,
                        "recruiter": recruiter_choice,
                        "metric": ta_metric_1_choice
                    }
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
            st.write("**Persona used:**", msg.get('persona', 'Not specified'))
            st.write("**Context:**")
            if 'context' in msg:
                st.write(f"- Job Functions: {', '.join(msg['context']['job_functions']) if msg['context']['job_functions'] else 'None'}")
                st.write(f"- Hiring Manager: {msg['context']['hiring_manager']}")
                st.write(f"- Recruiter: {msg['context']['recruiter']}")
                st.write(f"- Metric: {msg['context']['metric']}")
            st.write("**Question:**", msg['question'])
            st.write("**Answer:**", msg['answer'])

# === HELP SECTION ===
st.markdown("---")
with st.expander("ℹ️ How to use this app"):
    st.markdown("""
    ### Quick Start Guide:
    
    1. **Configure the Job Profile** - Select relevant job functions
    2. **Set up Hiring Manager details** - Enter their name and select their persona type
    3. **Choose your configuration** - Select your name and the metric you're optimizing for
    4. **Enter your API Key** - Add your OpenAI API key in the System Configuration section
    5. **Ask your question** - Type your question about the hiring manager intake
    6. **Submit** - Click the button to get personalized advice
    
    ### Example Questions:
    - What questions should I ask in the intake call?
    - How should I handle pushback on the timeline?
    - What's the best way to discuss salary expectations?
    - How do I get buy-in for a more flexible job description?
    - What are the red flags I should watch for?
    
    ### Tips:
    - Be specific in your questions for better advice
    - The more context you provide, the more tailored the response
    - Use GPT-4 for more nuanced responses
    - Review the conversation history to track insights across multiple interactions
    """)

# === FOOTER ===
st.markdown("---")
st.caption("Copyright (c) 2025 Reportingology. All Rights Reserved.")
