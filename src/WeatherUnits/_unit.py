from typing import Optional, Union

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
		value = super().__truediv__(other)
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
