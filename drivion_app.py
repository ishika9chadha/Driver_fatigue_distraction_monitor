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
