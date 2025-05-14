import streamlit as st
from openai import OpenAI
from langchain_openai import OpenAI as LangChainOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import pandas as pd
import datetime
import tempfile
import os
from github import Github
import base64

# Show title and description.
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses OpenAI's GPT-3.5 model to generate responses. "
    "Type '#save' to create a summary of the current conversation and save it to GitHub."
)

# Ask user for their OpenAI API key and GitHub token
openai_api_key = st.text_input("OpenAI API Key", type="password")
github_token = st.text_input("GitHub Personal Access Token", type="password")
github_repo_name = st.text_input("GitHub Repository (format: username/repo)", 
                                placeholder="yourusername/your-repo")

if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
elif not github_token or not github_repo_name:
    st.info("Please add your GitHub token and repository name to enable saving.", icon="🗝️")
else:
    # Create clients
    client = OpenAI(api_key=openai_api_key)
    langchain_llm = LangChainOpenAI(api_key=openai_api_key, temperature=0)
    
    # Initialize GitHub client
    g = Github(github_token)
    repo = g.get_repo(github_repo_name)
    
    # Create summarization chain
    summary_template = """
    Please create a concise summary of the following conversation:
    
    {conversation}
    
    Summary:
    """
    
    summary_prompt = PromptTemplate(
        input_variables=["conversation"],
        template=summary_template
    )
    
    summary_chain = LLMChain(llm=langchain_llm, prompt=summary_prompt)
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "save_count" not in st.session_state:
        st.session_state.save_count = 0
    
    # Function to save summary to temp file and GitHub
    def save_conversation_summary():
        # Format the conversation
        conversation_text = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}" 
            for msg in st.session_state.messages
        ])
        
        # Generate summary using LangChain
        summary = summary_chain.run(conversation=conversation_text)
        
        # Create timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save to temporary file
        temp_filename = f"save_temp_context_window_{timestamp.replace(':', '-').replace(' ', '_')}.txt"
        with tempfile.NamedTemporaryFile(mode='w', delete=False, 
                                       prefix="chat_summary_", 
                                       suffix=".txt") as temp_file:
            temp_file.write(f"Timestamp: {timestamp}\n")
            temp_file.write(f"Summary: {summary}\n")
            temp_file.write(f"\nFull Conversation:\n{conversation_text}\n")
            temp_path = temp_file.name
        
        # Prepare CSV data
        csv_data = {
            'timestamp': timestamp,
            'summary': summary,
            'conversation_length': len(st.session_state.messages),
            'full_conversation': conversation_text
        }
        
        # Update CSV in GitHub
        csv_filename = 'conversation_summaries.csv'
        try:
            # Try to get existing CSV file
            file_contents = repo.get_contents(csv_filename)
            existing_content = base64.b64decode(file_contents.content).decode()
            df = pd.read_csv(pd.io.common.StringIO(existing_content))
        except:
            # Create new dataframe if file doesn't exist
            df = pd.DataFrame(columns=['timestamp', 'summary', 'conversation_length', 
                                     'full_conversation'])
        
        # Add new row
        df = pd.concat([df, pd.DataFrame([csv_data])], ignore_index=True)
        
        # Convert dataframe back to CSV
        csv_content = df.to_csv(index=False)
        
        # Update or create file in GitHub
        try:
            # Update existing file
            repo.update_file(
                csv_filename,
                f"Update conversation summary - {timestamp}",
                csv_content,
                file_contents.sha
            )
        except:
            # Create new file
            repo.create_file(
                csv_filename,
                f"Create conversation summary file - {timestamp}",
                csv_content
            )
        
        st.session_state.save_count += 1
        
        return summary, temp_path
    
    # Display existing chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("What is up?"):
        # Check if user typed #save
        if prompt.lower() == "#save":
            with st.spinner("Generating summary and saving..."):
                try:
                    summary, temp_path = save_conversation_summary()
                    
                    # Add confirmation message
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": f"✅ Conversation saved!\n\n**Summary:** {summary}\n\n"
                                 f"**Temp file:** {temp_path}\n"
                                 f"**GitHub:** Updated conversation_summaries.csv"
                    })
                    
                    with st.chat_message("assistant"):
                        st.markdown(st.session_state.messages[-1]["content"])
                    
                except Exception as e:
                    st.error(f"Error saving conversation: {str(e)}")
        else:
            # Regular chat interaction
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate response
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Changed from gpt-4.1-nano
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            
            # Stream response
            with st.chat_message("assistant"):
                response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Sidebar with save information
    with st.sidebar:
        st.header("Save Information")
        st.write(f"Conversations saved: {st.session_state.save_count}")
        st.write("Type '#save' to save the current conversation")