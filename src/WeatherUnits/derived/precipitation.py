from enum import Enum

from ..base.Decorators import UnitType
from . import Length, Time, DistanceOverTime

__all__ = ['Precipitation']


class Precipitation:
	class Type(Enum):
		NONE = 0
		Rain = 1
		Hail = 2
		Sleet = 3
		Snow = 4


@UnitType
class PrecipitationRate(DistanceOverTime, Precipitation, limit=(0.0, None)):
	Daily: type
	Hourly: type
	Minutely: type

	def __init__(self, numerator: Length, denominator: int = None, *args, **kwargs):
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
		return Secondly(self.numerator, self.denominator)


class Daily(PrecipitationRate, denominator=Time.Day): ...


class Hourly(PrecipitationRate, denominator=Time.Hour): ...


class Minutely(PrecipitationRate, denominator=Time.Minute): ...


class Secondly(PrecipitationRate, denominator=Time.Second): ...


Precipitation.Rate = PrecipitationRate
Precipitation.Daily = Daily
Precipitation.Hourly = Hourly
Precipitation.Minutely = Minutely
Precipitation.Secondly = Secondly
