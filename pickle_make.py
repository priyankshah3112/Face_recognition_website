import sys
import os
import numpy as np
import pickle
import _compat_pickle
from face_recognition_system.videocamera import VideoCamera
from face_recognition_system.detectors import FaceDetector
import face_recognition_system.operations as op
import cv2
import cv2.face

from PIL import Image

from matplotlib import pyplot as plt
from cv2 import __version__
people_folder = "C://projects//video_stream//people"
people = [person for person in os.listdir("C://projects//video_stream//people")]

try:
    recognizer = cv2.face.createLBPHFaceRecognizer()
    threshold = 4000
except: print("some error in recognixer")

images = []
labels = []
labels_people = {}
for i, person in enumerate(people):
    labels_people[i] = person
    recognizer.setLabelInfo(i,person)
    for image in os.listdir(people_folder +'/' +person):
        images.append(cv2.imread(people_folder +'/'+ person + '/' + image, 0))
        labels.append(i)

try:
    recognizer.train(images, np.array(labels))

except:
    print("\nOpenCV Error: Do you have at least two people in the database?\n")
    sys.exit()


recognizer.save('C://projects//video_stream//recognizer.xml')


#dest=os.path.join('video_streaming','pkl_objects')
#if not os.path.exists(dest):
#    os.makedirs(dest)
#pickle.dump(recognizer,open(os.path.join(dest,'recognizer.pkl'),'wb'),protocol=4)
#print(type(recognizer))
#f = open("recognizer.cpickle", "w")
#(pickle.dump(recognizer,f))
#f.close()
#print((recognizer.))
