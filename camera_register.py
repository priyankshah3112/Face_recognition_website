import cv2
from video_stream.detectors import FaceDetector
import video_stream.operations as op
import sqlite3
import os
from matplotlib import pyplot as plt
from cv2 import __version__
import numpy as np
import shutil

class RegisterVideoCamera(object):
    db = "C://projects//video_stream//guest.sqlite"
    guest_train=[]
    recognizer=cv2.face.createLBPHFaceRecognizer()
    recognizer.load("C://projects//video_stream//recognizer.xml")
    counter=1
    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        self.video_register = cv2.VideoCapture(1)
        # If you decide to use video.mp4, you must have this file in the folder
        # as the main.py.
        # self.video = cv2.VideoCapture('video.mp4')

    def __del__(self):
        self.video_register.release()

    def sqlite_get(self):
        conn = sqlite3.connect("C://projects//video_stream//guest.sqlite")
        c = conn.cursor()
        q = "SELECT * FROM users WHERE id=(SELECT MAX(id) FROM users)"
        c.execute(q)
        list=c.fetchone()
        name = list[1]
        id = list[0]
        conn.close()
        return name, id

    def get_frame(self):
        li=[]
        db = "C://projects//video_stream//guest.sqlite"
        detector = FaceDetector('C://projects//video_stream//frontal_face.xml')
        success, image = self.video_register.read()
        jpeg=image
        frame=image
        faces_coord = detector.detect(frame, False)
        if (len(faces_coord)):
            for (x, y, w, h) in faces_coord:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (150, 150, 0), 8)
            # We are using Motion JPEG, but OpenCV defaults to capture raw images,
            # so we must encode it into JPEG in order to correctly display the
            # video stream.
            self.guest_train.append(self.add_people(frame,faces_coord))
            ##print("Lenght"+str(len(self.guest_train)))
            if(len(self.guest_train)==20):
                guest_name,guest_id=self.sqlite_get()
                self.__del__()
                for i in range(20):
                    li.append(guest_id)
                arr=np.array(li)
                self.recognizer.update(self.guest_train,arr)
                self.recognizer.setLabelInfo(guest_id,guest_name)
                self.recognizer.save('C://projects//video_stream//recognizer.xml')
                for i in range(20):
                    cv2.imwrite('C://projects//video_stream//photo/'+str(i)+'.jpg',
                                self.guest_train[i])
                image=self.guest_train[18]
                self.guest_train.clear()
            ret, jpeg = cv2.imencode('.jpg', image)

        return jpeg.tostring()

    def get_images(self,frame, faces_coord, shape):
        """ Perfrom transformation on original and face images.

        This function draws the countour around the found face given by faces_coord
        and also cuts the face from the original image. Returns both images.

        :param frame: original image
        :param faces_coord: coordenates of a rectangle around a found face
        :param shape: indication of which shape should be drwan around the face
        :type frame: numpy array
        :type faces_coord: list of touples containing each face information
        :type shape: String
        :return: two images containing the original plus the drawn contour and
                 anoter one with only the face.
        :rtype: a tuple of numpy arrays.
        """
        faces_img=[]
        if shape == "rectangle":
            faces_img = op.cut_face_rectangle(frame, faces_coord)
            frame = op.draw_face_rectangle(frame, faces_coord)
        elif shape == "ellipse":
            faces_img = op.cut_face_ellipse(frame, faces_coord)
            frame = op.draw_face_ellipse(frame, faces_coord)
        faces_img = op.normalize_intensity(faces_img)
        faces_img = op.resize(faces_img)
        return (faces_img)

    def recognize_face(self,frame,faces_coord,shape):
        threshold=105
        pred=0
        name=""
        conf=0
        faces_img=self.get_images(frame,faces_coord,shape)
        recognizer=self.recognizer
        for i, face_img in enumerate(faces_img):
                collector = cv2.face.MinDistancePredictCollector()
                recognizer.predict(face_img, collector)

                conf = collector.getDist()
                pred = collector.getLabel()
                name=recognizer.getLabelInfo(pred)
                print("Prediction: " + str(pred))
                print('Confidence: ' + str(round(conf)))
                print('Threshold: ' + str(threshold))
        return pred,conf,threshold,name




    def add_people(self,frame,faces_coord):
        detector = FaceDetector('C://projects//video_stream//frontal_face.xml')
        self.counter = 1
        timer = 0


        while self.counter < 21:


            if len(faces_coord):

                face_img = self.get_images(frame, faces_coord, "rectangle")
                print("FUCK")
                # save a face every second, we start from an offset '5' because
                # the first frame of the camera gets very high intensity
                # readings.
                if timer % 100 == 5:
                    ##self.guest_train[self.counter]=face_img[0]
                    print('Images Saved:' + str(self.counter))
                    self.counter += 1
                    if self.counter==21:
                        self.__del__()
                    return face_img[0]

            timer += 5







