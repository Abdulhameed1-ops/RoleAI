import streamlit as st
import requests
import os
from PyPDF2 import PdfReader
from docx import Document
from io import BytesIO
import pyttsx3
import tempfile


# Function to extract text from PDF
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


# Function to extract text from DOCX
def extract_text_from_docx(file):
    doc = Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text


# Function to call Cohere API for text summarization or conversion to podcast-like text
def generate_podcast_text(text):
    api_key = 'bf5Qur8XrFgfmiAoU0KL111qbVud0P2KGQFZvdW8'  # Replace with your Cohere API key
    url = "https://api.cohere.ai/chat",
          "Authorization": f"Bearer {api_key}",
          "Content-Type": "application/json"
    }
    
    # 2025 model (latest)
    payload = {
        "model": "command-xlarge-2025",  # Replace with the latest model if needed
        "prompt": f"Transform the following text into a natural, conversational podcast script:\n\n{text}",
        "max_tokens": 1000,
        "temperature": 0.7
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()['text']
    else:
        st.error(f"Error from Cohere API: {response.status_code} - {response.text}")
        return None


# Function to convert text to speech (podcast audio)
def text_to_speech(text):
    # Initialize the pyttsx3 engine
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # Adjust speech rate
    engine.setProperty('volume', 1)  # Volume (0.0 to 1.0)
    
    # Create a temporary file to store audio output
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio_file:
        audio_path = temp_audio_file.name
        engine.save_to_file(text, audio_path)
        engine.runAndWait()
    
    return audio_path


# Streamlit app layout
st.title("Document to Podcast Converter")

# Upload document
uploaded_file = st.file_uploader("Upload a document (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])

if uploaded_file:
    # Read document text
    if uploaded_file.type == "application/pdf":
        text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = extract_text_from_docx(uploaded_file)
    else:
        text = uploaded_file.read().decode("utf-8")

    if text:
        st.subheader("Extracted Text Preview:")
        st.text_area("Document Content", text, height=300)

        # Generate podcast script using Cohere API
        with st.spinner("Generating podcast script..."):
            podcast_text = generate_podcast_text(text)

        if podcast_text:
            st.subheader("Generated Podcast Script:")
            st.text_area("Podcast Script", podcast_text, height=300)

            # Convert the script to speech (audio)
            st.spinner("Converting script to speech...")
            audio_path = text_to_speech(podcast_text)

            # Display the audio player
            st.subheader("Listen to the Podcast:")
            audio_file = open(audio_path, "rb")
            st.audio(audio_file, format="audio/mp3")

            os.remove(audio_path)  # Clean up temporary audio file
