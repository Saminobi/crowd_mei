import os

from pdf2image import convert_from_path
from flask import Flask, request, render_template, flash
from flask_cors import CORS
from pathlib import Path
from pymongo import MongoClient
from werkzeug.utils import secure_filename, redirect
from shutil import copyfile

# connect to the database "crowd_mei"
connection = MongoClient()
db = connection.crowd_mei

# create the collections "compositions" and "scores"
composition_col = db["compositions"]
score_col = db["scores"]

app = Flask(__name__, static_url_path='', static_folder='static')
app.secret_key = "secret key"

# JH: You have the UPLOAD_FOLDER, why not use it in code?
UPLOAD_FOLDER = Path('static/data/pdf').absolute()
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy   dog'
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app)


# method to find the allowed files
# JH: If your method performs a True/False check, it is a good habit to name it with an is_
# prefix.
# JH: Also, it does not really check whether the *file* is allowed, it only checks the filename.
# But because it is *used* to check whether the file itself is allowed, it should not be called
# is_filename_allowed(); this should be reflected in the docstring.
def is_file_allowed(filename):
    """Method to check whether the given file name suggests the file is acceptable.

    :param filename: String with file name.
    :return: True/False
    """
    # JH: It is better to not put conditions directly into return statements.
    #     You never know when you might want to add another check, for instance.
    is_allowed = ('.' in filename) and \
                 (filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS)
    return is_allowed


# method to add compositions to the right directories
# TODO: JH: What if multiple compositions have the same name? If it is user input, any assumption
# TODO: JH: you make is practically guaranteed to fail at some point. Furthermore, while the combination
# TODO: JH: of composer_name, composition_name and instrument does to some extent guarantee a unique
# TODO: JH: identification of a composition, it does not guarantee a unique PDF file! You can have
# TODO: JH: multiple different PDFs of the same composition (manuscript and printed edition, for instance).
# TODO: JH: See corresponding issue.
def add_composition(composer_name, composition_name, instrument):
    """Adds composition pages to the filesystem on the server and inserts
    the appropriate records into the database.

    Assumes the score PDF is already uploaded. TODO: This is not the best design choice.

    The path is ``static/data/composers/COMPOSER_NAME/COMPOSITION_NAME/INSTRUMENT``.

    :param composer_name:
    :param composition_name:
    :param instrument:
    """
    # TODO: JH: What exactly is the instrument? There can be many instruments, there can be
    # TODO: JH: instrumental parts, etc. I'm not sure what you mean here; requires clarification.
    # TODO: JH: What happens when people put names there with characters that cannot be in a path?
    # TODO: JH: The files referred to from the database should be in media/, not static/.
    # JH: static/ is generally meant for content that users will not modify -- hence also the name.
    #
    # JH: This should be a separate function, generate_score_media_path(). Also, do the Path() thing!
    path = "static/data/composers/" + composer_name + "/" + composition_name + "/" + instrument
    # create the directories
    if not os.path.exists(path):
        os.makedirs(path)
        os.makedirs(path + "/pdf")
        os.makedirs(path + "/jpg")
        os.makedirs(path + "/png")
        os.makedirs(path + "/mei")

    # add records to "composition" collection in the database
    composition_col.insert_one({"composition_name": composition_name,
                                "composer_name": composer_name,
                                "instrument": instrument})
    # JH: Formatting. It's easier to get an overview of the fields like this.
    add_score(composition_name + ".pdf", path)  # JH: Use spaces in algebraic expressions.
    # TODO: JH: Bug alert! Don't forget you sanitized your filename when you save the score PDF in upload_score().


