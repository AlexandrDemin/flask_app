import dbProvider as db
from flask import Flask, url_for, render_template, abort

app = Flask(__name__)

@app.route('/')
def mainPage():
    return render_template('mainPage.html',
        siteName = db.getText("header", "siteName"),
        motto = db.getText("header", "motto"),
        title = db.getText("mainPage", "title"),
        description = db.getText("mainPage", "description"),
        keywords = db.getText("mainPage", "keywords"),
        h1 = db.getText("mainPage", "h1"),
        copyright = db.getText("footer", "copyright"),
        services = db.getServices(),
        regions = db.getRegionsTree())

@app.route('/<serviceNameTranslit>')
def ServiceNoRegion(serviceNameTranslit):
    service = db.getServiceByNameTranslit(serviceNameTranslit)
    if service == None:
        abort(404)
    return render_template('serviceNoRegion.html',
        siteName = db.getText("header", "siteName"),
        motto = db.getText("header", "motto"),
        title = service['name'],
        description = service['name'],
        keywords = service['name'],
        h1 = service['name'],
        copyright = db.getText("footer", "copyright"),
        regions = db.getRegionsTree())

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html',
        siteName = db.getText("header", "siteName"),
        motto = db.getText("header", "motto"),
        title = "Страница не найдена",
        copyright = db.getText("footer", "copyright")),404