from typing import Union

from ..length import Length
from ..time import Time
from .rate import DistanceOverTime
from ..base import NamedType, NamedSubType
from ..others import Direction

__all__ = ['Wind']


@NamedType
class Wind(DistanceOverTime):
	_numerator: Length
	_denominator: Time

	# TODO: Add support for setting both speed and direction
	__direction: Direction = None

	# def __init__(self, speed: DistanceOverTime = None, direction: Direction = None):
	# 	if direction is not None:
	# 		self.__direction = direction
	# 	if
	# 	super(Wind, self).__init__(DistanceOverTime)

	@property
	def direction(self):
		return self.__direction

	@direction.setter
	def direction(self, value):
		if not isinstance(value, Direction) and isinstance(value, (float, int)):
			value = Direction(value)
		self.__direction = value


@NamedSubType
class PerSecond(Wind):
	_denominator: Time.Second

	def __init__(self, numerator: Length, denominator: Union[Time, int, float] = 1, *args, **kwargs):
		denominator = Time.Second(denominator)
		Wind.__init__(self, numerator, denominator, *args, **kwargs)


@NamedSubType
class PerMinute(Wind):
	_denominator: Time.Minute

	def __init__(self, numerator: Length, denominator: Union[Time, int, float] = 1, *args, **kwargs):
		denominator = Time.Minute(denominator)
		Wind.__init__(self, numerator, denominator, *args, **kwargs)


@NamedSubType
class PerHour(Wind):
	_denominator: Time.Hour

	def __init__(self, numerator: Length, denominator: Union[Time, int, float] = 1, *args, **kwargs):
		denominator = Time.Hour(denominator)
		Wind.__init__(self, numerator, denominator, *args, **kwargs)
