import streamlit as st
import cv2
import mediapipe as mp
import numpy as np

st.title("Live Face Landmark Detection with Mediapipe")

# Sidebar controls for tuning
st.sidebar.header("Tuning Parameters")
landmark_radius = st.sidebar.slider("Landmark Radius", 1, 5, 2)
landmark_color = st.sidebar.color_picker("Landmark Color", "#00FF00")

# Initialize Mediapipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=5, refine_landmarks=True, min_detection_confidence=0.5)

# Webcam input checkbox
use_webcam = st.sidebar.checkbox("Use Webcam", value=True)

if use_webcam:
    cap = cv2.VideoCapture(0)
    FRAME_WINDOW = st.image([])

    while True:
        ret, frame = cap.read()
        if not ret:
            st.error("Failed to capture video")
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(frame_rgb)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                for landmark in face_landmarks.landmark:
                    x = int(landmark.x * frame.shape[1])
                    y = int(landmark.y * frame.shape[0])
                    color = tuple(int(landmark_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                    cv2.circle(frame_rgb, (x, y), landmark_radius, color, -1)

        FRAME_WINDOW.image(frame_rgb)

    cap.release()
else:
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        results = face_mesh.process(image_rgb)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                for landmark in face_landmarks.landmark:
                    x = int(landmark.x * image.shape[1])
                    y = int(landmark.y * image.shape[0])
                    color = tuple(int(landmark_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                    cv2.circle(image_rgb, (x, y), landmark_radius, color, -1)

        st.image(image_rgb, caption="Image with Face Landmarks", use_column_width=True)
    else:
        st.write("Please upload an image.")
                    
