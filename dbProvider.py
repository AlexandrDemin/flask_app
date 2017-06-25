import json
import random
from operator import itemgetter

absolutePath = '/home/noidea91/flask_app/'
# absolutePath = ''

# Texts

def getTextsCache():
	json_data = open(absolutePath + "configs/texts.json").read()
	texts = json.loads(json_data)
	return texts

_textsCache = getTextsCache()

def getText(action, stringName=""):
	if stringName == "":
		return _textsCache[action]
	else:
		return _textsCache[action].get(stringName)

def getServicesCache():
	json_data = open(absolutePath + "configs/services.json").read()
	texts = json.loads(json_data)
	return texts

# Services

_servicesCache = getServicesCache()

def getServices():
	return _servicesCache

def getServiceByNameTranslit(serviceNameTranslit):
	for service in _servicesCache:
		if service['nameTranslit'] == serviceNameTranslit:
			return service
	return None

def getServiceById(serviceId):
	for service in _servicesCache:
		if service['id'] == serviceId:
			return service
	return None

# Regions

def getRegionsCache():
	json_data = open(absolutePath + "configs/regions.json").read()
	regions = json.loads(json_data)
	for region in regions:
		region['childrenIds'] = []
		for potentialChild in regions:
			if region['id'] == potentialChild['parentId']:
				region['childrenIds'].append(potentialChild['id'])
		region['hasChildren'] = False if len(region['childrenIds']) == 0 else True
	return regions

_regionsCache = getRegionsCache()

def getAllChildrenRegionIds(parentId):
	parents = [parentId]
	allChildren = []
	while len(parents) > 0:
		regions = getRegionIdsByParentIds(parents)
		allChildren.extend(regions)
		parents = regions
	return allChildren

def isChildrenRegion(regionId, mainRegionId):
	parents = [mainRegionId]
	while len(parents) > 0:
		regions = getRegionIdsByParentIds(parents)
		if regionId in regions:
			return True
		parents = regions
	return False

def getRegionByDativeTranslitAndMainRegion(dativeTranslit, mainRegionId):
	for region in _regionsCache:
		if region['dativeTranslit'] == dativeTranslit:
			if isChildrenRegion(region['id'], mainRegionId):
				return region
	return None

def getRegionByNameTranslitAndParentId(nameTranslit, parentId):
	for region in _regionsCache:
		if region["parentId"] == parentId and region["nameTranslit"] == nameTranslit:
			return region
	return None

def getRegionIdsByParentIds(parentIds):
	result = []
	for regionId in parentIds:
		region = getRegionById(regionId)
		result.extend(region['childrenIds'])
	return result

def getRegionsByParentIds(parentIds):
	result = []
	for regionId in parentIds:
		region = getRegionById(regionId)
		for childId in region['childrenIds']:
			child = getRegionById(childId)
			result.append(getRegionById(child['id']))
	return result

def getRegionParents(regionId):
	result = []
	region = getRegionById(regionId)
	while True:
		parent = getRegionById(region['parentId'])
		if parent == None:
			return result
		result.append(parent)
		region = parent

def getRegionParentsSorted(regionId, deleteFirst = True):
	parentsUnsorted = getRegionParents(regionId)
	parents = sorted(parentsUnsorted, key=itemgetter('id'))
	if len(parents) > 0 and deleteFirst:
		parents.pop(0)
	return parents

def getRegionsByLevel(levels):
	result = []
	for region in _regionsCache:
		if region["level"] in levels:
			result.append(region)
	return result

def getRegionsTree(parentIds=None, depth=1):
	result = []
	regions = getRegionsByLevel([1]) if parentIds == None else getRegionsByParentIds(parentIds);
	if depth > 0:
		for region in regions:
			regionId = region['id']
			if depth > 1:
				region['children'] = getRegionsTree(parentIds = [regionId], depth = depth - 1)
			else:
				region['children'] = getRegionsByParentIds([regionId])
			result.append(region)
	return result

def getRegionById(id):
	for region in _regionsCache:
		if region["id"] == id:
			return region
	return None

# Subdomains

def getSubdomainsCache():
	json_data = open(absolutePath + "configs/subdomains.json").read()
	subdomains = json.loads(json_data)
	for subdomain in subdomains:
		subdomain['allChildrenRegionIds'] = getAllChildrenRegionIds(subdomain['regionId'])
	return subdomains

_subdomainsCache = getSubdomainsCache()

def getRegionBySubdomain(subdomainString):
	for subdomain in _subdomainsCache:
		if subdomain['subdomain'] == subdomainString:
			return getRegionById(subdomain['regionId'])
	return None

def getSubdomainByMainRegionId(regionId):
	for subdomain in _subdomainsCache:
		if subdomain['regionId'] == regionId:
			return subdomain['subdomain']
	return None

def getSubdomainByRegionId(regionId):
	for subdomain in _subdomainsCache:
		if regionId in subdomain['allChildrenRegionIds']:
			return subdomain['subdomain']
	return None

# Phones

def getPhonesCache():
	json_data = open(absolutePath + "configs/phones.json").read()
	phones = json.loads(json_data)
	return phones

_phonesCache = getPhonesCache()

def getDefaultPhone():
	# Номер 8800 с RegionId 0
	return _phonesCache["0"]

def getPhoneByRegionId(regionId):
	return _phonesCache.get(str(regionId), getDefaultPhone())

# Cars

def getCarsCache():
	json_data = open(absolutePath + "configs/cars.json").read()
	texts = json.loads(json_data)
	return texts

_carsCache = getCarsCache()

def getRandomCars(count):
	tempCars = _carsCache[:]
	result = []
	for i in range(1, count):
		random.seed()
		rnd = random.randrange(len(tempCars))
		result.append(tempCars[rnd])
		tempCars.pop(rnd)
	return result
