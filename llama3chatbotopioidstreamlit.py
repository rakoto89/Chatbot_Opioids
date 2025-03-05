import speech_recognition as sr
from gtts import gTTS
import os
import tempfile
import streamlit as st
import requests
import pdfplumber

# Function to convert speech to text
def speech_to_text(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand the audio."
        except sr.RequestError:
            return "Speech recognition service is unavailable."

# Function for text-to-speech output
def text_to_speech(response_text):
    tts = gTTS(text=response_text, lang='en')
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_file.name)
    return temp_file.name

# Voice input option
st.write("🎤 Upload an audio question (WAV format):")
audio_file = st.file_uploader("Choose an audio file", type=["wav"])

if audio_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(audio_file.read())
        temp_audio_path = temp_audio.name

    # Convert speech to text
    transcribed_text = speech_to_text(temp_audio_path)
    st.write(f"🗣️ Recognized Speech: {transcribed_text}")

    # Validate and process the transcribed text
    if validate_question(transcribed_text):
        response = query_llama3(transcribed_text, "")
    else:
        response = "I can only respond to inquiries about opioids, addiction, overdose, or withdrawal."

    # Display chatbot response
    st.write(f"🤖 Chatbot: {response}")

    # Convert chatbot response to speech and provide playback option
    audio_response_path = text_to_speech(response)
    st.audio(audio_response_path)
