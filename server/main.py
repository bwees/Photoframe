
from flask import Flask, request, redirect, url_for, send_file
from PIL import Image, ImageOps
import PIL
from pillow_heif import register_heif_opener
import os
import re
import dithering
import datetime
from io import BytesIO

register_heif_opener()
app = Flask(__name__)

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

# get all fo the dates in the static/images folder
# find the first hole in the dates
# use datetime
def find_next_date():
    dates = []
    for i in os.listdir("static/images"):
        if i.split(".")[1] == "bmp":
            dates.append(i.split(".")[0])
    
    dates.sort()
    dates = [datetime.datetime.strptime(date, "%Y-%m-%d") for date in dates]
    dates = [date.strftime("%Y-%m-%d") for date in dates]

    for i in range(len(dates)):
        if dates[i] != str(datetime.datetime.now().date() + datetime.timedelta(i)):
            return str(datetime.datetime.now().date() + datetime.timedelta(i))
    
    return str(datetime.datetime.now().date() + datetime.timedelta(len(dates)))
    
    

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/thumbnail/<img_id>')
def send_thumbnail(img_id):
    i = Image.open("static/images/" + img_id + ".bmp")
    return serve_pil_image(i)

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']

        try:
            image = Image.open(f)
        except PIL.UnidentifiedImageError:
            return redirect(url_for('index'))

        image = ImageOps.exif_transpose(image)

        # crop to a 600:448 aspect ratio from center
        if image.width / image.height > 600/448:
            image = image.crop((int(image.width/2 - image.height * 600/448/2), 0, int(image.width/2 + image.height * 600/448/2), image.height))
        else:
            image = image.crop((0, int(image.height/2 - image.width * 448/600/2), image.width, int(image.height/2 + image.width * 448/600/2)))

        image = image.resize((600, 448))

        processed = dithering.process(image, color_table)


        if not os.path.exists("static/images"):
            os.mkdir("static/images")

        processed.save("static/images/" + find_next_date() + ".bmp")
    
    return redirect(url_for('index'))

@app.route("/api/images")
def get_images():

    images = []
    # get all images from images folder
    for i in os.listdir("static/images"):
        if i.split(".")[1] == "bmp":
            images.append(i.split(".")[0])

    images.sort()
    
    return images

@app.route("/api/today")
def get_today():
    # get image for today
    today = str(datetime.datetime.now().date())
    if not os.path.exists("static/images/" + today + ".bmp"):
        return "No image for today"
    
    return app.send_static_file("images/" + today + ".bmp")
      
            

@app.route("/api/images/<img_id>", methods=["PATCH", "DELETE"])
def get_image(img_id):
    if (not date_regex.match(img_id)):
        return "Invalid date format", 400

    if request.method == "PATCH":
        os.rename("static/images/" + img_id + ".bmp", "static/images/" + request.json["date"] + ".bmp")
    elif request.method == "DELETE":
        os.remove("static/images/" + img_id + ".bmp")

    return "OK"

if __name__ == '__main__':
    app.run(debug=True, port=8000, host="0.0.0.0")
