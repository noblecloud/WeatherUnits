from ..length import Length
from ..time import Time
from . import Derived


class Wind(Derived):
	_type = 'wind'
	_numerator: Length
	_denominator: Time

	@property
	def fts(self):
		return Wind(self._numerator.ft, self._denominator.s)

	@property
	def mih(self):
		converted = Wind(self._numerator.mi, self._denominator.hr)
		converted._suffix = 'mph'
		return converted

	@property
	def inh(self):
		return Wind(self._numerator.inch, self._denominator.hr)

	@property
	def ms(self):
		return Wind(self._numerator.m, self._denominator.s)

	@property
	def mh(self):
		return Wind(self._numerator.m, self._denominator.hr)

	@property
	def kmh(self):
		return Wind(self._numerator.km, self._denominator.hr)

	@property
	def mmh(self):
		return Wind(self._numerator.mm, self._denominator.hr)

