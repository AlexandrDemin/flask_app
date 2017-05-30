import json

def getTextsCache():
	json_data = open("texts.json").read()
	texts = json.loads(json_data)
	return texts

_textsCache = getTextsCache()

def getText(key):
	return _textsCache[key]

def getServicesCache():
	json_data = open("services.json").read()
	texts = json.loads(json_data)
	return texts

_servicesCache = getServicesCache()

def getServices():
	return _servicesCache

def getRegionsCache():
	json_data = open("regions.json").read()
	regions = json.loads(json_data)
	return regions

_regionsCache = getRegionsCache()

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