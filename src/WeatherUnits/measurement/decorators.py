import logging

from utils import toCamelCase
from .. import config as _config

properties = _config['UnitProperties']


def NamedType(cls):
	cls._type = cls
	return cls


def NamedSubType(cls):
	cls._subType = cls
	return cls


def UnitSystem(cls):
	cls._unitSystem = cls
	return cls


def BaseUnit(cls):
	cls._unitSystem._baseUnit = cls
	cls._Scale._baseUnit = cls._Scale.Base
	return cls


def NoSpaceBeforeUnit(cls):
	cls._unitSpacer = False
	return cls


def strToDict(string: str, cls: type) -> type:

	def parseString(item: str):
		key, value = item.split('=')
		# expectedTypes = {'max': int, 'precision': int, 'unitSpacer': stringToBool, 'shorten': stringToBool, 'thousandsSeparator': stringToBool, 'cardinal': stringToBool, 'degrees': stringToBool}
		if value.isnumeric():
			value = float(value)
			if value.is_integer():
				value = int(value)
		if value == 'True':
			value = True
		elif value == 'False':
			value = False
		return f'_{key}', value

	conf = [parseString(a) for a in [(y.strip(' ')) for y in string.split(',')]]
	for item in conf:
		setattr(cls, *item)

	return cls


def Tiny(cls):
	return strToDict(properties['tiny'], cls)


def Small(cls):
	return strToDict(properties['small'], cls)


def Medium(cls):
	return strToDict(properties['medium'], cls)


def Large(cls):
	return strToDict(properties['large'], cls)


def Huge(cls):
	return strToDict(properties['huge'], cls)


def Integer(cls):
	cls._precision = -1
	return cls


class NoConfigSpecifiedForUnit(Exception):
	pass


def PropertiesFromConfig(cls):
	possibleNames = [cls.__name__.lower(), toCamelCase(cls.__name__), cls.__name__]

	if hasattr(cls, '_type') and cls._type is not None:
		possibleTypes = [cls._type.__name__.lower(), toCamelCase(cls._type.__name__), cls._type.__name__]
		for classType in possibleTypes:
			try:
				cls = strToDict(properties[classType], cls)
				break
			except KeyError:
				pass
		else:
			logging.warning(f'{cls.__name__} has no type defined')
	for name in possibleNames:
		try:
			cls = strToDict(properties[name], cls)
			break
		except KeyError:
			pass
	return cls
