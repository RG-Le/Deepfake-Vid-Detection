from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
import cv2
import numpy as np
import tensorflow as tf
import os

app = FastAPI()
classNames = ['Real', 'Fake']
model = load_model('deepfake-detection-model2.h5')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=["*"],
    allow_headers=["*"],
)


def processFrames(vid_Path):
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    X = []
    cap = cv2.VideoCapture(vid_Path)
    frameCnt = 0
    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Detecting the Faces in the images
        faces = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) > 0:
            # print("Faces in Vid", idx, "are:", len(faces))
            for (x, y, w, h) in faces:
                x1 = x
                y1 = y
                x2 = x + w
                y2 = y + h

                # Cropping, Resizing and normalizing the singular frame
                # print("Procssing Frame")
                cropImg = frame[y1:y2, x1:x2]
                resizeImg = cv2.resize(cropImg, (128, 128))
                normalizedImg = resizeImg / 255.0
                # Adding each frame to frame_list
                X.append(normalizedImg)
                break
        else:
            continue

        frameCnt += 1

        if frameCnt == 10:
            break
        else:
            continue

    X = np.array(X)
    X = np.expand_dims(X, axis=0)
    return X


def predict(videoPath):
    X = processFrames(videoPath)

    probs = model.predict(X)
    if np.argmax(probs) == 1:
        return {
            "message": "Video Is REAL!!"
        }
    return {
        "message": "Video is FAKE!!!"
    }


@app.post("/upload_video/")
async def upload_video(video: UploadFile = File(...)):
    allowed_extensions = ('.mp4', '.avi', '.mov', '.mkv')
    file_extension = video.filename[-4:].lower()

    if file_extension not in allowed_extensions:
        return {
            'error': 'Unsupported file format!!'
        }

    with open(f"uploaded_videos/{video.filename}", "wb") as buffer:
        buffer.write(video.file.read())

    video_path = f"uploaded_videos/{video.filename}"
    print("Video Saved Loacally")
    res = predict(video_path)
    print("Detection Complete!!")
    os.remove(video_path)
    print("Removed file from directory!!")

    return res


@app.get("/")
async def root():
    return {
        "message": "Hello!! Server is Running!!"
    }
