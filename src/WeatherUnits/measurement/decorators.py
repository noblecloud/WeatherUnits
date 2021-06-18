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
	return cls


def NoSpaceBeforeUnit(cls):
	cls._unitSpacer = False
	return cls


def strToDict(string, cls) -> dict[str:int]:
	conf = {a[0]: int(a[1]) for a in [(y.strip(' ').split('=')) for y in string.split(',')]}
	for key, value in conf.items():
		setattr(cls, f'_{key}', value)
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


def PropertiesFromConfig(cls):
	try:
		cls = strToDict(properties[cls.__name__], cls)
	except Exception as e:
		print(e)
	return cls
