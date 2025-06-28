import streamlit as st
import requests
import json
import time
from datetime import datetime
import audio_recorder_streamlit as audio_recorder
import speech_recognition as sr
from pydub import AudioSegment
from gtts import gTTS
import os
import io
import pyttsx3
from googletrans import Translator
from io import BytesIO

import base64
ACCESS_TOKEN ="eyJraWQiOiIyMDE5MDcyNCIsImFsZyI6IlJTMjU2In0.eyJpYW1faWQiOiJJQk1pZC02OTIwMDA3N1o1IiwiaWQiOiJJQk1pZC02OTIwMDA3N1o1IiwicmVhbG1pZCI6IklCTWlkIiwianRpIjoiYWNkNGMyNTItYTAxYS00MmQ3LWJhMGYtNjc5YjNkYWE4YTkzIiwiaWRlbnRpZmllciI6IjY5MjAwMDc3WjUiLCJnaXZlbl9uYW1lIjoiU291amFueWEiLCJmYW1pbHlfbmFtZSI6IlMiLCJuYW1lIjoiU291amFueWEgUyIsImVtYWlsIjoic291amFueWFzNTgwQGdtYWlsLmNvbSIsInN1YiI6InNvdWphbnlhczU4MEBnbWFpbC5jb20iLCJhdXRobiI6eyJzdWIiOiJzb3VqYW55YXM1ODBAZ21haWwuY29tIiwiaWFtX2lkIjoiSUJNaWQtNjkyMDAwNzdaNSIsIm5hbWUiOiJTb3VqYW55YSBTIiwiZ2l2ZW5fbmFtZSI6IlNvdWphbnlhIiwiZmFtaWx5X25hbWUiOiJTIiwiZW1haWwiOiJzb3VqYW55YXM1ODBAZ21haWwuY29tIn0sImFjY291bnQiOnsidmFsaWQiOnRydWUsImJzcyI6ImQ2NGRhNjhhYzdlYzRhNDQ5MDA1NTUzNDc5NDYwOTkxIiwiaW1zX3VzZXJfaWQiOiIxMzkwMDc0OSIsImZyb3plbiI6dHJ1ZSwiaW1zIjoiMjk5OTE2NiJ9LCJtZmEiOnsiaW1zIjp0cnVlfSwiaWF0IjoxNzUxMTM2NTI5LCJleHAiOjE3NTExNDAxMjksImlzcyI6Imh0dHBzOi8vaWFtLmNsb3VkLmlibS5jb20vaWRlbnRpdHkiLCJncmFudF90eXBlIjoidXJuOmlibTpwYXJhbXM6b2F1dGg6Z3JhbnQtdHlwZTphcGlrZXkiLCJzY29wZSI6ImlibSBvcGVuaWQiLCJjbGllbnRfaWQiOiJkZWZhdWx0IiwiYWNyIjoxLCJhbXIiOlsicHdkIl19.m7YctTujI7RNsL4TbrD8j2n451BwRPgTa4VRLSvBfAkA-DxMhyfsFsHcpIHpEj3PI-SXNzIXI3G3R7lhci_-UUDfkMbLKVfK6oLoIxUrcqzkxxKRhL2ZrW1RKkr3rhUoA9QOCi3BaeFUxor8m6OkCZ2DsLBJPTrMP3HEtvUKkNfyOVbPCIx3S5EXISU6iJY_whTxJmt7ZhWVh5Poc5cLIZWXBflgPqamfGIsu-t0j7v85-G0GxcuJc06kf1cuHVSt72klG1Tm_CXXMYwVDHdRtbeAoKErcZwxq2e_xmwMWEUIifabM4lUFgzGb1xpj4KMjEMFJnWN5wYJ_fD4j9Zcg"
PROJECT_ID = "beeb36cb-848c-4ab8-a7f6-9a72e95c3df1"
MODEL_ID = "ibm/granite-3-3-8b-instruct"
API_URL = "https://us-south.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# === AUDIO FUNCTION ===
def speak(text, lang="en"):
    try:
        tts = gTTS(text=text, lang=lang)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        st.audio(audio_bytes, format="audio/mp3", autoplay=True)
        return audio_bytes
    except Exception as e:
        st.error(f"Audio error: {str(e)}")
        return None

# === UI ===
st.set_page_config(page_title="MeetMind", layout="wide")
st.markdown("""
<style>
    body, .stApp { background-color: #111; color: white; }
    .stButton>button { background-color: #0e76a8; color: white; }
    .stTextInput>div>input, .stTextArea>textarea { background-color: #222; color: white; }
</style>
""", unsafe_allow_html=True)

# === SESSION STATE ===
if 'users' not in st.session_state:
    st.session_state.users = {}
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'meeting_summary' not in st.session_state:
    st.session_state.meeting_summary = ""

