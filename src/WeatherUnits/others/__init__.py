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
	_unit_symbol = '%'
	_digit_budget = 3
	_precision = 2

	def __new__(cls, value, isPercentage: bool = None, *args, **kwargs):
		if isPercentage is None:
			if value > cls._limits[1] or isinstance(value, int) and value != 1:
				value /= 100
		elif isPercentage:
			value /= 100

		return super(Percentage, cls).__new__(cls, value, *args, **kwargs)

	def __format__(self, format_spec: str, **extras) -> str:
		return super().__format__(format_spec, **extras)

	def __int__(self) -> int:
		return int(float(self)*100)

	@cached_property
	def valuePrecision(self) -> int:
		value = super().valuePrecision
		return value + 2

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
	_unit_symbol = '%'
	_id = '%h'


class Probability(Percentage, limits=(0.0, 1.0)):
	_unit_symbol = '%'
	_id = '%p'
	_fraction: Optional[Fraction]
	_denominatorLimit: int = 10

	@property
	def fraction(self) -> Fraction:
		if (fraction := getattr(self, '_fraction', None)) is None:
			self._fraction = Fraction(self).limit_denominator(self._denominatorLimit)
		return fraction


class Coverage(Percentage, limits=(0.0, 1.0)):
	_unit_symbol = '%'
	_id = '%c'


class BatteryPercentage(Percentage, limits=(0.0, 1.0)):
	_voltageLimits: Optional[Tuple[float, float]]
	_unit_symbol = '%'
	_id = '%bat'

	def __init__(self, value, voltageLimits: Optional[Tuple[float, float]] = None, *args, **kwargs):
		self._voltageLimits = voltageLimits
		super(BatteryPercentage, self).__init__(value, *args, **kwargs)


@UnitType
class Angle(Dimensionless):
	_precision = 0
	_unit_symbol = '°'
	_shorten = True
	_id = '°'


class Direction(Angle, FiniteField, limits=(0, 360)):
	_cardinal = True
	_unit_symbol = '°'
	_id = '°d'
	_digit_budget = 3

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
		return "{value}{unit_symbol}"

	@property
	def defaultFormat(self) -> str:
		if self._cardinal:
			return self.__cardinalFormat
		return self.__valueFormat

	@property
	def defaultFormatParams(self):
		return {
			'cardinal':     self._cardinal if self._cardinal else False,
			'show_cardinal': self._cardinal,
			**super().defaultFormatParams
		}

	@property
	def properties(self):
		measurement = super().properties
		return {'cardinal': self.cardinal, 'show_cardinal': self._cardinal, **measurement, }

	def __repr_value__(self) -> str:
		return f'{self: cardinal: False}'

	def __format_value__(self, params: Mapping) -> str:
		show_cardinal = getFrom(('show_cardinal', 'cardinal'), *params.maps, default=self._cardinal, expectedType=(bool, str))
		if show_cardinal:
			return self.cardinal.__format_value__(params)
		return super().__format_value__(params)

	def __format_template__(self, params: Mapping) -> str:
		template = super().__format_template__(params)
		show_cardinal = getFrom(('show_cardinal', 'cardinal'), *params.maps, default=self._cardinal, expectedType=(bool, str))
		if show_cardinal and '{cardinal}' not in template:
			template = template.replace('{unit_symbol}', '')
		return template


