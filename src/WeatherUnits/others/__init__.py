from fractions import Fraction
from functools import cached_property
from typing import Optional, Tuple, Mapping

from ..base import Dimensionless, NonPlural, Measurement, Quantity, FiniteField, UnitType
from ..utils import getFrom
from . import light

Light = light.Light

__all__ = ['Light', 'Angle', 'Direction', 'Humidity', 'Voltage', 'LightningStrike', 'Probability', 'Coverage', 'Percentage']


@UnitType
class Percentage(Dimensionless, NonPlural):
	_decorator = '%'
	_max = 3
	_precision = 2

	def __new__(cls, value, isPercentage: bool = None, *args, **kwargs):
		if isPercentage is None:
			if value > cls._limits[1] or isinstance(value, int) and value != 1:
				value /= 100
		elif isPercentage:
			value /= 100

		return super(Percentage, cls).__new__(cls, value, *args, **kwargs)

	def __format__(self, format_spec: str) -> str:
		return super().__format__(format_spec)

	def __int__(self) -> int:
		return int(float(self)*100)

	# @property
	# def defaultFormatParams(self):
	# 	sup = super().defaultFormatParams
	# 	sup['type'] = '%'
	# 	return sup

	@classmethod
	def fromFloat(cls, value: float) -> 'Percentage':
		return cls(value, isPercentage=False, limits=False)

	@property
	def formatValue(self) -> float:
		return float(self)*100


class Humidity(Percentage, limits=(0.0, 1.0)):
	_decorator = '%'
	_id = '%h'


class Probability(Percentage, limits=(0.0, 1.0)):
	_decorator = '%'
	_id = '%p'
	_fraction: Optional[Fraction]
	_denominatorLimit: int = 10

	@property
	def fraction(self) -> Fraction:
		if (fraction := getattr(self, '_fraction', None)) is None:
			self._fraction = Fraction(self).limit_denominator(self._denominatorLimit)
		return fraction


class Coverage(Percentage, limits=(0.0, 1.0)):
	_decorator = '%'
	_id = '%c'


class BatteryPercentage(Percentage, limits=(0.0, 1.0)):
	_voltageLimits: Optional[Tuple[float, float]]
	_decorator = '%'
	_id = '%bat'

	def __init__(self, value, voltageLimits: Optional[Tuple[float, float]] = None, *args, **kwargs):
		self._voltageLimits = voltageLimits
		super(BatteryPercentage, self).__init__(value, *args, **kwargs)


@UnitType
class Angle(Dimensionless):
	_precision = 0
	_decorator = 'º'
	_shorten = True
	_id = 'º'


class Direction(Angle, FiniteField, limits=(0, 360)):
	_cardinal = True
	_decorator = 'º'
	_id = '°d'
	_max = 3

	@cached_property
	def cardinal(self) -> 'Cardinal':
		return Cardinal(self)

	@property
	def angle(self) -> Angle:
		return Angle(self)

	@property
	def decoratedInt(self) -> str:
		return super()._string(forceUnit=False, asInt=True)

	@property
	def __cardinalFormat(self):
		return '{value}'

	@property
	def __valueFormat(self):
		return "{value}{decorator}"

	@property
	def defaultFormat(self) -> str:
		if self._cardinal:
			return self.__cardinalFormat
		return self.__valueFormat

	@property
	def defaultFormatParams(self):
		return {
			'cardinal':     self._cardinal if self._cardinal else False,
			'showCardinal': self._cardinal,
			**super().defaultFormatParams
		}

	@property
	def properties(self):
		measurement = super().properties
		return {'cardinal': self.cardinal, 'showCardinal': self._cardinal, **measurement, }

	def __repr_value__(self) -> str:
		return f'{self: cardinal: False}'

	def __format_value__(self, params: Mapping) -> str:
		showCardinal = getFrom(('showCardinal', 'cardinal'), *params.maps, default=self._cardinal, expectedType=(bool, str))
		if showCardinal:
			return self.cardinal.__format_value__(params)
		return super().__format_value__(params)

	def __format_template__(self, params: Mapping) -> str:
		template = super().__format_template__(params)
		showCardinal = getFrom(('showCardinal', 'cardinal'), *params.maps, default=self._cardinal, expectedType=(bool, str))
		if showCardinal and '{cardinal}' not in template:
			template = template.replace('{decorator}', '')
		return template


class Cardinal:
	__slots__ = '__direction'
	__dirsAbbrv = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
	__dirsFull = ['North', 'North Northeast', 'Northeast', 'East Northeast', 'East', 'East Southeast', 'Southeast',
		'South Southeast', 'South', 'South Southwest', 'Southwest', 'West Southwest', 'West',
		'West Northwest', 'Northwest', 'North Northwest']
	__direction: Direction
	direction: Direction

	def __init__(self, direction: Direction):
		self.__direction = direction

	def __str__(self):
		if self.shorten:
			return self.abbrivated
		else:
			return self.full

	def __format_value__(self, params: Mapping) -> str:
		if self.shorten:
			return self.abbrivated
		else:
			return self.full

	def __repr__(self):
		return f'Cardinal({self!s} {self.direction: cardinal: False})'

	@property
	def direction(self) -> Direction:
		return self.__direction

	@property
	def __shortIndex(self):
		return round(self.direction/45)%8*2

	@property
	def __longIndex(self):
		return round(self.direction/22.5)%16

	@property
	def abbrivated(self):
		if self.direction.max > 2:
			return self.threeLetter
		return self.twoLetter

	@property
	def shortened(self):
		if self.direction.max < 5:
			return self.abbrivated
		return self.singleWord

	@property
	def twoLetter(self):
		return self.__dirsAbbrv[self.__shortIndex]

	@property
	def threeLetter(self):
		return self.__dirsAbbrv[self.__longIndex]

	@property
	def singleWord(self):
		return self.__dirsFull[self.__shortIndex]

	@property
	def text(self):
		if self.direction.max < 7:
			return self.singleWord
		return self.full

	@property
	def full(self):
		return self.__dirsFull[self.__longIndex]

	@property
	def shorten(self):
		return self.direction.shorten

	@shorten.setter
	def shorten(self, value: bool):
		self.direction.shorten = value


class Voltage(Measurement):
	_max = 3
	_precision = 2
	_unit = 'v'


class LightningStrike(Quantity, altName='Strike'):
	...


Percentage.Humidity = Humidity
Percentage.Probability = Probability
Percentage.Coverage = Coverage
Percentage.BatteryPercentage = BatteryPercentage

Angle.Direction = Direction
Direction.Cardinal = Cardinal
Angle.Cardinal = Cardinal
