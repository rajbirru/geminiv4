import streamlit as st
import google.generativeai as genai
import os

st.title("Chat with Gemini LLM")

# Access your GOOGLE_API_KEY
google_api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=google_api_key)

# Function to initialize the Gemini LLM model and start a chat session
def init_gemini_model():
    model = genai.GenerativeModel('gemini-pro')
    chat = model.start_chat(history=[])
    return chat

# Initialize the chat session
if 'gemini_chat' not in st.session_state:
    st.session_state.gemini_chat = init_gemini_model()

# Initialize message history
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display messages from the chat history
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# Input for the user's message
user_input = st.chat_input("Type your message here...")

# When the user sends a message
if user_input:
    # Append user message to chat history
    st.session_state.messages.append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.markdown(user_input)

    # Send the user input to the LLM and fetch the response
    response = st.session_state.gemini_chat.send_message(user_input)

    # Process the LLM response and update the chat history
    llm_response = ''.join([chunk.text for chunk in response])
    st.session_state.messages.append({'role': 'assistant', 'content': llm_response})
    with st.chat_message('assistant'):
        st.markdown(llm_response)
