import logging

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

	def stringToBool(item: string):
		return item.lower() in ('yes', 'true', 't', '1')

	def parseString(item):
		key, value = item.split('=')
		expectedTypes = {'max': int, 'precision': int, 'unitSpacer': stringToBool, 'shorten': stringToBool, 'thousandsSeparator': stringToBool}
		return f'_{key}', expectedTypes[key](value)

	conf = [parseString(a) for a in [(y.strip(' ')) for y in string.split(',')]]
	for item in conf:
		setattr(cls, item[0], item[1])

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
	noConfig = True
	try:
		cls = strToDict(properties[cls._type.__name__.lower()], cls)
		noConfig = False
	except KeyError:
		pass
	except AttributeError:
		logging.warning(f'{cls.__name__.lower()} has no type defined')
	try:
		cls = strToDict(properties[cls.__name__], cls)
		noConfig = False
	except KeyError:
		pass
	finally:
		if noConfig:
			logging.warning(f'Config for {cls._type.__name__} was not found')
		return cls
