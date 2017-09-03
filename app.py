# import cv2
# img = cv2.imread('sof.jpg') # load a dummy image
# while(1):
#     img = cv2.imread('ball.png')
#     cv2.imshow('input',img)
#     k = cv2.waitKey(33)
#     if k==27:    # Esc key to stop
#         break
#     elif k==-1:  # normally -1 returned,so don't print it
#         continue
#     else:
#         print k # else print its value

from flask import Flask, render_template, request, send_file
from werkzeug import secure_filename
import json
import numpy as np
import cv2

app = Flask(__name__)

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@app.route('/')
def hello():
    return render_template('main.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        print(type(f.filename))
        filename = 'images/inputs/'+secure_filename(f.filename) # gives secure filename
        f.save(filename)
        print(filename)
        im = cv2.imread(filename, 0)
        # # ret, thresh = cv2.threshold(im, 1, 255, 0)
        # cv2.namedWindow('input')
        # cv2.imshow('input', im)
        # k = cv2.waitKey(0) % 256
        cv2.imwrite('images/outputs/test_img.png', im)
        # return render_template("main.html", image_name=f.filename)
        return send_file('images/outputs/test_img.png', mimetype='image/png')


@app.route('/uploadmask', methods=['GET', 'POST'])
def upload_mask():
    if request.method == 'POST':
        f = request.files['canvasImage']
        print(type(f.filename))
        filename = 'images/inputs/'+secure_filename(f.filename)+'.png'  # gives secure filename
        f.save(filename)
        print(filename)
        im = cv2.imread(filename, -1)
        # # ret, thresh = cv2.threshold(im, 1, 255, 0)
        # cv2.namedWindow('input')
        # cv2.imshow('input', im)
        # k = cv2.waitKey(0) % 256
        cv2.imwrite('images/outputs/test_img.png', im)
        # return render_template("main.html", image_name=f.filename)
        return send_file('images/outputs/test_img.png', mimetype='image/png')


@app.route('/postmethod', methods = ['POST'])
def get_post_javascript_data():
    jsdata = request.form['javascript_data']
    return json.loads(jsdata)[0]


@app.route('/signUpUser', methods=['POST'])
def signUpUser():
    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        im = cv2.imread(f.filename, 0)
        print 'hello working fine here'
        # # ret, thresh = cv2.threshold(im, 1, 255, 0)
        # cv2.namedWindow('input')
        # cv2.imshow('input', im)
        # k = cv2.waitKey(0) % 256
        cv2.imwrite('test_img.png', im)
        # return render_template("main.html", image_name=f.filename)
        return send_file('test_img.png', mimetype='image/png')


if __name__ == '__main__':
    app.run(debug=True)