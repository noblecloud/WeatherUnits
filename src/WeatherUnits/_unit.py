from typing import Union
from . import config
from .errors import BadConversion


class SmartFloat(float):
	_config = config
	_precision: int = 1
	_max = 3

	_unitType: str = 'f'
	_unit: str = ''
	_suffix: str = ''
	_decorator: str = ''
	_unitFormat: str = '{decorated} {unit}'
	_format: str = '{value}{decorator}'

	def __new__(cls, value):
		return float.__new__(cls, value)

	def __init__(self, value):
		decimal = list(len(n) for n in str(value).split('.'))[-1]
		self._precision = min(self._precision, decimal)
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


class Measurement(SmartFloat):
	_type = ''

	def __new__(cls, value):
		return SmartFloat.__new__(cls, value)

	def __init__(self, value):
		self._config = config
		SmartFloat.__init__(self, value)

	def __getitem__(self, item):
		try:
			return self.__getattribute__(item)
		except ValueError:
			raise BadConversion

	@property
	def localized(self):
		if self.convertible:
			try:
				return self[self._config['Units'][self._type.lower()]]
			except AttributeError or KeyError as e:
				BadConversion("Unable to get localized type for {}".format(self.name), e)
		else:
			return self

	@property
	def convertible(self):
		return self._type in self._config['Units']

	@property
	def str(self):
		return str(self)


class AbnormalScale(Measurement):
	_value: Union[int, float]
	_factors: list[int, float]
	_scale: int

	def changeScale(self, newScale: Union[int, float]):
		newScale += 1
		newValue = self
		if newScale < self._scale + 1:
			for x in self._factors[newScale:self._scale + 1]:
				newValue *= x
		elif newScale > self._scale + 1:
			for x in self._factors[self._scale + 1:newScale]:
				newValue /= x

		return newValue
