from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = "d6cebd5c93ba466b860a0949bc13b331"
app.config['TEMP_FOLDER'] = "static/pictures/temp"