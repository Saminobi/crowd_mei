from flask import request
from flask import Flask
from flask_cors import CORS, cross_origin

app = Flask(__name__)

app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy   dog'
app.config['CORS_HEADERS'] = 'Content-Type'

cors = CORS(app, resources={r"/": {"origins": "http://127.0.0.1:8000"}})


@app.route('/', methods=['GET', 'POST'])
def store_mei_changes():
    print(request.get_data().decode('utf-8'))
    return 'Backend Server. Work in Progress...'

if __name__ == '__main__':
    app.run()
