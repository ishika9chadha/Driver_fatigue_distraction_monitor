from flask import Flask, render_template, request, redirect, url_for, flash, Response, jsonify
import cv2
import mediapipe as mp
import numpy as np
import joblib
import pygame
import os

app = Flask(__name__)
app.secret_key = 'drivion_secret_key'

# Audio alerts
pygame.mixer.init()
try:
    pygame.mixer.music.load('alarm.wav')
except:
    pass

# Loading trained SVM model
model_path = 'Models/svm_drivion_model.pkl'
if os.path.exists(model_path):
    model = joblib.load(model_path)
    print("Loaded SVM model successfully!")
else:
    print("Warning: Model file not found in Models/ folder.")

# MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
face_detector = mp_face_detection.FaceDetection(min_detection_confidence=0.6)

current_state = {"pred": 0, "text": "Safe Driving"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/monitor')
def monitor():
    return render_template('monitor.html')

@app.route('/status_api')
def status_api():
    return jsonify(current_state)

import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load variables from the hidden .env file
load_dotenv()

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    name = request.form.get('name')
    sender_email = request.form.get('email')
    message_body = request.form.get('message')
    
    receiver_email = "ishikachadha098@gmail.com"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    
    # Securely fetch credentials (hidden from GitHub)
    my_gmail = os.getenv("MAIL_USERNAME")
    app_password = os.getenv("MAIL_PASSWORD")
    
    try:
        msg = MIMEMultipart()
        msg['From'] = my_gmail
        msg['To'] = receiver_email
        msg['Subject'] = f"New Feedback from {name} via Drivion"
        
        email_content = f"Name: {name}\nEmail: {sender_email}\n\nMessage:\n{message_body}"
        msg.attach(MIMEText(email_content, 'plain'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(my_gmail, app_password)
        server.sendmail(my_gmail, receiver_email, msg.as_string())
        server.quit()
        
        flash('Thank you! Your feedback has been successfully emailed.')
    except Exception as e:
        flash('Feedback received, but email delivery failed.')
        
    return redirect(url_for('index') + '#feedback')

def gen_frames():
    global current_state
    cap = cv2.VideoCapture(0)
    window_states = []

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        status_text = "Safe Driving"
        color = (0, 255, 0) 
        pred = 0

        results = face_detector.process(rgb)

        if results.detections and model is not None:
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                bw = int(bbox.width * w)
                bh = int(bbox.height * h)

                x1 = max(0, x - 20)
                y1 = max(0, y - 20)
                x2 = min(w, x + bw + 20)
                y2 = min(h, y + bh + 20)

                face_crop = frame[y1:y2, x1:x2]

                if face_crop.size > 0:
                    face_resized = cv2.resize(face_crop, (64, 64))
                    features = face_resized.flatten().reshape(1, -1) / 255.0

                    try:
                        pred = model.predict(features)[0]
                    except Exception:
                        pred = 0


                    if bw < bh * 0.75:
                        pred = 2  

                    window_states.append(pred)
                    if len(window_states) > 3:
                        window_states.pop(0)
                    smoothed_pred = max(set(window_states), key=window_states.count)

                    if smoothed_pred == 1:
                        status_text = "DROWSY WARNING!"
                        color = (0, 0, 255) 
                        pred = 1
                    elif smoothed_pred == 2:
                        status_text = "DISTRACTION DETECTED!"
                        color = (0, 140, 255) 
                        pred = 2
                    else:
                        status_text = "Safe Driving"
                        color = (0, 255, 0) 
                        pred = 0

                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)