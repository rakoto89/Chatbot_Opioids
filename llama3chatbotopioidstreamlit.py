import os
import requests
import pdfplumber
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load API endpoint and key securely
LLAMA3_ENDPOINT = os.getenv("LLAMA3_ENDPOINT")
LLAMA3_API_KEY = os.getenv("LLAMA3_API_KEY")

# Debugging: Print API key (Remove this after confirming it's working)
print(f"Loaded API Key: {LLAMA3_API_KEY}")

# Ensure API Key is loaded correctly
if not LLAMA3_API_KEY:
    st.error("API Key not found! Check your .env file.")
    st.stop()

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    return text

# Function to read multiple PDFs from a folder
def read_pdfs_in_folder(folder_path):
    pdf_text = ""
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            pdf_text += extract_text_from_pdf(pdf_path) + "\n"
    return pdf_text

# List of relevant opioid-related keywords
relevant_topics = [
    "opioids", "addiction", "overdose", "withdrawal", "fentanyl", "heroin",
    "painkillers", "narcotics", "opioid crisis", "naloxone", "rehab", "opiates",
    "opium", "substance abuse", "drugs", "tolerance", "help", "assistance", "support"
]

# Function to check if a question is relevant
def is_question_relevant(question):
    return any(topic.lower() in question.lower() for topic in relevant_topics)

# Function to send the question to Llama 3 API
def get_llama3_response(question, context):
    """
    Sends a request to OpenRouter Llama 3 API.
    """
    headers = {
        "Authorization": f"Bearer {LLAMA3_API_KEY.strip()}",
        "Content-Type": "application/json"
    }

    prompt = f"""
    You are an expert in opioid education. Answer the user's question as clearly as possible using the provided document as reference.
    If the document doesn't contain the answer, just say "I don't have enough information."
    """

    payload = {
        "model": "meta-llama/llama-3-8b-instruct",
        "messages": [{"role": "user", "content": question}],
    }

    try:
        response = requests.post(LLAMA3_ENDPOINT, headers=headers, json=payload, timeout=10)
        response.raise_for_status()  # Raise an error for HTTP issues
        data = response.json()
        response_text = data.get("choices", [{}])[0].get("message", {}).get("content", "No response").strip()

        # Remove unwanted phrases
        unwanted_phrases = ["Based on the document", "According to the document"]
        for phrase in unwanted_phrases:
            response_text = response_text.replace(phrase, "").strip()

        return response_text

    except requests.exceptions.RequestException as e:
        st.error(f"Llama 3 API error: {str(e)}")
        return f"ERROR: Failed to connect to Llama 3 instance. Details: {str(e)}"

# Streamlit Interface
st.title("📖 Opioid Awareness Chatbot")
st.markdown("Welcome to the Opioid Awareness Chatbot! Here you will learn all about opioids.")

# User Input
user_question = st.text_input("Ask a question related to opioids:")

if user_question:
    if is_question_relevant(user_question)
