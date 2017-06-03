import dbProvider as db
from flask import Flask, url_for, render_template, abort

app = Flask(__name__)

app.config['SERVER_NAME'] = 'otkachkaseptika.ru:5000'

# No subdomain

@app.route('/')
def MainPage():
    return render_template('mainPage.html',
        siteName = db.getText("header", "siteName"),
        motto = db.getText("header", "motto"),
        mainPhone = db.getDefaultPhone()['phoneString'],
        mainPhoneMeta = "Звонок бесплатный по России",
        title = db.getText("mainPage", "title"),
        description = db.getText("mainPage", "description"),
        keywords = db.getText("mainPage", "keywords"),
        h1 = db.getText("mainPage", "h1"),
        copyright = db.getText("footer", "copyright"),
        services = db.getServices(),
        regions = db.getRegionsTree()
        )

@app.route('/<service>')
def ServiceNoRegion(service):
    service = db.getServiceByNameTranslit(service)
    if service == None:
        abort(404)
    return render_template('serviceNoRegion.html',
        siteName = db.getText("header", "siteName"),
        motto = db.getText("header", "motto"),
        mainPhone = db.getDefaultPhone()['phoneString'],
        mainPhoneMeta = "Звонок бесплатный по России",
        title = service['name'],
        description = service['name'],
        keywords = service['name'],
        h1 = service['name'],
        copyright = db.getText("footer", "copyright"),
        regions = db.getRegionsTree()
        )

# With subdomain

@app.route('/', subdomain="<subdomain>")
def RegionNoService(subdomain):
    region = db.getRegionBySubdomain(subdomain)
    if region == None:
        abort(404)
    return render_template('regionNoService.html',
        siteName = db.getText("header", "siteName"),
        motto = db.getText("header", "motto"),
        mainPhone = db.getDefaultPhone()['phoneString'],
        mainPhoneMeta = "Звонок бесплатный по России",
        title = db.getText("mainPage", "title"),
        description = db.getText("mainPage", "description"),
        keywords = db.getText("mainPage", "keywords"),
        h1 = db.getText("mainPage", "h1"),
        copyright = db.getText("footer", "copyright"),
        services = db.getServices(),
        regions = db.getRegionsTree()
        )

@app.route('/<serviceVRegione>', subdomain="<subdomain>")
def OrderService(serviceVRegione, subdomain):
    mainRegion = db.getRegionBySubdomain(subdomain)
    if mainRegion == None:
        abort(404)
    serviceAndRegion = serviceVRegione.split("-v-")
    service = db.getServiceByNameTranslit(serviceAndRegion[0])
    if service == None:
        abort(404)
    if len(serviceAndRegion) > 1:
        region = db.getRegionByDativeTranslitAndMainRegion(serviceAndRegion[1], mainRegion['id'])
        if region == None:
            abort(404)
    else:
        return render_template('mainRegionService.html',
            siteName = db.getText("header", "siteName"),
            motto = db.getText("header", "motto"),
            mainPhone = db.getDefaultPhone()['phoneString'],
            mainPhoneMeta = "Звонок бесплатный по России",
            title = service['name'],
            description = service['name'],
            keywords = service['name'],
            h1 = service['name'],
            copyright = db.getText("footer", "copyright"),
            regions = db.getRegionsTree()
            )
    return render_template('orderService.html',
        siteName = db.getText("header", "siteName"),
        motto = db.getText("header", "motto"),
        mainPhone = db.getDefaultPhone()['phoneString'],
        mainPhoneMeta = "Звонок бесплатный по России",
        title = service['name'],
        description = service['name'],
        keywords = service['name'],
        h1 = service['name'],
        copyright = db.getText("footer", "copyright"),
        regions = db.getRegionsTree()
        )

@app.route('/<service>/<path:regions>', subdomain="<subdomain>")
def RegionsService(service, regions, subdomain):
    mainRegion = db.getRegionBySubdomain(subdomain)
    if mainRegion == None:
        abort(404)
    service = db.getServiceByNameTranslit(service)
    if service == None:
        abort(404)
    regions = regions.split('/')
    parentId = mainRegion['id']
    for regionName in regions:
        region = db.getRegionByNameTranslitAndParentId(regionName, parentId)
        if region == None:
            abort(404)
        parentId = region['id']
    return render_template('mainRegionService.html',
        siteName = db.getText("header", "siteName"),
        motto = db.getText("header", "motto"),
        mainPhone = db.getDefaultPhone()['phoneString'],
        mainPhoneMeta = "Звонок бесплатный по России",
        title = service['name'],
        description = service['name'],
        keywords = service['name'],
        h1 = service['name'],
        copyright = db.getText("footer", "copyright"),
        regions = db.getRegionsTree()
        )

# Error handling

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html',
        siteName = db.getText("header", "siteName"),
        motto = db.getText("header", "motto"),
        title = "Страница не найдена",
        copyright = db.getText("footer", "copyright")),404

