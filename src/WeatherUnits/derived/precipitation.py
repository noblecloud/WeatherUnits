from typing import Union

from enum import Enum

from .rate import DistanceOverTime
from ..base.Decorators import NamedType, NamedSubType
from ..length import Length
from ..time import Time

__all__ = ['Precipitation']


@NamedType
class Precipitation(Length):

	class Type(Enum):
		NONE = 0
		Rain = 1
		Hail = 2
		Sleet = 3
		Snow = 4

	def __new__(cls, value: Length, *args, **kwargs):
		value = value.__class__(value, *args, **kwargs)
		value.__dict__.update(Precipitation.__dict__)
		return value


@NamedType
class PrecipitationRate(DistanceOverTime, Precipitation):
	_numerator: Length
	_denominator: Time
	Daily: type
	Hourly: type
	Minutely: type

	def __init__(self, numerator: Length, denominator: int = 1, *args, **kwargs):
		if isinstance(denominator, int):
			denominator = Time.Hour(denominator)
		DistanceOverTime.__init__(self, numerator, denominator, *args, **kwargs)

	@property
	def fth(self):
		return Hourly(self._numerator.foot, self._denominator.hour)

	@property
	def inh(self):
		return Hourly(self._numerator.inch, self._denominator.hour)

	@property
	def ins(self):
		return PrecipitationRate(self._numerator.inch, self._denominator.second)

	@property
	def mmh(self):
		return Hourly(self._numerator.millimeter, self._denominator.hour)

	@property
	def mms(self):
		return PrecipitationRate(self._numerator.millimeter, self._denominator.second)

	@property
	def cmh(self):
		return Hourly(self._numerator.centimeter, self._denominator.hour)

	@property
	def mh(self):
		return Hourly(self._numerator.meter, self._denominator.hour)

	@property
	def daily(self):
		return Daily(self._numerator, self._denominator)

	@property
	def hourly(self):
		return Hourly(self._numerator, self._denominator)

	@property
	def minutely(self):
		return Minutely(self._numerator, self._denominator)

	@property
	def secondly(self):
		return PrecipitationRate(self._numerator, self._denominator)


@NamedSubType
class Daily(PrecipitationRate):
	_denominator: Time.Day

	def __init__(self, numerator: Length, denominator: Union[Time, int, float] = 1, *args, **kwargs):
		PrecipitationRate.__init__(self, numerator, denominator, *args, **kwargs)


@NamedSubType
class Hourly(PrecipitationRate):
	_denominator: Time.Hour

	def __init__(self, numerator: Length, denominator: Union[Time, int, float] = 1, *args, **kwargs):
		PrecipitationRate.__init__(self, numerator, denominator, *args, **kwargs)


@NamedSubType
class Minutely(PrecipitationRate):
	_denominator: Time.Minute

	def __init__(self, numerator: Length, denominator: Union[Time, int, float] = 1, *args, **kwargs):
		PrecipitationRate.__init__(self, numerator, denominator, *args, **kwargs)


@NamedSubType
class Secondly(PrecipitationRate):
	_denominator: Time.Second

	def __init__(self, numerator: Length, denominator: Union[Time, int, float] = 1, *args, **kwargs):
		PrecipitationRate.__init__(self, numerator, denominator, *args, **kwargs)


Precipitation.Rate = PrecipitationRate
Precipitation.Daily = Daily
Precipitation.Hourly = Hourly
Precipitation.Minutely = Minutely
Precipitation.Secondly = Secondly
