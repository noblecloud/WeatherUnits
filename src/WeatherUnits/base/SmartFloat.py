import logging

from math import nan

from ..config import config as _config

log = logging.getLogger('SmartFloat')

properties = _config['UnitProperties']

__all__ = ['SmartFloat']


class Meta(type):
	def __new__(cls, name, bases, dct):

		def toCamelCase(string, titleCase: bool = False) -> str:
			string = (string.lower() if string.isupper() else string)
			for char in ['-', ' ', '.', '_']:
				string.replace(char, '')
			return string[0].upper() if titleCase else string[0].lower() + string[1:]

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

		def PropertiesFromConfig(cls):
			possibleNames = [cls.__name__.lower(), toCamelCase(cls.__name__), cls.__name__]
			if hasattr(cls, '_type') and cls._type is not None and not isinstance(cls._type, str):
				possibleTypes = [cls._type.__name__.lower(), toCamelCase(cls._type.__name__), cls._type.__name__]
				for classType in possibleTypes:
					try:
						cls = strToDict(properties[classType], cls)
						break
					except KeyError:
						pass
				else:
					log.debug(f'{cls.__name__} has no type defined')

			for name in possibleNames:
				try:
					cls = strToDict(properties[name], cls)
					break
				except KeyError:
					pass
			return cls

		x = super().__new__(cls, name, bases, dct)
		x = PropertiesFromConfig(x)
		return x


class SmartFloat(float, metaclass=Meta):
	_config = _config
	_precision: int = 1
	_max: int = 3
	_unit: str = ''
	_suffix: str = ''
	_decorator: str = ''
	_unitSpacer = True
	_title: str = ''
	_scale = 1
	_showUnit: bool = True
	_shorten: bool = True
	_thousandsSeparator = False
	_combineUnitAndSuffix: bool = False
	_subscriptionKey: str = None
	_sizeHint: str = None

	@classmethod
	def noneToNan(cls, value):
		if not isinstance(value, float):
			try:
				value = float(value)
			except ValueError:
				value = nan
			except TypeError:
				value = nan
		return value

	def __new__(cls, value):
		value = cls.noneToNan(value)
		return float.__new__(cls, value)

	def __init__(self, value):
		# if isinstance(value, SmartFloat):
		# 	self._title = value._title if value._title is not None else self._title
		value = self.noneToNan(value)
		self._scale, decimal = list(len(n) for n in str(float(value)).split('.'))
		self._precision = min(self._precision, decimal)
		float.__init__(value)

	def _string(self, hintString: bool = False, forceUnit: bool = False) -> str:
		if self._shorten:
			c, valueFloat = 0, float(self)
			numberLength = len(str(int(valueFloat)))
			while numberLength > 3 and numberLength > self._max:
				c += 1
				valueFloat /= 1000
				numberLength = len(str(int(valueFloat)))
			suffix = ['', 'k', 'm', 'B'][c]
		else:
			valueFloat = self
			c = False
			suffix = ''

		# TODO: Allow for precision to be overridden if number is scaled.  (10,110 becomes 10.11k instead of 10.1k)
		newScale, decimal = list(len(n) for n in str(round(valueFloat, self._precision)).strip('0').split('.'))

		# Max amount of precision that can be displayed while keeping string under max length
		intAllowedPrecision = max(0, self._max - newScale)

		# Allow at least on level of precision if
		# Removed 1 if not decimal and c else decimal
		decimal = min(self._precision, intAllowedPrecision)
		formatStr = f"{{:{',' if self._thousandsSeparator else ''}.{decimal}f}}"
		valueString = formatStr.format(10 ** max(newScale - 1, 0) if hintString else valueFloat)
		needsSpacer = self._unitSpacer or (forceUnit and self._unitSpacer) or c
		spacer = " " if needsSpacer else ""
		unit = self._unit if self._showUnit or forceUnit else ''
		return f'{valueString}{suffix}{self._decorator}{spacer}{unit}'

	def __str__(self):
		return self._string()

	def __bool__(self):
		return super().__bool__() or bool(self.unit)

	@property
	def valueUnset(self) -> bool:
		return self == nan

	@property
	def withUnit(self):
		return self._string(forceUnit=True)

	@property
	def withoutUnit(self):
		return self._string(forceUnit=False)

	@property
	def unit(self) -> str:
		return self._unit

	@property
	def unitArray(self):
		return [self._unit]

	@property
	def suffix(self):
		return self._suffix

	@property
	def int(self):
		return int(self)

	@property
	def name(self):
		return self.__class__.__name__

	@property
	def title(self):
		return self._title if self._title else self.name

	@title.setter
	def title(self, value):
		self._title = value

	@property
	def subscriptionKey(self) -> str:
		if self._subscriptionKey:
			return self._subscriptionKey
		else:
			t = self.title
			t = t.lower() if t.isupper() else t
			t = t.replace(' ', '')
			return f"{t[0].lower()}{t[1:]}"

	@subscriptionKey.setter
	def subscriptionKey(self, value: str):
		self._subscriptionKey = value

	@property
	def showUnit(self):
		return self._showUnit

	@showUnit.setter
	def showUnit(self, value):
		self._showUnit = value

	@property
	def sizeHint(self) -> int:
		# length = len(string) - (0.5 * (string.count('.') + string.count(','))
		return self._string(hintString=True).replace('1', '0') if self._sizeHint is None else self._sizeHint

	@property
	def decorator(self):
		self._decorator
