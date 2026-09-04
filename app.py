import os
import asyncio
import streamlit as st
from groq import Groq
import edge_tts

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION & STARK HUD STYLING
# ---------------------------------------------------------
st.set_page_config(
    page_title="J.A.R.V.I.S. MARK II",
    page_icon="⚡",
    layout="centered"
)

# Stark Industries Custom UI Styling
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #00e5ff;
    }
    .stTextInput > div > div > input {
        background-color: #161b22;
        color: #00e5ff;
        border: 1px solid #00e5ff;
    }
    .stButton > button {
        background-color: #00e5ff;
        color: #0e1117;
        font-weight: bold;
        border-radius: 5px;
        border: none;
    }
    .stButton > button:hover {
        background-color: #ff0055;
        color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SECURITY PROTOCOL (PASSCODE AUTHENTICATION)
# ---------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 J.A.R.V.I.S. SECURITY PROTOCOL")
    st.subheader("Authentication Required")
    
    passcode = st.text_input("Enter Access Passcode:", type="password")
    if st.button("AUTHENTICATE"):
        if passcode == "StarkProtocol99":
            st.session_state.authenticated = True
            st.success("Access Granted. Welcome back, Sir.")
            st.rerun()
        else:
            st.error("Access Denied: Invalid Security Clearance.")
    st.stop()

# ---------------------------------------------------------
# 3. INITIALIZE SYSTEM MEMORY & GROQ CLIENT
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": "You are J.A.R.V.I.S., a highly intelligent AI assistant created and built by Master Sujal (not Tony Stark). Respond efficiently, maintain a suave, loyal personality, give credit to Master Sujal for your creation, and always address the user as Sir."
        }
    ]

# Async Function for Voice Generation (Edge-TTS)
async def generate_speech(text, output_file="jarvis_voice.mp3"):
    communicate = edge_tts.Communicate(text, "en-IN-PrabhatNeural")
    await communicate.save(output_file)
    return output_file

# ---------------------------------------------------------
# 4. MAIN HUD INTERFACE & CHAT DISPLAY
# ---------------------------------------------------------
st.title("⚡ J.A.R.V.I.S. MARK II HUD")
st.caption("STARK INDUSTRIES INTEGRATED INTELLIGENCE SYSTEM")

# Display Conversation History
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# ---------------------------------------------------------
# 5. USER COMMAND EXECUTION
# ---------------------------------------------------------
user_prompt = st.chat_input("Execute Command, Sir...")

if user_prompt:
    # Append User Input
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.write(user_prompt)

    # Fetch Groq API Key
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        st.error("System Failure: GROQ_API_KEY environment variable missing.")
        st.stop()

    client = Groq(api_key=api_key)

    # Generate Response from Groq
    with st.chat_message("assistant"):
        with st.spinner("Analyzing command..."):
            try:
                response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=st.session_state.messages
                )
                reply = response.choices[0].message.content
                st.write(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

                # Generate Voice Response
                asyncio.run(generate_speech(reply))
                if os.path.exists("jarvis_voice.mp3"):
                    st.audio("jarvis_voice.mp3", format="audio/mp3", autoplay=True)

            except Exception as e:
                st.error(f"System Error: {str(e)}")
