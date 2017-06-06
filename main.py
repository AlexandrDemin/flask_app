import dbProvider as db
from flask import Flask, url_for, render_template, abort

app = Flask(__name__)

app.config['SERVER_NAME'] = 'govnosos.pro:5000'

# Helpers

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
                    return url_for("RegionService", routeString = service['nameTranslit'], subdomain = subdomain)
                else:
                    if not (region['hasChildren']):
                        order = True
                    if order:
                        routeString = service['nameTranslit'] + "-v-" + region['dativeTranslit']
                        return url_for("RegionService", routeString = routeString, subdomain = subdomain)
                    else:
                        routeString = service['nameTranslit'] + getPathForRegionId(regionId)
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
        mainPhoneMeta = db.getText("phoneDescription", "8800"),
        title = db.getText("mainPage", "title"),
        description = db.getText("mainPage", "description"),
        keywords = db.getText("mainPage", "keywords"),
        h1 = db.getText("mainPage", "h1"),
        copyright = db.getText("footer", "copyright"),
        services = db.getServices(),
        regions = db.getRegionsTree(),
        region = None
        )

@app.route('/<service>')
def ServiceNoRegion(service):
    service = db.getServiceByNameTranslit(service)
    if service == None:
        abort(404)
    return render_template('selectRegionForService.html',
        siteName = db.getText("header", "siteName"),
        motto = db.getText("header", "motto"),
        mainPhone = db.getDefaultPhone()['phoneString'],
        mainPhoneMeta = db.getText("phoneDescription", "8800"),
        title = service['name'],
        description = service['name'],
        keywords = service['name'],
        h1 = service['name'],
        service = service,
        parentRegions = None,
        copyright = db.getText("footer", "copyright"),
        regions = db.getRegionsTree(),
        region = None
        )

# With subdomain

@app.route('/', subdomain="<subdomain>")
def RegionNoService(subdomain):
    region = db.getRegionBySubdomain(subdomain)
    if region == None:
        abort(404)
    return render_template('selectServiceForRegion.html',
        siteName = db.getText("header", "siteName"),
        motto = db.getText("header", "motto"),
        mainPhone = db.getPhoneByRegionId(region['id'])['phoneString'],
        mainPhoneMeta = db.getText("phoneDescription", "other"),
        title = db.getText("regionNoService", "title").format(region['dativeCaseName']),
        description = db.getText("regionNoService", "description").format(region['dativeCaseName']),
        keywords = db.getText("regionNoService", "keywords"),
        h1 = db.getText("regionNoService", "h1").format(region['dativeCaseName']),
        copyright = db.getText("footer", "copyright"),
        services = db.getServices(),
        region = region,
        parentRegions = db.getRegionParents(region['id']),
        regions = db.getRegionsTree(parentIds=[region['id']])
        )

@app.route('/<path:routeString>', subdomain="<subdomain>")
def RegionService(routeString, subdomain):
    mainRegion = db.getRegionBySubdomain(subdomain)
    if mainRegion == None:
        abort(404)
    serviceAndRegion = routeString.split("/")
    service = db.getServiceByNameTranslit(serviceAndRegion[0])
    if service != None:
        regionPath = routeString.replace(service['nameTranslit'] + "/", "")
        region = getRegionByPathAndParentId(path=regionPath, parentId=mainRegion['id'])
        dativeRegionName = mainRegion['dativeCaseName']
        parentIds=[mainRegion['id']]
        parentRegions = db.getRegionParents(mainRegion['id'])
        regionOrMainRegion = mainRegion
        if region != None:
            dativeRegionName = region['dativeCaseName']
            parentIds=[region['id']]
            parentRegions = db.getRegionParents(region['id'])
            regionOrMainRegion = region
        return render_template('selectRegionForService.html',
            siteName = db.getText("header", "siteName"),
            motto = db.getText("header", "motto"),
            mainPhone = db.getPhoneByRegionId(mainRegion['id'])['phoneString'],
            mainPhoneMeta = db.getText("phoneDescription", "other"),
            title = db.getText("mainRegionService", "title").format(service['name'], dativeRegionName),
            description = db.getText("mainRegionService", "description").format(service['name'], dativeRegionName, service['description']),
            keywords = db.getText("mainRegionService", "keywords").format(service['name'], dativeRegionName),
            h1 = db.getText("mainRegionService", "h1").format(service['name'], dativeRegionName),
            service = service,
            parentRegions = parentRegions,
            copyright = db.getText("footer", "copyright"),
            regions = db.getRegionsTree(parentIds=parentIds),
            region = regionOrMainRegion
            )
    else:
        serviceAndRegion = routeString.split("-v-")
        service = db.getServiceByNameTranslit(serviceAndRegion[0])
        if service == None:
            region = getRegionByPathAndParentId(serviceAndRegion[0], mainRegion['id'])
            if region == None:
                abort(404)
            return render_template('selectServiceForRegion.html',
                siteName = db.getText("header", "siteName"),
                motto = db.getText("header", "motto"),
                mainPhone = db.getPhoneByRegionId(region['id'])['phoneString'],
                mainPhoneMeta = db.getText("phoneDescription", "other"),
                title = db.getText("regionNoService", "title").format(region['dativeCaseName']),
                description = db.getText("regionNoService", "description").format(region['dativeCaseName']),
                keywords = db.getText("regionNoService", "keywords"),
                h1 = db.getText("regionNoService", "h1").format(region['dativeCaseName']),
                copyright = db.getText("footer", "copyright"),
                services = db.getServices(),
                region = region,
                parentRegions = db.getRegionParents(region['id']),
                regions = db.getRegionsTree()
                )
        if len(serviceAndRegion) > 1:
            region = db.getRegionByDativeTranslitAndMainRegion(serviceAndRegion[1], mainRegion['id'])
            if region == None:
                abort(404)
            services = db.getServices()[:]
            services.remove(db.getServiceById(1))
            return render_template('orderService.html',
                siteName = db.getText("header", "siteName"),
                motto = db.getText("header", "motto"),
                mainPhone = db.getPhoneByRegionId(region['id'])['phoneString'],
                mainPhoneLink = db.getPhoneByRegionId(region['id'])['phoneNormal'],
                mainPhoneMeta = db.getText("phoneDescription", "other"),
                title = db.getText("orderService", "title").format(service['name'], region['dativeCaseName']),
                description = db.getText("orderService", "description").format(service['name'], region['dativeCaseName']),
                keywords = db.getText("orderService", "keywords"),
                h1 = db.getText("orderService", "h1").format(service['name'], region['dativeCaseName']),
                copyright = db.getText("footer", "copyright"),
                services = services,
                region = region,
                service = service,
                parentRegions = db.getRegionParents(region['id']),
                regions = db.getRegionsTree(),
                otherServicesHeader = "Другие услуги в {}".format(region['dativeCaseName']),
                contentBlocks = db.getText("orderService", str(service['id']))
                )

# Error handling

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html',
        siteName = db.getText("header", "siteName"),
        motto = db.getText("header", "motto"),
        title = "Страница не найдена",
        copyright = db.getText("footer", "copyright")),404

