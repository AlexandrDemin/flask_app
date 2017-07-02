import dbProvider as db
import json
from operator import itemgetter
from flask import Flask, url_for, render_template, abort, make_response, redirect

app = Flask(__name__)

# serverName = 'govnosos.pro:5000'
serverName = 'otkachkaseptika.ru'

def getStaticPath(relativePath):
    return '/static/' + relativePath
    # return url_for('static', filename=relativePath)

app.config['SERVER_NAME'] = serverName

# Helpers

@app.context_processor
def utility_processor():
    def getLinkForRegionService(regionId = None, serviceId = None, order = False):
        if regionId == None:
            if serviceId == None:
                return url_for("RegionNoService", subdomain = 'www')
            else:
                service = db.getServiceById(serviceId)
                return url_for("RegionService", routeString = service['nameTranslit'], subdomain = 'www')
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
    def getLen(array):
        return len(array)
    return dict(getLinkForRegionService=getLinkForRegionService, getLen=getLen)

def getPathForRegionId(regionId):
    path = ""
    parents = db.getRegionParentsSorted(regionId)
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

def getServiceImgUrl(service, region):
    imgNumber = db.getServiceRandomImgNumber(service, region['id'])
    if imgNumber == None:
        service = db.getServiceById(5)
        imgNumber = db.getServiceRandomImgNumber(service, region['id'])
    return getStaticPath('img/' + service['nameTranslit'] + '/' + service['nameTranslit'] + '-' + str(imgNumber) + '.jpg')

def replaceDataInContent(content, region, service):
    result = []
    for block in content:
        imgUrl = getServiceImgUrl(service, region)
        replaced = block.replace('{N}', region['dativeCaseName']).replace('{imgSrc}', imgUrl).replace('{imgAlt}', service['name'] + ' в ' + region['dativeCaseName'])
        result.append(replaced)
    return result

# Redirects from no subdomains to www

@app.route('/')
def Redirect():
    return redirect("http://www." + serverName + "/", code=301)

@app.route('/<path:routeString>')
def RedirectWithPath(routeString):
    return redirect("http://www." + serverName + "/" + routeString, code=301)

# With subdomain

@app.route('/', subdomain="<subdomain>")
def RegionNoService(subdomain):
    region = db.getRegionBySubdomain(subdomain)
    if region == None:
        return abort(404)
    return render_template('selectServiceForRegion.html',
        siteName = db.getText("header", "siteName"),
        motto = db.getText("header", "motto").format(region['dativeCaseName']),
        mainPhone = db.getPhoneByRegionId(region['id'])['phoneString'],
        mainPhoneMeta = db.getText("phoneDescription", "other"),
        title = db.getText("regionNoService", "title").format(region['dativeCaseName']),
        description = db.getText("regionNoService", "description").format(region['dativeCaseName']),
        keywords = db.getText("regionNoService", "keywords"),
        h1 = db.getText("regionNoService", "h1").format(region['dativeCaseName']),
        copyright = db.getText("footer", "copyright"),
        services = db.getServices(),
        region = region,
        parentRegions = db.getRegionParentsSorted(region['id']),
        regions = db.getRegionsTree(parentIds=[region['id']])
        )

