from enum import Enum

from ..base import Measurement
from .rate import DistanceOverTime
from ..base.Decorators import NamedType, NamedSubType
from ..length import Length
from ..time import Time

__all__ = ['Precipitation']


@NamedType
class Precipitation(Measurement):

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

	def __new__(cls, numerator, denominator: int = 1, *args, **kwargs):
		value = float(numerator) / float(denominator)
		return DistanceOverTime.__new__(cls, numerator, denominator, *args, **kwargs)

	def __init__(self, numerator: Length, denominator: int = 1, *args, **kwargs):
		if isinstance(denominator, int):
			denominator = Time.Hour(denominator)
		DistanceOverTime.__init__(self, numerator, denominator, *args, **kwargs)

	@property
	def fth(self):
		return PrecipitationRate(self._numerator.foot, self._denominator.hour)

	@property
	def inh(self):
		return PrecipitationRate(self._numerator.inch, self._denominator.hour)

	@property
	def ins(self):
		return PrecipitationRate(self._numerator.inch, self._denominator.second)

	@property
	def mmh(self):
		return PrecipitationRate(self._numerator.millimeter, self._denominator.hour)

	@property
	def mms(self):
		return PrecipitationRate(self._numerator.millimeter, self._denominator.second)

	@property
	def cmh(self):
		return PrecipitationRate(self._numerator.centimeter, self._denominator.hour)

	@property
	def mh(self):
		return PrecipitationRate(self._numerator.meter, self._denominator.hour)


@NamedSubType
class Daily(PrecipitationRate):

	def __init__(self, numerator: Length, denominator: int = 1, *args, **kwargs):
		if isinstance(denominator, int):
			denominator = Time.Day(denominator)
		PrecipitationRate.__init__(self, numerator, denominator, *args, **kwargs)


@NamedSubType
class Hourly(PrecipitationRate):

	def __init__(self, numerator: Length, denominator: int = 1, *args, **kwargs):
		if isinstance(denominator, int):
			denominator = Time.Hour(denominator)
		PrecipitationRate.__init__(self, numerator, denominator, *args, **kwargs)


@NamedSubType
class Minutely(PrecipitationRate):

	def __init__(self, numerator: Length, denominator: int = 1, *args, **kwargs):
		if isinstance(denominator, int):
			denominator = Time.Minute(denominator)
		PrecipitationRate.__init__(self, numerator, denominator, *args, **kwargs)


Precipitation.Rate = PrecipitationRate
Precipitation.Daily = Daily
Precipitation.Hourly = Hourly
Precipitation.Minutely = Minutely
