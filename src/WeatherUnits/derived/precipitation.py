from .speed import Speed as _Rate
from .. import NamedType, Measurement as _Measurement, NamedSubType
from ..length import Length as _Length
from ..time import Day as _Day, Minute as _Minute, Hour as _Hour


@NamedType
class Precipitation(_Rate):

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


@NamedSubType
class PrecipitationDaily(Precipitation):
	def __new__(cls, numerator: _Length, denominator: int = 1):
		value = float(numerator) / float(denominator)
		return _Measurement.__new__(cls, value)

	def __init__(self, numerator: _Length, denominator: int = 1):
		self._numerator = numerator
		self._denominator = _Day(denominator)
		_Measurement.__init__(self, float(self._numerator) / float(self._denominator))


@NamedSubType
class PrecipitationHourly(Precipitation):
	def __new__(cls, numerator: _Length, denominator: int = 1):
		value = float(numerator) / float(denominator)
		return _Measurement.__new__(cls, value)

	def __init__(self, numerator: _Length, denominator: int = 1):
		self._numerator = numerator
		self._denominator = _Hour(denominator)
		_Measurement.__init__(self, float(self._numerator) / float(self._denominator))


@NamedSubType
class PrecipitationMinutely(Precipitation):
	def __new__(cls, numerator: _Length, denominator: int = 1):
		value = float(numerator) / float(denominator)
		return _Measurement.__new__(cls, value)

	def __init__(self, numerator: _Length, denominator: int = 1):
		self._numerator = numerator
		self._denominator = _Minute(denominator)
		_Measurement.__init__(self, float(self._numerator) / float(self._denominator))
