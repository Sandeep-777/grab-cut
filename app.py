from flask import Flask, render_template, request, send_file, jsonify, url_for
from werkzeug import secure_filename
import Image
import numpy as np
import cv2

img = cv2.imread('static/images/inputs/test.png')
img2 = img.copy()
rect = [0, 0, 100, 100]
masl = 0
mask2 = 0
rect_or_mask = 0

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


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        global img, img2, mask, rect
        f = request.files['canvasImage']
        filename = 'static/images/inputs/' + secure_filename(f.filename)  # gives secure filename
        f.save(filename)
        im = cv2.imread(filename)
        img = im.copy()
        img2 = im.copy()
        height, width = img.shape[:2]
        rect = (0, 0, width, height)
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        cv2.imwrite('static/images/outputs/test_img.png', im)
        # return render_template("main.html", image_name=f.filename)
        return send_file('static/images/outputs/test_img.png', mimetype='image/png')
        # return render_template('main.html')


@app.route('/uploadrect', methods=['GET', 'POST'])
def upload_rect():
    if request.method == 'POST':
        global rect, rect_or_mask
        rect_or_mask = 1
        # print request.data
        # print request.get_json()
        f = request.json
        rect = (f['x_0'], f['y_0'], f['width'], f['height'])
        return jsonify(rect)


@app.route('/uploadmask', methods=['GET', 'POST'])
def upload_mask():
    if request.method == 'POST':
        global img, img2, mask
        f = request.files['canvasImage']
        filename = 'static/images/inputs/' + secure_filename(f.filename) + '.png'  # gives secure filename
        f.save(filename)
        im = cv2.imread(filename, -1)
        newmask = im[:, :, 2]
        newmaskfg = im[:, :, 1]
        mask[newmaskfg == 255] = 1
        mask[newmask == 255] = 0
        cv2.imwrite('static/images/outputs/test_img.png', im)
        return 'success'
        # return render_template('main.html', data=data)


@app.route('/segment', methods=['GET', 'POST'])
def segment():
    global img, img2, mask, mask2, rect, rect_or_mask
    output = np.zeros(img.shape, np.uint8)
    bgdmodel = np.zeros((1, 65), np.float64)
    fgdmodel = np.zeros((1, 65), np.float64)
    print mask
    if rect_or_mask == 1:
        cv2.grabCut(img2, mask, rect, bgdmodel, fgdmodel, 1, cv2.GC_INIT_WITH_RECT)
    else:
        cv2.grabCut(img2, mask, rect, bgdmodel, fgdmodel, 1, cv2.GC_INIT_WITH_MASK)
    print mask
    mask2 = np.where((mask == 1) + (mask == 3), 255, 0).astype('uint8')
    output = cv2.bitwise_and(img2, img2, mask=mask2)
    # cv2.imwrite('images/outputs/output.png', output)
    b_channel, g_channel, r_channel = cv2.split(output)
    alpha = mask2
    # converting channel to rgb from bgr for PIL and auto cropping
    output2 = cv2.merge((r_channel, g_channel, b_channel, mask2))
    image = Image.fromarray(output2)
    imageSize = image.size
    imageBox = image.getbbox()
    cropped = image.crop(imageBox)
    cropped.save('static/images/outputs/output.png')
    rect_or_mask = 0;

    return url_for('static', filename='images/outputs/output.png')
    # return send_file('images/outputs/output.png', mimetype='image/png')


@app.route('/')
def index():
    return render_template('main.html')


@app.route('/main')
def main():
    return render_template('main.html')


if __name__ == '__main__':
    app.run(debug=True)
