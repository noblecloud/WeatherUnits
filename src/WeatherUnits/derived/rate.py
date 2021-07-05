from ..length import Length
from ..time import Time
from ..base.Measurement import DerivedMeasurement
from ..base.Decorators import NamedType


__all__ = ['DistanceOverTime']


@NamedType
class DistanceOverTime(DerivedMeasurement):
	_numerator: Length
	_denominator: Time

	@property
	def fts(self):
		return DistanceOverTime(self._numerator.ft, self._denominator.s)

	@property
	def mih(self):
		converted = DistanceOverTime(self._numerator.mi, self._denominator.hr)
		converted._suffix = 'mph'
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