# for each file create the pages
# convert them to the "pdf", "jpg", "png" and "mei formats"
# and then add to the database
# JH: This should not be called add_page() -- it does not add a page, it adds the *score*, page by page
# JH: Also, the argument names can be made self-explanatory: "filename" and "path" is not clear enough.
# JH: I would also re-think what arguments this method should get.
def add_score(score_pdf_filename, target_path):
    """Given a PDF file, will split it into pages, convert pages into images,
    save the resulting files including empty MEI, and record this information
    in the scores collection of the database.

    :param score_pdf_filename: The name (NOT the path) of the PDF file. Assumed
        to be a file in the ``UPLOAD_FOLDER``.
    :param target_path: The path into which the score media files should be saved.
    """
    # JH: Here would be a good time to use the app.config['UPLOAD_FOLDER'] variable
    file_path = "static/data/pdf/" + score_pdf_filename
    # TODO: JH: empty.mei should go into a folder that is more obviously not a part of the media files.
    # TODO: JH: Also, this should be a variable like UPLOAD_PATH.
    # JH: Eventually, all these SOMETHING_PATH variables should be split off in some data_config file
    # JH: from which they get loaded into the app_config.
    # JH: It's highly probable that you will want to eventually use them in different modules.
    #
    # JH: It's good practice to check file existence assumptions.
    if not os.path.isfile(file_path):
        raise OSError("Source pdf file {} does not exist!", file_path)

    mei_empty_template_path = "static/data/mei/empty.mei"   # JH: Again -- clearer naming.

    pages = convert_from_path(file_path, 500)
    page_count = len(pages)  # JH: clearer naming. You'll get the hang of this easily.
    # db.scores.find({"file_path": file_path}).next()["_id"]
    page_number = 1  # JH: see above. It's straightforward: just call things what they really are & mean.
    page_list = []
    for page in pages:
        pdf_path = target_path + "/pdf/page" + str(page_number) + ".pdf"
        jpg_path = target_path + "/jpg/page" + str(page_number) + ".jpg"
        png_path = target_path + "/png/page" + str(page_number) + ".png"
        mei_path = target_path + "/mei/page" + str(page_number) + ".mei"
        copyfile(mei_empty_template_path, mei_path)
        page.save(pdf_path)
        page.save(jpg_path, 'JPEG')
        page_list.append({"pdf_path": pdf_path,
                          "png_path": png_path,
                          "jpg_path": jpg_path,
                          "mei_path": mei_path,
                          "is_checked": False})
        page_number += 1

    doc_body = {"user_added": "",
                "file_path": file_path,
                "no_pages": page_count,
                "pages": page_list}
    score_col.insert_one(doc_body)


# method to upload files
# JH: The method doesn't just upload files, it adds a score. A score is more than just
# JH: the file -- it is also the metadata, the database record(s), the page files, etc.
@app.route('/', methods=['GET', 'POST'])
def upload_score():
    """Handles PDF score upload by a user.
    """
    if request.method == 'POST':
        if 'file' not in request.files:     # JH: Call it 'score_pdf', maybe?
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        composer_name = request.form["composer name"]
        composition_name = request.form["composition name"]
        instrument = request.form["instrument"]
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # if file is allowed, add the file to the its given path
        if file and is_file_allowed(file.filename):
            filename = secure_filename(composition_name + ".pdf")  # JH: Well done on the filename sanitization.
            # TODO: JH: Bug alert! You save the uploaded PDF with a sanitized filename, but in add_composition,
            # TODO: JH: it is not sanitized.
            # TODO: JH: This bug is also a symptom of a suboptimal design decision: the path to the score
            # TODO: JH: should only be created in one place in the code, so that errors like this don't
            # TODO: JH: have a chance to happen. Ideally, there should be a function that generates
            # TODO: JH: the score filename (I would say it is better to use the whole path) which you
            # TODO: JH: call with all the relevant arguments when you need to find the score PDF file.
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # composer_col.insert_one({"composer_name": composer_name})
            add_composition(composer_name, composition_name, instrument)
        else:    # JH: And if it isn't...?
            flash('File missing or invalid.')
            return redirect(request.url)

    return render_template('index.html')


# method which loads the mei page
@app.route('/mei_page.html')
def load_mei_page():
    """Renders the Verovio editor view for some page.
    """
    if db.pages.count() != 0:
        # JH: Heads up: this will need to be refactored into a separate choose_page() function.
        unchecked = db.pages.find({"is_checked": False})
        record = unchecked.next()["jpg_path"]

        with open('templates/mei_page.html', 'r') as file:
            data = file.readlines()

        new_record = record[6:]
        # TODO: JH: ???? This is definitely bad practice, especially without a comment.
        # TODO: JH: I have no idea what it means and it's pretty sure to cause a bug
        # TODO: JH: as soon as path conventions change, and they *always* change at some point.

        data[10] = "<img src=\"" + new_record + "\">\n"
        # TODO: JH: Same here. No magic numbers, please! You can do:
        # TODO: JH:      IMAGE_URL_FIELD_INDEX = 10
        # TODO: JH:      data[IMAGE_URL_FIELD_INDEX] = "<img src... >\n"
        # TODO: JH: or something better, but it needs to be self-explanatory what this number is.

        # and write everything back
        # TODO: JH: IMPORTANT: There is a correct way to pass variables to a template,
        # TODO: JH: so that you don't have to modify the template HTML code directly.
        # TODO: JH: This is something you should never do: the template is called a template
        # TODO: JH: for a reason! Otherwise you will go crazy because you will break your
        # TODO: JH: own website. Especially because the jpg_path contains, IIRC, something
        # TODO: JH: you asked the users to input!
        with open('templates/mei_page.html', 'w') as file:
            file.writelines(data)

    return render_template('mei_page.html')


# method to store the mei changes
@app.route('/store', methods=['GET', 'POST'])
def store_mei_changes():
    print("store_mei_changes")
    print(request.get_data().decode('utf-8'))
    return 'hello'


# main method to run the application
if __name__ == '__main__':
    app.run()
