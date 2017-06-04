# flask_app

A simple website made with python flask.

## Getting started

First clone the repo and cd to the repository folder

1. `$ git clone https://github.com/AlexandrDemin/flask_app.git`
2. `$ cd flask_app`

Then install the requirements.

`$ pip install -r requirements.txt`

Then run flask server

1. `$ export FLASK_APP=main.py`
2. `$ export FLASK_DEBUG=1`
3. `$ flask run`

The site will be on `localhost:5000`

## Testing subdomains locally

To test URLs with subdomains locally

1. set SERVER_NAME config in `main.py` to your domain name `app.config['SERVER_NAME'] = 'yordomain.com:5000'`
2. add in [hosts file](https://www.howtogeek.com/howto/27350/beginner-geek-how-to-edit-your-hosts-file/){:target="_blank"}
```
127.0.0.1 govnosos.pro
127.0.0.1 subdomain1.yordomain.com
...
127.0.0.1 subdomainN.yordomain.com
```
Where `subdomain1` ... `subdomainN` are the subdomains from `configs/subdomains.json`

## Editing styles

If you want to change styles, don't change main.css. Edit scss files in the foundation folder. To compile css, run gulp from the foundation folder:

1. `$ cd foundation`
2. `$ gulp`
