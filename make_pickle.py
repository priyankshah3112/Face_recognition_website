import sys
import os
import numpy as np
import pickle
from face_recognition_system.videocamera import VideoCamera
from face_recognition_system.detectors import FaceDetector
import face_recognition_system.operations as op
import cv2
import cv2.face
from cv2 import __version__
people_folder="C://projects//video_stream//people"
people = [person for person in os.listdir(people_folder)]
recognizer = cv2.face.createLBPHFaceRecognizer()
threshold = 105
images = []
labels = []
labels_people = {}
for i, person in enumerate(people):
    labels_people[i] = person
    for image in os.listdir(people_folder +'/'+ person):
        images.append(cv2.imread(people_folder + person + '/' + image, 0))
        labels.append(i)
    try:
        recognizer.train(images, np.array(labels))
    except:
        print("\nOpenCV Error: Do you have at least two people in the database?\n")
        sys.exit()
dest = os.path.join('video_stream', 'pkl_objects')
if not os.path.exists(dest):
    os.makedirs(dest)
pickle.dump(recognizer, open(os.path.join(dest, 'recognizer.pkl'), 'wb'), protocol=4)