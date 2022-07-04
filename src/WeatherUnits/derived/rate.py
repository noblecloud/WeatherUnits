from datetime import timedelta as _td

__all__ = ['DistanceOverTime']

from ..base.Decorators import UnitType
from . import Length, Time, DerivedMeasurement


@UnitType
class DistanceOverTime(DerivedMeasurement, numerator=Length, denominator=Time):

	def __new__(cls, numerator: Length, denominator: Time = None):
		if isinstance(denominator, _td):
			denominator = Time.Second(denominator.total_seconds())
		return super().__new__(cls, numerator, denominator)

	def __init__(self, numerator: Length, denominator: Time = None):
		if isinstance(denominator, _td):
			denominator = Time.Second(denominator.total_seconds())
		super().__init__(numerator, denominator)

	@property
	def fts(self):
		return DistanceOverTime(self._numerator.ft, self._denominator.s)

	@property
	def mih(self):
		converted = MilesPerHour(self._numerator.mi, self._denominator.hr)
		return converted

	@property
	def inh(self):
		return DistanceOverTime(self._numerator.inch, self._denominator.hr)

	@property
	def ms(self):
		return DistanceOverTime(self._numerator.m, self._denominator.s)

	@property
	def mh(self):
		return DistanceOverTime(self._numerator.m, self._denominator.hr)

	@property
	def kmh(self):
		return DistanceOverTime(self._numerator.km, self._denominator.hr)

	@property
	def mmh(self):
		return DistanceOverTime(self._numerator.mm, self._denominator.hr)

	mph = mih
	fps = fts


class PerSecond(DistanceOverTime, numerator=Length, denominator=Time.Second):
	...


class PerMinute(DistanceOverTime, numerator=Length, denominator=Time.Minute):
	...


class PerHour(DistanceOverTime, numerator=Length, denominator=Time.Hour):
	...


class MilesPerHour(PerHour, numerator=Length.Mile, unit='mph'):
	...


class MetersPerSecond(PerSecond, numerator=Length.Meter):
	...


DistanceOverTime.PerSecond = PerSecond
DistanceOverTime.PerMinute = PerMinute
DistanceOverTime.PerHour = PerHour
DistanceOverTime.MilesPerHour = MilesPerHour
DistanceOverTime.MetersPerSecond = MetersPerSecond
DistanceOverTime.MetersPerHour = MetersPerSecond
