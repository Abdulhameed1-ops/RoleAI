import streamlit as st
import cv2
import dlib
import numpy as np
from imutils import face_utils

# Load dlib's face detector and facial landmark predictor
detector = dlib.get_frontal_face_detector()
predictor_path = "shape_predictor_68_face_landmarks.dat"
predictor = dlib.shape_predictor(predictor_path)

st.title("Live Face Detection and Facial Landmark Tuning App")

# Sidebar controls for tuning
st.sidebar.header("Tuning Parameters")

upsample_num = st.sidebar.slider("Upsample Number (face detector)", 0, 3, 1)
landmark_color = st.sidebar.color_picker("Landmark Color", "#00FF00")
landmark_radius = st.sidebar.slider("Landmark Radius", 1, 10, 2)
landmark_thickness = st.sidebar.slider("Landmark Thickness", 1, 5, 1)

# Webcam input checkbox
use_webcam = st.sidebar.checkbox("Use Webcam", value=True)

if use_webcam:
    # Open webcam
    cap = cv2.VideoCapture(0)
    FRAME_WINDOW = st.image([])

    while True:
        ret, frame = cap.read()
        if not ret:
            st.error("Failed to capture video")
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        faces = detector(frame_rgb, upsample_num)

        for face in faces:
            shape = predictor(frame_rgb, face)
            shape = face_utils.shape_to_np(shape)

            for (x, y) in shape:
                cv2.circle(frame_rgb, (x, y), landmark_radius,
                           tuple(int(landmark_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)),
                           landmark_thickness)

        FRAME_WINDOW.image(frame_rgb)

    cap.release()
else:
    st.write("Please upload an image to detect faces and landmarks.")
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        st.image(image_rgb, caption="Uploaded Image", use_column_width=True)

        faces = detector(image_rgb, upsample_num)
        st.write(f"Number of faces detected: {len(faces)}")

        for face in faces:
            shape = predictor(image_rgb, face)
            shape = face_utils.shape_to_np(shape)

            for (x, y) in shape:
                cv2.circle(image_rgb, (x, y), landmark_radius,
                           tuple(int(landmark_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)),
                           landmark_thickness)

        st.image(image_rgb, caption="Image with Facial Landmarks", use_column_width=True)
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