@app.route('/<path:routeString>', subdomain="<subdomain>")
def RegionService(routeString, subdomain):
    mainRegion = db.getRegionBySubdomain(subdomain)
    if mainRegion == None:
        return abort(404)
    serviceAndRegion = routeString.split("/")
    service = db.getServiceByNameTranslit(serviceAndRegion[0])
    if service != None:
        regionPath = routeString.replace(service['nameTranslit'] + "/", "")
        region = getRegionByPathAndParentId(path=regionPath, parentId=mainRegion['id'])
        dativeRegionName = mainRegion['dativeCaseName']
        parentIds=[mainRegion['id']]
        parentRegions = db.getRegionParentsSorted(mainRegion['id'])
        regionOrMainRegion = mainRegion
        if region != None:
            dativeRegionName = region['dativeCaseName']
            parentIds=[region['id']]
            parentRegions = db.getRegionParentsSorted(region['id'])
            regionOrMainRegion = region
        return render_template('selectRegionForService.html',
            siteName = db.getText("header", "siteName"),
            motto = db.getText("header", "motto").format(mainRegion['dativeCaseName']),
            mainPhone = db.getPhoneByRegionId(mainRegion['id'])['phoneString'],
            mainPhoneMeta = db.getText("phoneDescription", "other"),
            title = db.getText("mainRegionService", "title").format(service['name'], dativeRegionName),
            description = db.getText("mainRegionService", "description").format(service['name'], dativeRegionName, service['description']),
            keywords = db.getText("mainRegionService", "keywords").format(service['name'], dativeRegionName),
            h1 = db.getText("mainRegionService", "h1").format(service['name'], dativeRegionName),
            service = service,
            parentRegions = parentRegions,
            copyright = db.getText("footer", "copyright"),
            regions = db.getRegionsTree(parentIds, 2),
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
                motto = db.getText("header", "motto").format(mainRegion['dativeCaseName']),
                mainPhone = db.getPhoneByRegionId(region['id'])['phoneString'],
                mainPhoneMeta = db.getText("phoneDescription", "other"),
                title = db.getText("regionNoService", "title").format(region['dativeCaseName']),
                description = db.getText("regionNoService", "description").format(region['dativeCaseName']),
                keywords = db.getText("regionNoService", "keywords"),
                h1 = db.getText("regionNoService", "h1").format(region['dativeCaseName']),
                copyright = db.getText("footer", "copyright"),
                services = db.getServices(),
                region = region,
                parentRegions = db.getRegionParentsSorted(region['id']),
                regions = db.getRegionsTree()
                )
        if len(serviceAndRegion) > 1:
            region = db.getRegionByDativeTranslitAndMainRegion(serviceAndRegion[1], mainRegion['id'])
            if region == None:
                abort(404)
            services = db.getServices()[:]
            services.remove(service)
            content = db.getRandomizedTexts("orderService", str(service['id']), randomSeed = region['id'])
            content = replaceDataInContent(content, region, service)
            return render_template('orderService.html',
                siteName = db.getText("header", "siteName"),
                motto = db.getText("header", "motto").format(mainRegion['dativeCaseName']),
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
                parentRegions = db.getRegionParentsSorted(region['id']),
                regions = db.getRegionsTree(parentIds = [mainRegion['id']], depth = 2),
                otherServicesHeader = "Другие услуги в {}".format(region['dativeCaseName']),
                contentBlocks = content
                )

#robots.txt
@app.route('/robots.txt', subdomain="<subdomain>")
def Robots(subdomain):
    mainRegion = db.getRegionBySubdomain(subdomain)
    if mainRegion == None:
        abort(404)
    robots = 'User-agent: *\nAllow: /\nHost: www.otkachkaseptika.ru\nsitemap: http://www.otkachkaseptika.ru/sitemap.xml'
    response= make_response(robots)
    response.headers["Content-Type"] = "text/plain"
    return response

#sitemap.xml

sitemapCount = 50
lastMod = '2017-06-27'

@app.route('/sitemap.xml', subdomain="<subdomain>")
def SitemapIndex(subdomain):
    mainRegion = db.getRegionBySubdomain(subdomain)
    if mainRegion == None:
        abort(404)
    sitemapIndex = render_template('sitemapindex.xml',
        urlRoot='http://' + subdomain + '.' + serverName,
        sitemapCount = sitemapCount,
        lastMod = lastMod)
    response= make_response(sitemapIndex)
    response.headers["Content-Type"] = "application/xml"
    return response

@app.route('/sitemap<index>.xml', subdomain="<subdomain>")
def Sitemap(index, subdomain):
    mainRegion = db.getRegionBySubdomain(subdomain)
    if mainRegion == None:
        abort(404)
    index = int(index)
    if index > sitemapCount:
        abort(404)
    services = db.getServices()
    regions = db.getAllChildrenRegionIds(mainRegion['id'])
    start = (index - 1) * len(regions)/sitemapCount
    if start < 0:
        abort(404)
    if start > len(regions):
        start = len(regions)
    end = index * len(regions)/sitemapCount
    if end > len(regions):
        end = len(regions)
    start = int(start)
    end = int(end)
    sitemapTemplate = 'sitemap1.xml'
    if index == 1:
        sitemapTemplate = 'sitemap.xml'
    sitemapXml = render_template(sitemapTemplate,
        urlRoot='http://' + subdomain + '.' + serverName,
        services = services,
        regions = regions[start:end],
        lastMod = lastMod)
    response= make_response(sitemapXml)
    response.headers["Content-Type"] = "application/xml"
    return response

#verification

@app.route('/google450d69197dedc081.html', subdomain="<subdomain>")
def GoogleVerification(subdomain):
    mainRegion = db.getRegionBySubdomain(subdomain)
    if mainRegion == None:
        abort(404)
    return 'google-site-verification: google450d69197dedc081.html'


# Error handling

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html',
        siteName = db.getText("header", "siteName"),
        motto = db.getText("header", "motto"),
        title = "Страница не найдена",
        copyright = db.getText("footer", "copyright")),404

