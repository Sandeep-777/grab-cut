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

from flask import Flask, render_template, request, send_file, send_from_directory
from werkzeug import secure_filename
import json
import os
import numpy as np
import cv2


img = cv2.imread('images/inputs/test.png')
img2 = img.copy();
rect =  [0,0,100,100];
masl = 0;
mask2 = 0;
rect = 0

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
        global img, img2
        f = request.files['file']
        print(type(f.filename))
        filename = 'images/inputs/'+secure_filename(f.filename) # gives secure filename
        f.save(filename)
        print(filename)
        im = cv2.imread(filename)
        img = im.copy();
        img2 = im.copy();
        # # ret, thresh = cv2.threshold(im, 1, 255, 0)
        # cv2.namedWindow('input')
        # cv2.imshow('input', im)
        # k = cv2.waitKey(0) % 256
        cv2.imwrite('images/outputs/test_img.png', im)
        # return render_template("main.html", image_name=f.filename)
        # return send_file('images/outputs/test_img.png', mimetype='image/png')
        return render_template('main.html')


@app.route('/uploadmask', methods=['GET', 'POST'])
def upload_mask():
    if request.method == 'POST':
        global img, img2, mask
        f = request.files['canvasImage']
        print(type(f.filename))
        filename = 'images/inputs/'+secure_filename(f.filename)+'.png'  # gives secure filename
        f.save(filename)
        print(filename)
        im = cv2.imread(filename, -1)
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        newmask = im[:, :, 2]
        mask[newmask == 0] = 0
        mask[newmask == 255] = 1
        print(mask)
        # # ret, thresh = cv2.threshold(im, 1, 255, 0)
        # cv2.namedWindow('input')
        # cv2.imshow('input', im)
        # k = cv2.waitKey(0) % 256
        cv2.imwrite('images/outputs/test_img.png', im)
        # return render_template("main.html", image_name=f.filename)
        # return send_file('images/outputs/test_img.png', mimetype='image/png')
        data = {'img': im, 'site': 'stackoverflow.com'}
        return render_template('main.html', data=data)


@app.route('/segment', methods=['GET', 'POST'])
def segment():
    global img, img2, mask, mask2, rect
    bgdmodel = np.zeros((1, 65), np.float64)
    fgdmodel = np.zeros((1, 65), np.float64)
    cv2.grabCut(img2, mask, rect, bgdmodel, fgdmodel, 1, cv2.GC_INIT_WITH_RECT)
    cv2.grabCut(img2, mask, rect, bgdmodel, fgdmodel, 1, cv2.GC_INIT_WITH_MASK)
    mask2 = np.where((mask == 1) + (mask == 3), 255, 0).astype('uint8')
    output = cv2.bitwise_and(img2, img2, mask=mask2)
    cv2.imwrite('images/outputs/output.png', output)
    return send_file('images/outputs/output.png', mimetype='image/png')


@app.route('/main')
def get_post_javascript_data():
    data = [1, 'foo']
    return render_template('main.html', data=json.dumps(data))

if __name__ == '__main__':
    app.run(debug=True)