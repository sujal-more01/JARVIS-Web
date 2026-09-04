import os
import asyncio
import streamlit as st
from groq import Groq
import edge_tts

# Page Configuration
st.set_page_config(page_title="JARVIS MARK II", page_icon="⚡", layout="centered")

# Security Passcode Check
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 J.A.R.V.I.S. Security Protocol")
    passcode = st.text_input("Enter Access Passcode:", type="password")
    if st.button("AUTHENTICATE"):
        if passcode == "StarkProtocol99":
            st.session_state.authenticated = True
            st.success("Access Granted. Welcome, Sir.")
            st.rerun()
        else:
            st.error("Access Denied: Invalid Passcode.")
    st.stop()

# Initialize Chat Messages State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are J.A.R.V.I.S., Tony Stark's AI assistant. Respond politely, efficiently, and refer to the user as Sir."}
    ]

# Function for Voice Generation via edge-tts
async def generate_speech(text, output_file="response.mp3"):
    communicate = edge_tts.Communicate(text, "en-IN-PrabhatNeural")
    await communicate.save(output_file)
    return output_file

# Main HUD Interface
st.title("⚡ J.A.R.V.I.S. MARK II HUD")

# Display Previous Conversation
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# User Input Form
with st.form(key="command_form", clear_on_submit=True):
    user_prompt = st.text_input("Execute Command:", key="user_input")
    submit_button = st.form_submit_button(label="SEND COMMAND")

if submit_button and user_prompt:
    # Append User Message
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    # Groq API Call
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        st.error("System Error: GROQ_API_KEY Missing in Streamlit Secrets.")
        st.stop()

    client = Groq(api_key=api_key)
    
    with st.spinner("J.A.R.V.I.S. is processing..."):
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=st.session_state.messages
        )
        reply = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": reply})

        # Generate Audio
        audio_file = asyncio.run(generate_speech(reply))

    # Refresh UI to show response
    st.rerun()

# Play audio for the latest assistant message if available
if os.path.exists("response.mp3"):
    st.audio("response.mp3", format="audio/mp3", autoplay=True)
