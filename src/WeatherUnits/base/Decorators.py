

__all__ = ['UnitType', 'Synonym', 'Tiny', 'Small', 'Medium', 'Large', 'Huge']


def UnitType(*args, **kwargs):
	if args:
		cls = args[0]
		cls._type = cls
		return cls
	else:
		def wrapper(cls):
			cls._type = cls
			return cls

		return wrapper


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
	return cls


def Small(cls):
	cls._size = 'small'
	return cls


def Medium(cls):
	cls._size = 'medium'
	return cls


def Large(cls):
	cls._size = 'large'
	return cls


def Huge(cls):
	cls._size = 'huge'
	return cls


def Synonym(cls):
	cls.__name__ = cls.__mro__[1].__name__
	return cls
