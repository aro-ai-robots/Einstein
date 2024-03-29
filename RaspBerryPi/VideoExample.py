import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
import time


camera = PiCamera()
camera.resolution=(640,480)
camera.framerate = 32
camera.rotation = 180
rawCapture = PiRGBArray(camera, size=(640,480))
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):    
    frame = frame.array
    cv2.imshow('Video', frame)
    rawCapture.truncate(0)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
video_capture.release()
cv2.destroyAllWindows()
