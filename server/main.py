
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

def process_image(input_image):
    image = ImageOps.exif_transpose(input_image)

    save_date = find_next_date()

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
            "date": i.split(".")[0],
            "complete": i.split(".")[1] == "bmp"
        }

        returnData.append(img)
        
    returnData = sorted(returnData, key=lambda x: x["date"])
    
    return returnData

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
    today = str(datetime.datetime.now().date())
    if not os.path.exists("static/images/" + today + ".bmp"):
        print("No")
        return "0"

    # check if current time is +- 30 mins of 3:00 AM
    now = datetime.datetime.now()
    t_wakeup = int(os.environ.get("WAKEUP_TIME", "3"))

    if now.hour == t_wakeup and now.minute < 30:
        return "1"
    elif now.hour == t_wakeup-1 and now.minute > 30:
        return "1"

    return "0"

if __name__ == '__main__':
    app.run(debug=True, port=8000, host="0.0.0.0")
