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