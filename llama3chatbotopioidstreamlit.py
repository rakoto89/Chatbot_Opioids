import streamlit as st
import requests
import pdfplumber
import pyttsx3
import speech_recognition as sr

# Retrieve API credentials from Streamlit secrets
API_KEY = st.secrets["openrouter"]["API_KEY"]
API_URL = st.secrets["openrouter"]["LLAMA3_1_ENDPOINT"]

# Halt execution if API Key is missing
if not API_KEY:
    st.error("API Key not found! Ensure it's set in Streamlit Cloud secrets.")
    st.stop()

# Streamlit Chatbot Interface
st.title("💊 Opioid Awareness Chatbot")

# **Introductory message**
st.markdown(
    """
    ### Welcome to the Opioid Awareness Chatbot!
    Here you will learn all about opioids!
    """
)

# Extract text from a single PDF file
def extract_text(pdf_path):
    content = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                content += extracted_text + "\n"
    return content

# Read text from multiple PDFs in a directory
def process_pdf_folder(directory):
    text_data = ""
    for file in os.listdir(directory):
        if file.endswith(".pdf"):
            pdf_file_path = os.path.join(directory, file)
            text_data += extract_text(pdf_file_path) + "\n"
    return text_data

# Define opioid-related keywords
keywords = [
    "heroin", "opioid crisis", "rehab", "tolerance", "substance abuse",
    "overdose", "narcotics", "help", "opiates", "fentanyl",
    "withdrawal", "opioids", "support", "addiction", "naloxone", "drugs", "painkillers"
]

# Determine if a question is relevant
def validate_question(user_input):
    return any(term.lower() in user_input.lower() for term in keywords)

# Communicate with Llama 3 API for answers
def query_llama3(question, context=""):
    """Interacts with OpenRouter's Llama 3 API."""
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
    As an opioid education expert, provide clear and precise answers using the given document.
    If insufficient data is available, respond with: "I don't have enough information."
    """

    data = {
        "model": "meta-llama/llama-3-8b-instruct:free",
        "messages": [{"role": "user", "content": question}],
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        response_content = response.json()
        result = response_content.get("choices", [{}])[0].get("message", {}).get("content", "No response").strip()

        # Remove unnecessary phrases
        for phrase in ["Based on the document", "According to the document"]:
            result = result.replace(phrase, "").strip()

        return result

    except requests.exceptions.RequestException as error:
        st.error(f"API Connection Error: {str(error)}")
        return f"ERROR: Unable to connect to Llama 3. Details: {str(error)}"

# Function for voice input using speech recognition
def listen_to_speech():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        st.info("Listening... Please ask your question.")
        audio = recognizer.listen(source)

    try:
        question = recognizer.recognize_google(audio)
        st.write(f"👤 You: {question}")
        return question
    except sr.UnknownValueError:
        st.error("Sorry, I could not understand the audio.")
        return None
    except sr.RequestError:
        st.error("Sorry, I could not request results from Google Speech Recognition service.")
        return None

# Function to speak the response
def speak_response(response):
    engine = pyttsx3.init()
    engine.say(response)
    engine.runAndWait()

# Capture user input
question = st.text_input("👤 You: Enter a question about opioids:")

# Add voice button
if st.button("🎙️ Ask by Voice"):
    question = listen_to_speech()

if question:
    if validate_question(question):
        response = query_llama3(question, "")
    else:
        response = "I can only respond to inquiries about opioids, addiction, overdose, or withdrawal."

    # Display chatbot response
    st.write(f"🤖 Chatbot: {response}")
    
    # Speak the response
    speak_response(response)

