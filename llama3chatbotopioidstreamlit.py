import streamlit as st
import requests
import pdfplumber
import speech_recognition as sr
from gtts import gTTS
import tempfile
import os

# Inject JavaScript to handle audio recording
st.markdown(
    """
    <script>
        let mediaRecorder;
        let audioChunks = [];

        function startRecording() {
            navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.start();
                
                mediaRecorder.ondataavailable = event => {
                    audioChunks.push(event.data);
                };

                mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    const audioUrl = URL.createObjectURL(audioBlob);
                    const downloadLink = document.createElement('a');
                    downloadLink.href = audioUrl;
                    downloadLink.download = 'recorded_audio.wav';
                    downloadLink.click();
                };
            })
            .catch(error => console.error("Error accessing microphone: ", error));
        }

        function stopRecording() {
            if (mediaRecorder) {
                mediaRecorder.stop();
            }
        }
    </script>
    """,
    unsafe_allow_html=True,
)

# Function to convert speech to text
def speech_to_text(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand the audio."
        except sr.RequestError:
            return "Speech recognition service is unavailable."

# Function for text-to-speech response
def text_to_speech(response_text):
    tts = gTTS(text=response_text, lang='en')
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio.name)
    return temp_audio.name

# Button to trigger JavaScript recording
st.write("🎙️ Click to record your voice question:")
st.markdown('<button onclick="startRecording()">Start Recording</button>', unsafe_allow_html=True)
st.markdown('<button onclick="stopRecording()">Stop Recording</button>', unsafe_allow_html=True)

# Upload recorded file
st.write("🔼 Upload your recorded file (WAV format):")
audio_file = st.file_uploader("Upload recorded audio", type=["wav"])

if audio_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(audio_file.read())
        temp_audio_path = temp_audio.name

    # Convert speech to text
    transcribed_text = speech_to_text(temp_audio_path)
    st.write(f"🗣️ Recognized Speech: {transcribed_text}")

    # Process the recognized text
    if validate_question(transcribed_text):
        response = query_llama3(transcribed_text, "")
    else:
        response = "I can only respond to inquiries about opioids, addiction, overdose, or withdrawal."

    # Display chatbot response
    st.write(f"🤖 Chatbot: {response}")

    # Convert chatbot response to speech
    audio_response_path = text_to_speech(response)
    st.audio(audio_response_path)