class Cardinal:
	"""A compass heading, rendered at whatever detail the budget allows.

	`digit_budget` counts **compass components**, and the atom it counts
	depends on the form: a letter when abbreviated, a word when spelled out.
	So the same budget means the same amount of information either way.

	  budget | shorten=True | shorten=False
	  -------|--------------|--------------------
	     1   | N            | North
	     2   | NE           | North East
	     3   | SSW          | South South West

	The word forms are *derived* from the abbreviations rather than kept in
	a parallel list. A hardcoded list drifts out of alignment: the previous
	one spelled the 2-component 'NE' as the single word 'Northeast' and the
	3-component 'SSW' as the 2-word 'South Southwest', so word count never
	matched the budget and the two forms disagreed about how much detail
	they were showing.
	"""
	__slots__ = '__direction'
	__dirsAbbrv = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
	__components = {'N': 'North', 'E': 'East', 'S': 'South', 'W': 'West'}
	__direction: Direction
	direction: Direction

	def __init__(self, direction: Direction):
		self.__direction = direction

	def __str__(self):
		if self.shorten:
			return self.abbrivated
		else:
			return self.spelled

	def __format_value__(self, params: Mapping) -> str:
		# Two independent axes:
		#   `shorten`     picks the FORM   - letters vs words
		#   digit_budget  picks the DETAIL - how many compass components
		# Both forms read the same budget through the same index ladder, so
		# they always name the same heading and differ only in spelling.
		shorten = getFrom('shorten', *getattr(params, 'maps', (params,)),
			default=self.shorten, expectedType=(bool, str))
		if shorten:
			return self.abbrivated
		return self.spelled

	def __repr__(self):
		return f'Cardinal({self!s} {self.direction: cardinal: False})'

	@property
	def direction(self) -> Direction:
		return self.__direction

	@property
	def __quarterIndex(self):
		return int(round(self.direction/90)%4)*4

	@property
	def __shortIndex(self):
		return int(round(self.direction/45)%8)*2

	@property
	def __longIndex(self):
		return int(round(self.direction/22.5)%16)

	def _indexFor(self, components: int) -> int:
		"""The compass index at a given number of components.

		One index ladder, shared by both forms, so letters and words always
		name the same heading at the same budget.
		"""
		if components <= 1:
			return self.__quarterIndex     # 4-point:  N  E  S  W
		if components == 2:
			return self.__shortIndex       # 8-point:  NE SE SW NW
		return self.__longIndex            # 16-point: NNE ESE SSW WNW

	def letters(self, components: int) -> str:
		return self.__dirsAbbrv[self._indexFor(components)]

	def words(self, components: int) -> str:
		"""Spelled out, one word per component - 'SSW' -> 'South South West'."""
		return ' '.join(self.__components[c] for c in self.letters(components))

	@property
	def oneLetter(self):
		"""The 4-point compass: N, E, S, W. Always exactly one character."""
		return self.letters(1)

	@property
	def twoLetter(self):
		return self.letters(2)

	@property
	def threeLetter(self):
		return self.letters(3)

	@property
	def abbrivated(self):
		return self.letters(self.direction.digit_budget)

	@property
	def spelled(self):
		return self.words(self.direction.digit_budget)

	@property
	def full(self):
		"""Every component spelled out, regardless of budget."""
		return self.words(3)

	@property
	def shorten(self):
		return self.direction.shorten

	@shorten.setter
	def shorten(self, value: bool):
		self.direction.shorten = value


class Voltage(Measurement):
	_digit_budget = 3
	_precision = 2
	_unit = 'v'


class LightningStrike(Quantity, altName='Strike'):
	...


# class OzoneThickness(Millimeter, altName='Dobson'):
# 	_unit = 'DU'
# 	_precision = 0
#
# 	@property
# 	def ppm(self) -> 'Ozone':
# 		return Ozone(float(self) * 2.69e-5)
#
#
# class Ozone(PartPerMillion, altName='O3'):
# 	_unit = 'ppm'
# 	_precision = 0
#
# 	@property
# 	def du(self) -> 'OzoneThickness':
# 		return OzoneThickness(float(self) / 2.69e-5)




Percentage.Humidity = Humidity
Percentage.Probability = Probability
Percentage.Coverage = Coverage
Percentage.BatteryPercentage = BatteryPercentage

Angle.Direction = Direction
Direction.Cardinal = Cardinal
Angle.Cardinal = Cardinal
