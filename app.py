import streamlit as st
import asyncio
import edge_tts
import base64
import os
from groq import Groq

# Page Config
st.set_page_config(page_title="J.A.R.V.I.S. MARK II", page_icon="⚡", layout="centered")

# --- STARK HUD STYLING ---
st.markdown("""
    <style>
    .main { background-color: #0A0A0A; }
    stApp { background-color: #0A0A0A; }
    h1 { color: #FF6600; text-align: center; font-family: 'Consolas', monospace; }
    .stTextInput input { background-color: #121212; color: #FF9900; border: 1px solid #FF5500; }
    .stButton button { background-color: #FF5500; color: black; font-weight: bold; width: 100%; border: none; }
    .stButton button:hover { background-color: #FF8800; color: black; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ J.A.R.V.I.S. MARK II HUD")

# --- PRIVATE PASSWORD GUARD ---
SECURITY_PASSWORD = "StarkProtocol99"  # <--- Apna Unique Password Yahan Set Karein

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.subheader("🔒 Security Authentication Required")
    pwd_input = st.text_input("Enter Passcode:", type="password")
    if st.button("AUTHENTICATE"):
        if pwd_input == SECURITY_PASSWORD:
            st.session_state.authenticated = True
            st.success("Access Granted. Welcome, Boss.")
            st.rerun()
        else:
            st.error("Access Denied: Invalid Security Clearance.")
    st.stop()

# --- MAIN APP LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are J.A.R.V.I.S., an elite autonomous intelligence designed exclusively by Boss. "
                "If asked who built you, state explicitly that Boss built you. "
                "Respond strictly in pure, highly intellectual English with sharp wit. Keep responses concise (1-2 sentences) and address user as 'Boss'."
            )
        }
    ]

# Display Chat History
for msg in st.session_state.messages[1:]:
    role_label = "[YOU]" if msg["role"] == "user" else "[JARVIS]"
    st.write(f"**{role_label}:** {msg['content']}")

# Input Box
user_prompt = st.text_input("Execute Command:", placeholder="Type or speak command, Boss...")

# Audio TTS Generator
async def generate_speech(text):
    output_file = "jarvis_web_voice.mp3"
    communicate = edge_tts.Communicate(text, "en-IN-PrabhatNeural")
    await communicate.save(output_file)
    return output_file

if st.button("SEND COMMAND") and user_prompt:
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    
    # GROQ API Call
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        st.error("System Error: GROQ_API_KEY Missing.")
        st.stop()

    client = Groq(api_key=api_key)
   response = client.chat.completions.create(model="llama-3.1-8b-instant",messages=st.session_state.messages)
    
    reply = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": reply})
    
    # Voice Output
    audio_file = asyncio.run(generate_speech(reply))
    
    st.rerun()
