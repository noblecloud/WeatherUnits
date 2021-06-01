from . import config as _config
import errors as _errors
import utils


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
	_Scale: utils.ScaleMeta = None

	def __new__(cls, value):
		if isinstance(value, cls.__mro__[1]):
			value = value.__class__.changeScale(value, cls._Scale[cls.__name__])
		if isinstance(value, Measurement):
			raise _errors.BadConversion(cls.__name__, value.__class__.__name__)
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

	def changeScale(self, newUnit: utils.ScaleMeta):
		if self._Scale:
			multiplier = self._scale * newUnit
			if self._scale > newUnit:
				return self * multiplier
			else:
				return self / multiplier
		else:
			return None

	@property
	def _scale(self):
		return self._Scale[self.name]

	@property
	def localized(self):
		if self.convertible:
			try:
				selector = self._config['Units'][self._type.lower()]
				new = self[selector]
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


