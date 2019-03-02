import cv2
from video_stream.detectors import FaceDetector
import video_stream.operations as op
from cv2 import __version__
class VideoCamera(object):
    predicted_names=[]
    recognizer=cv2.face.createLBPHFaceRecognizer()
    recognizer.load("C://projects//video_stream//recognizer.xml")
    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        self.video = cv2.VideoCapture(1)

        # If you decide to use video.mp4, you must have this file in the folder
        # as the main.py.
        # self.video = cv2.VideoCapture('video.mp4')

    def __del__(self):
        self.video.release()



    def get_frame(self):
        if(len(self.predicted_names)>30):
            self.predicted_names.clear()
        detector = FaceDetector('C://projects//video_stream//frontal_face.xml')
        success, image = self.video.read()
        frame=image
        faces_coord = detector.detect(frame, False)
        if(len(faces_coord)):

                pred,conf,threshold,name=self.recognize_face(frame,faces_coord,"rectangle")
                if conf < threshold:
                    self.predicted_names.append(name)
                    cv2.putText(frame, name.capitalize(),
                                (faces_coord[0][0], faces_coord[0][1] - 2),
                                cv2.FONT_HERSHEY_PLAIN, 1.7, (206, 0, 209), 2,
                                cv2.LINE_AA)
                else:

                    self.predicted_names.append('Unknown')
                    cv2.putText(frame, "Unknown",
                            (faces_coord[0][0], faces_coord[0][1]),
                            cv2.FONT_HERSHEY_PLAIN, 1.7, (206, 0, 209), 2,
                            cv2.LINE_AA)

        for (x, y, w, h) in faces_coord:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (150, 150, 0), 8)
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        ret, jpeg = cv2.imencode('.jpg', image)

        return jpeg.tostring(),self.predicted_names

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
        if(len(self.predicted_names)==1):
            self.recognizer = cv2.face.createLBPHFaceRecognizer()
            self.recognizer.load("C://projects//video_stream//recognizer.xml")
        threshold=95
        pred=-1
        name="XYZ"
        conf=-1
        faces_img=self.get_images(frame,faces_coord,shape)

        for i, face_img in enumerate(faces_img):
                collector = cv2.face.MinDistancePredictCollector()
                self.recognizer.predict(face_img, collector)
                conf = collector.getDist()
                pred = collector.getLabel()
                name=self.recognizer.getLabelInfo(pred)
                print(name)
                print(pred)
                print("Prediction: " + str(pred))
                print('Confidence: ' + str(round(conf)))
                print('Threshold: ' + str(threshold))
        return pred,conf,threshold,name
