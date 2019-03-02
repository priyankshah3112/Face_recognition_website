from flask import Flask,redirect, render_template, Response,request,session
from video_stream.camera import VideoCamera
import sqlite3
from collections import Counter
import numpy as np
from video_stream.vectorizer import vect
from video_stream.detectors import FaceDetector
import cv2
from video_stream.detectors import FaceDetector
from wtforms import validators,Form,TextAreaField,TextField
from video_stream.camera_register import RegisterVideoCamera
import pickle
import os
db="C://projects//video_stream//guest.sqlite"
cur_dir = os.path.dirname(__file__)
clf = pickle.load(open(os.path.join(cur_dir,
                 'pkl_objects',
                 'classifier.pkl'), 'rb'))
print(cur_dir)
def classify(document):
    label = {0: 'negative', 1: 'positive'}
    X = vect.transform([document])
    y = clf.predict(X)[0]
    proba = np.max(clf.predict_proba(X))
    return label[y], proba

def sqlite_entry(path,name):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    q="INSERT INTO users(id,name) VALUES (NULL,"+'"'+name+'")'
    print(q)
    c.execute(q)
    conn.commit()
    conn.close()
app = Flask(__name__,static_folder="C://projects//video_stream//static//images")
class RegisterForm(Form):
    name_guest=TextField('Enter your name',[validators.DataRequired()])
    email=TextField('Enter your email',[validators.email()])
class HotelReviewForm(Form):
    hotel_review = TextAreaField('Enter your review', [validators.DataRequired()])
class RegisterForm1(Form):
    name=TextField('Enter your name',[validators.DataRequired()])



@app.route('/')
def index():
    return render_template('wiredwiki.html')


@app.route('/success')
def success():
    conn = sqlite3.connect(db)
    c = conn.cursor()
    q = "SELECT name FROM Logged_in WHERE id=(SELECT MAX(id) FROM Logged_in)"
    c.execute(q)
    name = c.fetchone()[0]
    print(name)
    conn.close()
    session['logged_in'] = True
    return render_template("logged_in_res.html",name=name)
@app.route('/login')
def login():
    return render_template('index.html')
def gen(camera):

    while True:
        frame,name_list = camera.get_frame()
        if(len(name_list)==30):
            data=Counter(name_list)
            logged_in_guest=str(data.most_common(1)[0][0])
            print(logged_in_guest)
            conn = sqlite3.connect(db)
            c = conn.cursor()
            q = "INSERT INTO Logged_in(id,name) VALUES (NULL," + '"' + logged_in_guest + '")'
            c.execute(q)
            conn.commit()
            conn.close()
            camera.__del__()



        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    yield (b'--frame\r\n'
           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')




@app.route('/register_face',methods=['POST'])
def register_face():
     name=""
     form=RegisterForm(request.form)
     if request.method == 'POST' and form.validate():
         name = request.form['name_guest']
         sqlite_entry(db,name)
         print(name+"INSIDE REGISTERFACE")
     return render_template('register_face.html',name=name)

def register_gen(camera):
    counter=0
    while True:
        counter=counter+1
        frame = camera.get_frame()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/register_feed')
def register_feed():
    return Response(register_gen(RegisterVideoCamera()),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/thanks',methods=['POST'])
def thanks():
    form=RegisterForm(request.form)
    if request.method=='POST' and form.validate():
        name=request.form['name_guest']
        return render_template('thanks.html',name=name)

@app.route('/guest_name')
def get_name():
    form=RegisterForm(request.form)
    return render_template("get_name.html",form=form)
@app.route('/logOut')
def logOut():
    session['logged_in']=False
    return render_template('failed_login.html')

@app.route('/hotelreview')
def hotelreview():
    form=HotelReviewForm(request.form)
    return render_template("hotel_review.html",form=form)
@app.route('/results', methods=['POST'])
def results():
    form = HotelReviewForm(request.form)
    if request.method == 'POST' and form.validate():
        hotel_review = request.form['hotel_review']
        y, proba = classify(hotel_review)
        return render_template('results.html',
                                content=hotel_review,
                                prediction=y,
                                probability=round(proba*100, 2))
    return render_template('reviewform.html', form=form)
@app.route('/thanks_register')
def thanks_register():
    li=[]
    for i in range(20):
        li.append(cv2.imread('C://projects//video_stream//photo/'+str(i)+'.jpg', 0))

    return render_template('thanks_register.html',list=li)
@app.route('/check_form')
def check_form():
    form=RegisterForm(request.form)
    return  render_template("get_name.html",form=form)
@app.route('/instructions')
def instructions():
    return  render_template("instructions.html")

@app.route('/instruction_login')
def instructions_login():
    return  render_template("instructions_login.html")
if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)

