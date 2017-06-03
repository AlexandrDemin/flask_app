# flask_app

A simple website made with python flask.

First install requirements.

$ pip install -r requirements.txt

Then run flask server

1. $ export FLASK_APP=main.py
2. $ export FLASK_DEBUG=1
3. $ flask run

The site will be on localhost:5000

If you need to change styles, don't change main.css, change scss in the foundation folder. To compile css, run gulp from the foundation folder:

1. $ cd foundation
2. $ gulp
