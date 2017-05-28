from flask import Flask, url_for, render_template
from flask_assets import Environment, Bundle

app = Flask(__name__)

@app.route('/')
def hello_world():
    cssUrl = url_for('static', filename='css/app.css')
    return render_template('main.html', cssUrl = cssUrl)