# === AUTH ===
auth = st.sidebar.radio("User", ["🔐 Register", "🔓 Login"])
if auth == "🔐 Register":
    user = st.sidebar.text_input("New Username")
    pwd = st.sidebar.text_input("New Password", type="password")
    if st.sidebar.button("Register"):
        if user and pwd:
            st.session_state.users[user] = pwd
            st.sidebar.success("Registered! Go to Login.")
        else:
            st.sidebar.error("Fields cannot be empty.")
elif auth == "🔓 Login":
    user = st.sidebar.text_input("Username")
    pwd = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if user in st.session_state.users and st.session_state.users[user] == pwd:
            st.session_state.logged_in = True
            st.session_state.username = user
        else:
            st.sidebar.error("Invalid credentials.")

# === MAIN APP ===
if st.session_state.logged_in:
    nav = st.sidebar.radio("📂 Menu", ["📋 Summary", "🤖 Chatbot", "🚀 Features", "📌 Roadmap"])

    # === SUMMARY ===
    if nav == "📋 Summary":
        st.title("📋 Generate Meeting Summary")
        uploaded = st.file_uploader("📄 Upload .txt file", type="txt")
        transcript = ""

        if uploaded:
            try:
                transcript = uploaded.read().decode("utf-8")
            except Exception as e:
                st.error(f"File error: {str(e)}")
        else:
            transcript = st.text_area("Or paste transcript", value="")

        lang = st.selectbox("🌐 Translate to", ["en", "hi", "kn", "fr", "de", "None"])

        if st.button("🚀 Generate"):
            if not transcript.strip():
                st.warning("Transcript is empty.")
            else:
                with st.spinner("Processing..."):
                    try:
                        prompt = "Summarize this meeting transcript and extract action items:\n" + transcript
                        payload = {
                            "model_id": MODEL_ID,
                            "project_id": PROJECT_ID,
                            "messages": [{"role": "user", "content": prompt}],
                            "parameters": {
                                "decoding_method": "greedy",
                                "max_new_tokens": 300
                            }
                        }

                        response = requests.post(API_URL, headers=headers, json=payload)
                        response.raise_for_status()
                        output = response.json()["choices"][0]["message"]["content"]

                        if "Action Items:" in output:
                            summary, action = output.split("Action Items:", 1)
                        else:
                            summary = output
                            action = "No specific action items identified."

                        if lang != "None" and lang != "en":
                            translator = Translator()
                            summary = translator.translate(summary, dest=lang).text
                            action = translator.translate(action, dest=lang).text
                            tts_lang = lang
                        else:
                            tts_lang = "en"

                        final_output = f"Summary:\n{summary}\n\nAction Items:\n{action}"
                        st.session_state.meeting_summary = final_output

                        st.subheader("📝 Summary")
                        st.write(summary)
                        st.subheader("✅ Actions")
                        st.write(action)

                        speak(final_output, lang=tts_lang)

                        st.download_button("📥 Download Summary", data=final_output,
                                           file_name="meeting_summary.txt", mime="text/plain")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    # === CHATBOT ===
    elif nav == "🤖 Chatbot":
        st.title("🤖 Ask About the Meeting")
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                if "audio" in msg:
                    st.audio(io.BytesIO(msg["audio"]), format="audio/mp3")

        if prompt := st.chat_input("Ask a question about the meeting..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

            with st.spinner("Thinking..."):
                try:
                    full_prompt = f"Meeting Context:\n{st.session_state.meeting_summary}\n\nQuestion:\n{prompt}"
                    payload = {
                        "model_id": MODEL_ID,
                        "project_id": PROJECT_ID,
                        "messages": [{"role": "user", "content": full_prompt}],
                        "parameters": {
                            "decoding_method": "greedy",
                            "max_new_tokens": 200
                        }
                    }

                    response = requests.post(API_URL, headers=headers, json=payload)
                    response.raise_for_status()
                    reply = response.json()["choices"][0]["message"]["content"]

                    audio_bytes = speak(reply)
                    audio_data = audio_bytes.getvalue() if audio_bytes else None

                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": reply,
                        "audio": audio_data
                    })
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    # === FEATURES ===
    elif nav == "🚀 Features":
        st.title("🚀 Key Features")
        features_text = """
        - 🧠 AI-powered meeting summarization  
        - 🤖 Voice-enabled assistant  
        - 📄 Upload/paste transcripts  
        - 🌐 Multi-language support  
        - 🔊 Text-to-speech  
        - 📥 Downloadable summaries  
        """
        st.markdown(features_text)
        if st.button("🔊 Read Features"):
            speak(features_text)

    # === ROADMAP ===
    elif nav == "📌 Roadmap":
        st.title("📌 Future Plans")
        roadmap_text = """
        - 🗣️ Real-time transcription  
        - 📆 Calendar integration  
        - 🤝 Team collaboration features  
        - 📊 Analytics dashboard  
        - 🔍 Advanced search within transcripts  
        """
        st.markdown(roadmap_text)
        if st.button("🔊 Read Roadmap"):
            speak(roadmap_text)

else:
    st.warning("Please login to access MeetMind.")