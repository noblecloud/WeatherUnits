import logging
from typing import Union

log = logging.getLogger(__name__)


def loadUnitLocalization(measurement, config):
	possibleNames = [measurement.__class__.__name__.lower(), toCamelCase(measurement.__class__.__name__), measurement.__class__.__name__]

	if hasattr(measurement.__class__, '_type') and measurement.__class__._type is not None:
		possibleTypes = [measurement.__class__._type.__name__.lower(), toCamelCase(measurement.__class__._type.__name__), measurement.__class__._type.__name__]
		for classType in possibleTypes:
			try:
				return config['LocalUnits'][classType]
			except KeyError:
				pass
		else:
			log.warning(f'{measurement._type.__name__} has no type defined')


def toCamelCase(string, titleCase: bool = False) -> str:
	string = (string.lower() if string.isupper() else string)
	for char in ['-', ' ', '.', '_']:
		string.replace(char, '')
	return string[0].upper() if titleCase else string[0].lower() + string[1:]


'''https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python'''


def levenshtein(seq1, seq2):
	oneago = None
	thisrow = range(1, len(seq2) + 1) + [0]
	for x in range(len(seq1)):
		twoago, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
		for y in range(len(seq2)):
			delcost = oneago[y] + 1
			addcost = thisrow[y - 1] + 1
			subcost = oneago[y - 1] + (seq1[x] != seq2[y])
			thisrow[y] = min(delcost, addcost, subcost)
	return thisrow[len(seq2) - 1]


def convertString(value: str) -> Union[int, float, str, bool]:
	if value is None:
		return value
	if value.isnumeric():
		value = float(value)
		if value.is_integer():
			value = int(value)
		return value
	if value == 'True':
		value = True
	elif value == 'False':
		value = False
	return value


def parseString(item: str):
	key, value = item.split('=')
	value = convertString(value)
	return f'_{key}', value


def strToDict(string: str, cls: type) -> type:
	conf = [parseString(a) for a in [(y.strip(' ')) for y in string.split(',')]]
	for item in conf:
		setattr(cls, *item)
	return cls


def PropertiesFromConfig(cls, config):
	possibleNames = [cls.__name__.lower(), cls._unit, toCamelCase(cls.__name__), cls.__name__]
	if hasattr(cls, '_type') and cls._type is not None and not isinstance(cls._type, str):
		possibleTypes = [cls._type.__name__.lower(), toCamelCase(cls._type.__name__), cls._type.__name__]
		for classType in possibleTypes:
			try:
				cls = strToDict(config.unitProperties[classType], cls)
				config.configuredUnits[cls.__name__] = cls
				break
			except KeyError:
				pass
		else:
			log.debug(f'{cls.__name__} has no type defined')

	for name in possibleNames:
		try:
			cls = strToDict(config.unitProperties[name], cls)
			config.configuredUnits[name] = cls
			break
		except KeyError:
			pass
	return cls
