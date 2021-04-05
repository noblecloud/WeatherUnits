from ..length import Length
from . import Derived
from ..time import Time


class Precipitation(Derived):
	_type = 'precipitationRate'
	_numerator: Length
	_denominator: Time

	@property
	def fth(self):
		return Precipitation(self._numerator.ft, self._denominator.hr)

	@property
	def inh(self):
		return Precipitation(self._numerator.inch, self._denominator.hr)

	@property
	def ins(self):
		return Precipitation(self._numerator.inch, self._denominator.s)

	@property
	def mmh(self):
		return Precipitation(self._numerator.mm, self._denominator.hr)

	@property
	def mms(self):
		return Precipitation(self._numerator.mm, self._denominator.s)

	@property
	def cmh(self):
		return Precipitation(self._numerator.cm, self._denominator.hr)

	@property
	def mh(self):
		return Precipitation(self._numerator.m, self._denominator.hr)
