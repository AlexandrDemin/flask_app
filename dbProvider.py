import json
import random

def getTextsCache():
	json_data = open("configs/texts.json").read()
	texts = json.loads(json_data)
	return texts

_textsCache = getTextsCache()

def getText(action, stringName=""):
	if stringName == "":
		return _textsCache[action]
	else:
		return _textsCache[action].get(stringName)

def getServicesCache():
	json_data = open("configs/services.json").read()
	texts = json.loads(json_data)
	return texts

_servicesCache = getServicesCache()

def getServices():
	return _servicesCache

def getServiceByOrderNameTranslit(nameTranslitOrder):
	for service in _servicesCache:
		if service['nameTranslitOrder'] == nameTranslitOrder:
			return service
	return None

def getServiceByNameTranslit(serviceNameTranslit):
	for service in _servicesCache:
		if service['nameTranslit'] == serviceNameTranslit:
			return service
	return None

def getRegionsCache():
	json_data = open("configs/regions.json").read()
	regions = json.loads(json_data)
	return regions

_regionsCache = getRegionsCache()

def getRegionByDativeTranslit(dativeTranslit):
	for region in _regionsCache:
		if region.['dativeTranslit'] == dativeTranslit:
			return region
	return None

def getRegionByNameTranslitAndParentId(nameTranslit, parentId):
	for region in _regionsCache:
		if region["parentId"] == parentId and region["nameTranslit"] == nameTranslit:
			return region
	return None

def getRegionBySubdomain(subdomain):
	result = []
	for region in _regionsCache:
		if region.get("subdomain", "") == subdomain:
			return region
	return None

def getRegionsByParentIds(parentIds):
	result = []
	for region in _regionsCache:
		if region["parentId"] in parentIds:
			result.append(region)
	return result

def getRegionsByLevel(levels):
	result = []
	for region in _regionsCache:
		if region["level"] in levels:
			result.append(region)
	return result

def getRegionsTree(parents=None, depth=1):
	result = []
	regions = getRegionsByLevel([1]) if parents == None else getRegionsByParentIds(parents);
	if depth > 0:
		for region in regions:
			regionId = region['id']
			if depth - 1 > 0:
				region['children'] = getRegionsTree(parents = [regionId], depth = depth - 1)
			else:
				region['children'] = getRegionsByParentIds([regionId])
			result.append(region)
	return result

def getPhonesCache():
	json_data = open("configs/phones.json").read()
	texts = json.loads(json_data)
	return texts

_phonesCache = getPhonesCache()

def getDefaultPhone():
	# Номер 8800 с RegionId 0
	return _phonesCache["0"]

def getPhoneByRegionId(regionId):
	return _phonesCache.get(str(regionId), getDefaultPhone())

def getCarsCache():
	json_data = open("configs/cars.json").read()
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
