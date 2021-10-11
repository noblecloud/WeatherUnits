from fractions import Fraction
from typing import Optional

from ..base import NamedType
from ..base import Measurement
from . import light

Light = light.Light

__all__ = ['Light', 'Angle', 'Direction', 'Humidity', 'Voltage', 'Strikes', 'Probability', 'Coverage', 'Percentage']


class Percentage(Measurement):
	_unit = ''
	_decorator = '%'
	_maxValue = 1.0
	_minValue = 0.0

	def __new__(cls, value, isPercentage: bool = None, limits: bool = True, *args, **kwargs):
		if isPercentage is None:
			if value > cls._maxValue:
				value /= 100
		elif isPercentage:
			value /= 100

		if limits:
			value = min(cls._maxValue, max(value, cls._minValue))

		return super(Percentage, cls).__new__(cls, value, *args, **kwargs)
	
	def _string(self, *args, **kwargs):
		kwargs['multiplier'] = 100
		return super(Percentage, self)._string(*args, **kwargs)

	def __int__(self) -> int:
		return int(float(self) * 100)

	def fromFloat(self, value: float) -> 'Percentage':
		return Percentage(value, isPercentage=False, limits=False)


@NamedType
class Humidity(Percentage):
	_decorator = '%'


@NamedType
class Probability(Measurement):
	_decorator = '%'
	_fraction: Optional[Fraction]
	_denominatorLimit: int = 10

	def __init__(self, *args, **kwargs):
		self._fraction: Optional[Fraction] = None
		super(Probability, self).__init__(*args, **kwargs)

	@property
	def fraction(self) -> Fraction:
		if self._fraction is None:
			self._fraction = Fraction(self).limit_denominator(self._denominatorLimit)
		return self._fraction


@NamedType
class Coverage(Percentage):
	_decorator = '%'


@NamedType
class Angle(Measurement):
	_precision = 0
	_decorator = 'º'
	_cardinal = True
	_max = 3

	_dirsAbbrv = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
	_dirsFull = ['North', 'North Northeast', 'Northeast', 'East Northeast', 'East', 'East Southeast', 'Southeast',
	             'South Southeast', 'South', 'South Southwest', 'Southwest', 'West Southwest', 'West',
	             'West Northwest', 'Northwest', 'North Northwest']

	def _string(self, **kwargs) -> str:
		if self._cardinal and self._degrees:
			return f'{self.cardinal} ({super()._string(**kwargs)})'
		if self._cardinal:
			return f'{self.cardinal}'
		else:
			return f'{super()._string(**kwargs)}'

	@property
	def cardinal(self):
		if self._max < 3 and self._shorten:
			return self._dirsAbbrv[round(self / 45) % 8 * 2]
		if self._shorten:
			return self._dirsAbbrv[round(self / 22.5) % 16]
		else:
			return self._dirsFull[round(self / 22.5) % 16]

	@property
	def angle(self):
		return Angle(self)

	@property
	def decorator(self):
		return self._decorator if not self._cardinal else ''


@NamedType
class Voltage(Measurement):
	_max = 3
	_precision = 2
	_unit = 'v'


@NamedType
class Strikes(Measurement):
	# TODO: Create discrete number class for this and similar measurements
	unit = 'strikes'
