import logging
from typing import Optional

from . import config as _config
from . import errors as _errors, utils as _utils


class SmartFloat(float):
	_config = _config
	_precision: int = 1
	_max = 3

	_unitType: str = 'f'
	_unit: str = ''
	_suffix: str = ''
	_decorator: str = ''
	_unitFormat: str = '{decorated} {unit}'
	_format: str = '{value}{decorator}'
	_title: str = ''

	def __new__(cls, value):
		return float.__new__(cls, value)

	def __init__(self, value):
		decimal = list(len(n) for n in str(value).split('.'))[-1]
		self._precision = min(self._precision, decimal)
		if isinstance(value, SmartFloat):
			self._title = value._title
		float.__init__(value)

	def __str__(self) -> str:
		string = self.formatString.format(self)
		return '{value}{decorator}'.format(value=string, decorator=self._decorator)

	def __bool__(self):
		return self or self._unit

	def strip(self):
		return self._format.format(str(self)).rstrip('0').rstrip('.')

	@property
	def formatString(self) -> str:
		# Get number length of number before and after decimal
		# Could probably use a more efficient algorithm
		whole, decimal = (len(n) for n in str(float(self)).strip('0').split('.'))

		# Prevents negative float precision
		decimal = min(self._precision, max(0, self._max - (1 if not whole else whole)) if round(self % 1, self._precision) else 0)
		return f"{{:{whole}.{decimal}{self._unitType}}}"

	@property
	def withUnit(self):
		return self._unitFormat.format(decorated=str(self), unit=self.unit)

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


class Measurement(SmartFloat):
	_type = ''
	_Scale: _utils.ScaleMeta = None

	def __new__(cls, value):
		return SmartFloat.__new__(cls, value)

	def __init__(self, value):
		if isinstance(value, Measurement):
			self._title = value.title
			SmartFloat.__init__(self, value)
		SmartFloat.__init__(self, value)

	def __getitem__(self, item):
		try:
			return self.__getattribute__(item)
		except ValueError:
			raise _errors.BadConversion

	@property
	def _scale(self):
		return self._Scale[self.name]

	@property
	def localized(self):
		if self.convertible:
			try:
				selector = self._config['Units'][self._type.lower()]
				selector = 'inch' if selector == 'in' else selector
				new = getattr(self, selector)
				new.title = self.title
				return new
			except AttributeError or KeyError as e:
				_errors.BadConversion("Unable to get localized type for {}".format(self.name), e)
		else:
			return self

	@property
	def convertible(self):
		return self._type in self._config['Units']

	@property
	def str(self):
		return str(self)

	def __mul__(self, other):
		value = super().__mul__(other)
		return self.__class__(value)

	def __add__(self, other):
		value = super().__add__(other)
		return self.__class__(value)

	def __sub__(self, other):
		value = super().__sub__(other)
		return self.__class__(value)

	def __truediv__(self, other):
		i = 0

		while self.__class__.__mro__[i] != other.__class__.__mro__[i] and i < 4:
			i += 1
		if i == 1 or i == 2:
			value = self.__class__(other)
			value = super().__truediv__(value)
		elif issubclass(self.__class__, Measurement):
			return Derived(self, other)
		return self.__class__(value)


class MeasurementSystem(Measurement):
	_baseUnit = None

	def __new__(cls, value):
		if not cls._baseUnit:
			raise _errors.NoBaseUnitDefined(cls)
		'''For this to work each unit class must have a _baseUnit defined for each scale'''

		# If values are siblings change to sibling class with changeScale()
		if isinstance(value, cls.__mro__[1]):
			return cls(value.__class__.changeScale(value, cls._Scale[cls.__name__]))

		# if values are cousins initiate with values base sibling causing a recursive call to __new__
		elif isinstance(value, cls.__mro__[2]):
			return cls(value.__getattribute__('_' + cls._baseUnit)())

		elif isinstance(value, Measurement):
			raise _errors.BadConversion(cls.__name__, value.__class__.__name__)

		else:
			return Measurement.__new__(cls, value)

	def changeScale(self, newUnit: _utils.ScaleMeta) -> Optional[float]:
		if self._Scale:
			multiplier = self._scale * newUnit
			if self._scale > newUnit:
				return float(self) * multiplier
			else:
				return float(self) / multiplier
		else:
			return None


class Derived(Measurement):
	_type = 'derived'
	_numerator: Measurement
	_denominator: Measurement

	def __new__(cls, numerator, denominator):
		value = float(numerator) / float(denominator)
		return Measurement.__new__(cls, value)

	def __init__(self, numerator, denominator):
		self._numerator = numerator
		self._denominator = denominator
		Measurement.__init__(self, float(self._numerator) / float(self._denominator))

	# TODO: Implement into child classes
	def _getUnit(self) -> tuple[str, str]:
		return _config['Units'][self._type].split('/')

	@property
	def localized(self):
		try:
			newClass = self.__class__
			n, d = self._config['Units'][self._type.lower()].split(',')
			n = 'inch' if n == 'in' else n
			new = newClass(getattr(self._numerator, n), getattr(self._denominator, d))
			new.title = self.title
			return new
		except KeyError:
			logging.error('Measurement {} was unable to localize from {}'.format(self.name, self.unit))
			return self

	@property
	def unit(self):
		if self._suffix:
			return self._suffix
		elif issubclass(self.__class__, Derived):
			l = self.unitArray
			i = 0
			while i < len(l):
				power = 0
				while i + 1 < len(l) and l[i] == l[i + 1]:
					power += 1
					l.pop(i)
				if power:
					unicodePlace = 177 if power < 4 else 0x2074
					l[i] = f"{l[i]}{power + 177:c}"
				i += 1
			return '/'.join(l)
		elif self._numerator.unit == 'mi' and self._denominator.unit == 'hr':
			return 'mph'
		else:
			return '{}/{}'.format(self._numerator.unit, self._denominator.unit)

	@property
	def unitArray(self) -> list[str]:
		return [*self._numerator.unitArray, *self._denominator.unitArray]

	@property
	def numerator(self) -> Measurement:
		return self._numerator
	n = numerator

	@property
	def denominator(self) -> Measurement:
		return self._denominator
	d = denominator
