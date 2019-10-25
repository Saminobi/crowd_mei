import os

from pdf2image import convert_from_path
from flask import Flask, request, render_template, flash, url_for
from flask_cors import CORS
from pathlib import Path
from pymongo import MongoClient
from werkzeug.utils import secure_filename, redirect

connection = MongoClient()
db = connection.crowd_mei

file_col = db["files"]
page_col = db["pages"]

app = Flask(__name__)
app.secret_key = "secret key"

UPLOAD_FOLDER = Path('data/pdf').absolute()
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy   dog'
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources={r"/": {"origins": "http://127.0.0.1:5000"}})

if db.pages.count() != 0:
    unchecked = db.pages.find({"is_checked": False})
    record = unchecked.next()["jpg_path"]

    with open('templates/index.html', 'r') as file:
        data = file.readlines()

    data[10] = "<img src= ../" + record + "/>\n"

    # and write everything back
    with open('templates/index.html', 'w') as file:
        file.writelines(data)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def add_page(filename):
    filepath = "data/pdf/" + filename
    pages = convert_from_path(filepath, 500)
    length = len(pages)
    file_col.insert_one(
        {"file_path": filepath,
         "no_pages": length})
    fileid = db.files.find({"file_path": filepath}).next()["_id"]
    count = 1
    for page in pages:
        jpg_path = "data/jpg/" + filename + "_" + str(count) + ".jpg"
        page.save(jpg_path, 'JPEG')
        page_col.insert_one(
            {"file_id": fileid, "page_id": count, "png_path": "",
             "jpg_path": jpg_path,
             "mei_path": "", "is_checked": False})
        count += 1


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            add_page(filename)
    return render_template('index.html')

# @app.route('/', methods=['GET', 'POST'])
# def store_mei_changes():
#     if request.method == "GET":
#         name = request.form["name"]
#         return name + " Hello"
#     return "not working"


if __name__ == '__main__':
    app.run()
