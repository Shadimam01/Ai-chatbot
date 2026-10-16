import streamlit as st
import requests

# Page Configuration
st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="centered")
import streamlit as st

# Custom background image styling with a dark gradient overlay for text readability
background_css = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: linear-gradient(rgba(15, 15, 15, 0.85), rgba(15, 15, 15, 0.85)), 
                      url(https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQBEXJdlMylF0yuXZt9e12CZdUtsXyJd-iaYRahhtSfMg&s=10);
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}

[data-testid="stHeader"] {
    background: rgba(0, 0, 0, 0);
}
</style>
"""

# Inject CSS into Streamlit
st.markdown(background_css, unsafe_allow_html=True)

st.title("🤖 AI Chatbot")
st.caption("Powered by Google Gemini 3.5 Flash & FastAPI")

# Backend API endpoint URL
BACKEND_URL = "http://127.0.0.1:8000/chat"

# Initialize Chat Memory in Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar options
with st.sidebar:
    st.header("Settings")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Display all previous chat messages
for msg in st.session_state.messages:
    role = "user" if msg["role"] == "user" else "assistant"
    with st.chat_message(role):
        st.write(msg["content"])

# User Input Box
if prompt := st.chat_input("Type your message here..."):
    # 1. Display user message locally
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # 2. Format message history for the backend
    formatted_history = [
        {
            "role": "user" if m["role"] == "user" else "model",
            "content": m["content"]
        }
        for m in st.session_state.messages[:-1]  # exclude the new message
    ]

    # 3. Call Backend FastAPI with loading spinner
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                payload = {
                    "user_message": prompt,
                    "history": formatted_history
                }
                
                response = requests.post(BACKEND_URL, json=payload, timeout=30)

                if response.status_code == 200:
                    bot_reply = response.json().get("response", "No response received.")
                    st.write(bot_reply)
                    
                    # 4. Append bot reply to local state
                    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                else:
                    st.error(f"Error {response.status_code}: {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to backend server. Make sure FastAPI is running on port 8000!")