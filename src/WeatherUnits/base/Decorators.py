from src.WeatherUnits.config import config

__all__ = ['NamedType', 'NamedSubType', 'UnitSystem', 'BaseUnit', 'Synonym', 'Tiny', 'Small', 'Medium', 'Large', 'Huge']

properties = config['UnitProperties']


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
	cls._size = 'tiny'
	return strToDict(properties['Tiny'], cls)


def Small(cls):
	cls._size = 'small'
	return strToDict(properties['Small'], cls)


def Medium(cls):
	cls._size = 'medium'
	return strToDict(properties['Medium'], cls)


def Large(cls):
	cls._size = 'large'
	return strToDict(properties['Large'], cls)


def Huge(cls):
	cls._size = 'huge'
	return strToDict(properties['Huge'], cls)


def Synonym(cls):
	cls.__name__ = cls.__mro__[1].__name__
	return cls
