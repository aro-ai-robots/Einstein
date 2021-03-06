#!/usr/bin/env python
from statistics import mode
import speech_recognition as sr
import cv2
from keras.models import load_model
import numpy as np
import os
import time
import sys
import socket

from utils.datasets import get_labels
from utils.inference import detect_faces
from utils.inference import draw_text
from utils.inference import draw_bounding_box
from utils.inference import apply_offsets
from utils.inference import load_detection_model
from utils.preprocessor import preprocess_input
from utils.chat import *

#When the code runs, it will ask for the IP address of the server you want to connect to.
ip_address = input("Enter the IP address of the server: ")
sleeper = 5


def recognize_speech_from_mic(recognizer, microphone):
    """Transcribe speech from recorded from `microphone`.

    Returns a dictionary with three keys:
    "success": a boolean indicating whether or not the API request was
               successful
    "error":   `None` if no error occured, otherwise a string containing
               an error message if the API could not be reached or
               speech was unrecognizable
    "transcription": `None` if speech could not be transcribed,
               otherwise a string containing the transcribed text
    """
    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    # try recognizing the speech in the recording
    # if a RequestError or UnknownValueError exception is caught,
    #     update the response object accordingly
    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response
    
def makeConversation(emotion_text):
	prompt = get_prompt(emotion_text)
	print(prompt)
	time.sleep(sleeper)
	sock.send('6'.encode())
	os.system('echo %s | festival --tts' % prompt) 
	sock.send('7'.encode())
	response = recognize_speech_from_mic(recognizer,microphone)
	if not response["success"]:
		print("I didn't catch that. What did you say?\n")
	if response["error"]:
		print("ERROR: {}".format(response["error"]))
	try:
		print("You said: {}".format(response["transcription"]))
		botResp = respond(response["transcription"])
		print(botResp)
		sock.send('6'.encode())
		os.system('echo %s | festival --tts' % botResp) 
		sock.send('7'.encode())
	except:
		botResp = "I cannot understand. Try speaking more clearly."
		print(botResp)
		sock.send('6'.encode())
		os.system('echo %s | festival --tts' % botResp) 
		sock.send('7'.encode())
		
#creating voice recognizer and microphone
recognizer = sr.Recognizer()

#use sr.Microphone.list_microphone_names() to find the device index
#if device_index arg is omitted, it will use the default microphone
microphone = sr.Microphone()

# parameters for loading data and images
detection_model_path = '../trained_models/detection_models/haarcascade_frontalface_default.xml'
emotion_model_path = '../trained_models/emotion_models/fer2013_mini_XCEPTION.102-0.66.hdf5'
emotion_labels = get_labels('fer2013')

# hyper-parameters for bounding boxes shape
frame_window = 10
emotion_offsets = (20, 40)

# loading models
face_detection = load_detection_model(detection_model_path)
emotion_classifier = load_model(emotion_model_path, compile=False)

# getting input model shapes for inference
emotion_target_size = emotion_classifier.input_shape[1:3]

# starting lists for calculating modes
emotion_window = []

# starting socket connection
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (ip_address, 4000)
sock.connect(server_address)

# starting video streaming
cv2.namedWindow('window_frame')
video_capture = cv2.VideoCapture(0)

#Chatbot introduction
# all sock.send commands are for sending data to server
intro = "Hello, I am Herbot A. Simon. I am a social robot who can detect emotion and respond accordingly."
sock.send('6'.encode())
print(intro)
os.system('echo %s | festival --tts' % intro) 
sock.send('7'.encode())

# While loop preforms Facial then Emotion Recogintion
# then will base robots next responses based on
# what Emotion it has recognized 
while True:
    for x in range(5):
        bgr_image = video_capture.read()[1]
    bgr_image = cv2.resize(bgr_image, (1000, 1000))
    gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
    rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
    faces = detect_faces(face_detection, gray_image)
    
    bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
    cv2.imshow('window_frame', bgr_image)
    cv2.waitKey(1)
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break
    
    for face_coordinates in faces:
        x1, x2, y1, y2 = apply_offsets(face_coordinates, emotion_offsets)
        gray_face = gray_image[y1:y2, x1:x2]
        try:
            gray_face = cv2.resize(gray_face, (emotion_target_size))
        except:
            continue

        gray_face = preprocess_input(gray_face, True)
        gray_face = np.expand_dims(gray_face, 0)
        gray_face = np.expand_dims(gray_face, -1)
        emotion_prediction = emotion_classifier.predict(gray_face)
        emotion_probability = np.max(emotion_prediction)
        emotion_label_arg = np.argmax(emotion_prediction)
        emotion_text = emotion_labels[emotion_label_arg]

        if emotion_text == 'angry':
	        sock.send('3'.encode())
	        makeConversation(emotion_text)
        elif emotion_text == 'sad':
	        sock.send('4'.encode())
	        makeConversation(emotion_text)
        elif emotion_text == 'happy':
	        sock.send('2'.encode())
	        makeConversation(emotion_text)
        elif emotion_text == 'surprise':
	        sock.send('5'.encode())
	        makeConversation(emotion_text)
        elif emotion_text == 'neutral':
	        sock.send('1'.encode())
	        makeConversation(emotion_text)
        else:
	        sock.close()
	        
video_capture.release()
