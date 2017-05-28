import dbProvider as db
from flask import Flask, url_for, render_template

app = Flask(__name__)

@app.route('/')
def mainPage():
    title = "title"
    description = "desc"
    keywords = "key"
    h1 = db.getText("mainPageHeader")
    siteTitle = "SiteTitle"
    regions = db.getRegionsByLevel([1,2])
    return render_template('mainPage.html',
        siteTitle = siteTitle,
        title=title,
        description=description,
        keywords=keywords,
        h1=h1,
        regions=regions)