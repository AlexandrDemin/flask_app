import dbProvider as db
from flask import Flask, url_for, render_template, abort

app = Flask(__name__)

app.config['SERVER_NAME'] = 'otkachkaseptika.ru:5000'

@app.context_processor
def utility_processor():
    def getLinkForRegionService(regionId = None, serviceId = None, order = False):
        if regionId == None:
            if serviceId == None:
                return url_for("MainPage")
            else:
                service = db.getServiceById(serviceId)
                return url_for("ServiceNoRegion", service = service['nameTranslit'])
        else:
            region = db.getRegionById(regionId)
            subdomain = db.getSubdomainByMainRegionId(regionId)
            if subdomain == None:
                isMainRegion = False
                subdomain = db.getSubdomainByRegionId(regionId)
            else:
                isMainRegion = True
            if serviceId == None:
                if isMainRegion:
                    return url_for("RegionNoService", subdomain = subdomain)
                else:
                    return url_for("RegionService", routeString = getPathForRegionId(regionId), subdomain = subdomain)
            else:
                service = db.getServiceById(serviceId)
                if isMainRegion:
                    return url_for("RegionNoService", routeString = service['nameTranslit'], subdomain = subdomain)
                else:
                    if order:
                        routeString = service['nameTranslit'] + "-v-" + region['dativeTranslit']
                        return url_for("RegionService", routeString = routeString, subdomain = subdomain)
                    else:
                        routeString = service['nameTranslit'] + "/" + getPathForRegionId(regionId)
                        return url_for("RegionService", routeString = routeString, subdomain = subdomain)
    return dict(getLinkForRegionService=getLinkForRegionService)

def getPathForRegionId(regionId):
    path = ""
    parents = db.getRegionParents(regionId)
    parents.pop(0)
    for parent in parents:
        path += "/" + parent["nameTranslit"]
    region = db.getRegionById(regionId)
    path += "/" + region["nameTranslit"]
    return path

def getRegionByPathAndParentId(path, parentId):
    regions = path.split('/')
    for regionName in regions:
        region = db.getRegionByNameTranslitAndParentId(regionName, parentId)
        if region == None:
            return None
        parentId = region['id']
    return region

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

@app.route('/<path:routeString>', subdomain="<subdomain>")
def RegionService(routeString, subdomain):
    mainRegion = db.getRegionBySubdomain(subdomain)
    if mainRegion == None:
        abort(404)
    serviceAndRegion = routeString.split("/")
    service = db.getServiceByNameTranslit(serviceAndRegion[0])
    if service != None:
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
    else:
        serviceAndRegion = routeString.split("-v-")
        service = db.getServiceByNameTranslit(serviceAndRegion[0])
        if service == None:
            region = getRegionByPathAndParentId(serviceAndRegion[0], mainRegion['id'])
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
        if len(serviceAndRegion) > 1:
            region = db.getRegionByDativeTranslitAndMainRegion(serviceAndRegion[1], mainRegion['id'])
            if region == None:
                abort(404)
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

# Error handling

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html',
        siteName = db.getText("header", "siteName"),
        motto = db.getText("header", "motto"),
        title = "Страница не найдена",
        copyright = db.getText("footer", "copyright")),404

