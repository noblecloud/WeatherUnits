import logging
from typing import Callable, Optional

from .SmartFloat import Meta
from .. import errors
from . import SmartFloat

__all__ = ['Measurement', 'DerivedMeasurement']

log = logging.getLogger('WeatherUnits')


class Measurement(SmartFloat):
	_type: type = None
	_updateFunction: Optional[Callable] = None

	def __new__(cls, value):
		return SmartFloat.__new__(cls, value)

	def __init__(self, value, title: str = None):
		if isinstance(value, Measurement):
			if title is not None:
				self._title = title
			else:
				self._title = value.title
			SmartFloat.__init__(self, value)
		SmartFloat.__init__(self, value)

	@property
	def localize(self):
		if self.convertible:
			try:
				selector = self._config['Units'][self.type.__name__.lower()]
				selector = 'inch' if selector == 'in' else selector
				new = getattr(self, selector)
				new.title = self.title
				return new
			except AttributeError or KeyError as e:
				errors.Conversion.BadConversion("Unable to get localized type for {}".format(self.name), e)
		else:
			return self

	@property
	def convertible(self):
		return self._type.__name__.lower() in self._config['Units']

	@property
	def str(self):
		return str(self)

	@property
	def type(self) -> type:
		return self._type if self._type is not None else self.__class__.__mro__[0]

	@property
	def updateFunction(self):
		return self._updateFunction

	@updateFunction.setter
	def updateFunction(self, function: callable):
		self._updateFunction = function

	def _convert(self, other):
		if isinstance(other, self.type):
			return self.__class__(other)
		else:
			return other

	def transform(self, other):
		if isinstance(other, type) and issubclass(other, Measurement):
			other = other(self)
		nonTransferred = ['_unit', '_suffix', '_scale', '_denominator', '_numerator']
		if self.type != other.type:
			log.warning(f'{self.withUnit} and {other.withUnit} are not identical types, this may cause issues')
		other.__dict__.update({key:value for key, value in self.__dict__.items() if key not in nonTransferred and value is not None})
		if other._updateFunction:
			other._updateFunction(other)
		return other

	def __getitem__(self, item):
		try:
			return self.__getattribute__(item)
		except ValueError:
			raise errors.Conversion.BadConversion

	def __mul__(self, other):
		other = self._convert(other) if isinstance(other, self.type) else other
		return self.__class__(super().__mul__(other))

	def __add__(self, other):
		other = self._convert(other) if isinstance(other, self.type) else other
		return self.__class__(super().__add__(other))

	def __sub__(self, other):
		other = self._convert(other) if isinstance(other, self.type) else other
		return self.__class__(super().__sub__(other))

	def __truediv__(self, other):
		other = self._convert(other)

		if isinstance(other, self.type):
			value = super().__truediv__(self._convert(other))

		elif issubclass(self.__class__, DerivedMeasurement) and not isinstance(other, Measurement):
			return DerivedMeasurement(self, self.denominator.__class__(other))

		elif not isinstance(other, Measurement):
			value = super().__truediv__(float(other))

		elif issubclass(other.__class__, Measurement):
			return DerivedMeasurement(self, other)

		return self.__class__(value)

	## Transform shortcuts ##

	def __or__(self, other):
		return self.transform(other)

	def __lshift__(self, other):
		return self.transform(other)


class DerivedMeasurement(Measurement):
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
		return self._config['Units'][self._type].split('/')

	@property
	def localize(self):
		try:

			n, d = self._config['Units'][self.type.__name__.lower()].split('/')
			n = 'inch' if n == 'in' else n
			d = self.d.unit if d == '*' else d
			new = newClass(getattr(self._numerator, n), getattr(self._denominator, d))
			new.title = self.title
			return new
		except KeyError:
			log.error('Measurement {} was unable to localize from {}'.format(self.name, self.unit))
			return self

	@property
	def unit(self):
		if self._unit:
			return self._unit
		elif self._numerator.unit == 'mi' and self._denominator.unit == 'hr':
			return 'mph'
		elif issubclass(self.__class__, DerivedMeasurement):
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

	@property
	def dArr(self):
		arr = []
		if isinstance(self.n, DerivedMeasurement):
			arr += [*self.n.dArr]
		if isinstance(self.d, DerivedMeasurement):
			arr += [*self.d.dArr]
		else:
			arr += [self.d.unit]
		return arr

	@property
	def nArr(self):
		arr = []
		if isinstance(self.d, DerivedMeasurement):
			arr += [*self.n.nArr]
		if isinstance(self.n, DerivedMeasurement):
			arr += [*self.n.nArr]
		else:
			arr += [self.n.unit]
		return arr
