
from flask import Flask, request, redirect, url_for, send_file
from PIL import Image, ImageOps
import PIL
import os
import re
import dithering
import datetime
from io import BytesIO
import datetime
import multiprocessing
import random
import uuid

app = Flask(__name__)

uuid_regex = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE)
date_regex = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", re.IGNORECASE)

# static files
app.static_folder = 'static'
app.static_url_path = '/static'

if not os.path.exists("static/images"):
    os.mkdir("static/images")

color_table = [
    dithering.Color(  0,   0,   0),
    dithering.Color(255, 255, 255),
    dithering.Color(255,   0,   0),
    dithering.Color(  0, 255,   0),  
    dithering.Color(  0,   0, 255),
    dithering.Color(255, 255,   0),
    dithering.Color(255, 128,   0)
]

def serve_pil_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/thumbnail/<img_id>')
def send_thumbnail(img_id):
    i = Image.open("static/images/" + img_id + ".bmp")
    return serve_pil_image(i)

def process_image(input_image):
    image = ImageOps.exif_transpose(input_image)

    save_date = str(uuid.uuid4())

    # create an empty file with the date as the name and .tmp as the extension
    open("static/images/" + save_date + ".tmp", "w").close()


    # crop to a 600:448 aspect ratio from center
    if image.width / image.height > 600/448:
        image = image.crop((int(image.width/2 - image.height * 600/448/2), 0, int(image.width/2 + image.height * 600/448/2), image.height))
    else:
        image = image.crop((0, int(image.height/2 - image.width * 448/600/2), image.width, int(image.height/2 + image.width * 448/600/2)))

    image = image.resize((600, 448))

    processed = dithering.process(image, color_table)

    if not os.path.exists("static/images"):
        os.mkdir("static/images")

    processed.save("static/images/" + save_date + ".bmp")

    # remove the .tmp file
    os.remove("static/images/" + save_date + ".tmp")

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']

        try:
            image = Image.open(f)
        except PIL.UnidentifiedImageError:
            return redirect(url_for('index'))

        multiprocessing.Process(target=process_image, args=(image,)).start()
    
    return redirect(url_for('index'))

@app.route("/api/images")
def get_images():
    returnData = []

    # get all images from images folder
    for i in os.listdir("static/images"):
        img = {
            "uuid": i.split(".")[0],
            "complete": i.split(".")[1] == "bmp" # is processing complete?
        }

        returnData.append(img)
            
    return returnData

@app.route("/api/today")
def get_today():
    # get random image for today
    imgs = get_images()

    # the frame pulls the image 3 times because of memory constraints
    # make sure the image is the same random image for all 3 pulls
    random.seed(f"{datetime.datetime.now().year}_{datetime.datetime.now().month}_{datetime.datetime.now().day}")

    today = random.choice([i["uuid"] for i in imgs if i["complete"]])

    return app.send_static_file("images/" + today + ".bmp")
            

@app.route("/api/images/<img_id>", methods=["PATCH", "DELETE"])
def get_image(img_id):
    if (not uuid_regex.match(img_id) and not date_regex.match(img_id)):
        return "Invalid picture ID", 400

    elif request.method == "DELETE":
        os.remove("static/images/" + img_id + ".bmp")

    return "OK"

@app.route("/api/wakeup")
def wakeup():
    now = datetime.datetime.now()

    # get tomorrow at 3am
    t_wakeup = now.replace(day=now.day+1, hour=3, minute=0, second=0, microsecond=0)

    # get the difference in seconds
    delta_t = t_wakeup - now

    return str(int(delta_t.total_seconds()))

@app.route("/api/preflight")
def preflight():
    # verify we have an image
    if len(get_images()) == 0:
        return "0"

    return "1"

if __name__ == '__main__':
    app.run(debug=True, port=8000, host="0.0.0.0")
