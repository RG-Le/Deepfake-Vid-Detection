import json
import os
import cv2
import numpy as np
import tensorflow as tf


class DataProcessing:
    def __init__(self, inputShape, trainingDir=None):
        self.inputShape = inputShape
        self.trainingDir = trainingDir
        self.detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def processVid(self, vidPath):
        cap = cv2.VideoCapture(vidPath)
        processedFrames = []
        frameCnt = 0

        while cap.isOpened():
            ret, frame = cap.read()

            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            if len(faces) > 0:
                for (x, y, w, h) in faces:
                    x1 = x
                    y1 = y
                    x2 = x + w
                    y2 = y + h

                    cropImg = frame[y1:y2, x1:x2]
                    resizeImg = cv2.resize(cropImg, self.inputShape)
                    normalizedImg = resizeImg / 255.0
                    processedFrames.append(normalizedImg)
            else:
                continue

            frameCnt += 1
            if frameCnt == 10:
                break

        cap.release()

        return processedFrames

    def generateDataset(self, limit=1e9):
        with open(os.path.join(self.trainingDir, 'metadata.json'), 'r') as f:
            data = json.load(f)

        trainingDataFiles = [f for f in os.listdir(self.trainingDir) if f.endswith(".mp4")]

        X = []
        Y = []

        VidCounter = 0

        for idx, vid in enumerate(trainingDataFiles):
            vidPath = os.path.join(self.trainingDir, vid)
            X.append(self.processVid(vidPath))
            if data[vid]['label'] == 'REAL':
                Y.append(1)
            elif data[vid]['label'] == 'FAKE':
                Y.append(0)

            VidCounter += 1

            if VidCounter == int(limit):
                break

        X = np.array(X)
        Y = np.array(Y)

        return X, Y

    def generateSinglePredData(self, vidPath):
        X = self.processVid(vidPath)
        X = np.array(X)
        X = np.expand_dims(X, axis=0)
        return X

    def generateMultiplePredData(self, testDir):
        testingDataFiles = [f for f in os.listdir(testDir) if f.endswith(".mp4")]
        X = []
        for vid in testingDataFiles:
            vidPath = os.path.join(testDir, vid)
            X.append(self.processVid(vidPath))

        X = np.array(X)
        return X
