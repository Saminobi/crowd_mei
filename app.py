import os

from pdf2image import convert_from_path
from flask import Flask, request, render_template, flash, url_for
from flask_cors import CORS
from pathlib import Path
from pymongo import MongoClient
from werkzeug.utils import secure_filename, redirect
from shutil import copyfile

connection = MongoClient()
db = connection.crowd_mei

composition_col = db["compositions"]
score_col = db["scores"]


app = Flask(__name__, static_url_path='', static_folder='static')
app.secret_key = "secret key"

UPLOAD_FOLDER = Path('static/data/pdf').absolute()
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy   dog'
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def add_composition(composer_name, composition_name, instrument):
    path = "static/data/composers/" + composer_name + "/" + composition_name + "/" + instrument
    if not os.path.exists(path):
        os.makedirs(path)
        os.makedirs(path + "/pdf")
        os.makedirs(path + "/jpg")
        os.makedirs(path + "/png")
        os.makedirs(path + "/mei")

    composition_col.insert_one({"composition_name": composition_name, "composer_name": composer_name, "instrument": instrument})
    add_page(composition_name+".pdf", path)


def add_page(filename, path):
    file_path = "static/data/pdf/"+filename
    empty_path = "static/data/mei/empty.mei"
    pages = convert_from_path(file_path, 500)
    length = len(pages)
    # db.scores.find({"file_path": file_path}).next()["_id"]
    count = 1
    page_list = []
    for page in pages:
        pdf_path = path + "/pdf/page" + str(count) + ".pdf"
        jpg_path = path + "/jpg/page" + str(count) + ".jpg"
        png_path = path + "/png/page" + str(count) + ".png"
        mei_path = path + "/mei/page" + str(count) + ".mei"
        copyfile(empty_path, mei_path)
        page.save(pdf_path)
        page.save(jpg_path, 'JPEG')
        page_list.append({"pdf_path": pdf_path, "png_path": png_path,"jpg_path": jpg_path, "mei_path": mei_path, "is_checked": False})
        count += 1
    doc_body = {"user_added": "", "file_path": file_path, "no_pages": length, "pages": pagelist}
    score_col.insert_one(doc_body)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        composer_name = request.form["composer name"]
        composition_name = request.form["composition name"]
        instrument = request.form["instrument"]
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(composition_name+".pdf")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # composer_col.insert_one({"composer_name": composer_name})
            print("calling add composition")
            add_composition(composer_name, composition_name, instrument)
    return render_template('index.html')


@app.route('/mei_page.html')
def load_mei_page():
    if db.pages.count() != 0:
        unchecked = db.pages.find({"is_checked": False})
        record = unchecked.next()["jpg_path"]

        with open('templates/mei_page.html', 'r') as file:
            data = file.readlines()

        new_record = record[6:]
        data[10] = "<img src=\"" + new_record + "\">\n"

        # and write everything back
        with open('templates/mei_page.html', 'w') as file:
            file.writelines(data)
    return render_template('mei_page.html')


@app.route('/store', methods=['GET', 'POST'])
def store_mei_changes():
    print("store_mei_changes")
    print(request.get_data().decode('utf-8'))
    return 'hello'


if __name__ == '__main__':
    app.run()