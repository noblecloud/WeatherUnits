from enum import Enum

from .speed import Speed
from ..base.Decorators import NamedType, NamedSubType
from ..base.Measurement import Measurement
from ..length import Length
from ..time import Time

__all__ = ['Precipitation']


@NamedType
class Precipitation(Speed):
	_numerator: Length
	_denominator: Time
	Daily: type
	Hourly: type
	Minutely: type

	class Type(Enum):
		NONE = 0
		Rain = 1
		Hail = 2
		Sleet = 3
		Snow = 4

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
class Daily(Precipitation):
	# def __new__(cls, numerator: Length, denominator: int = 1):
	# 	value = float(numerator) / float(denominator)
	# 	return Measurement.__new__(cls, value)

	def __init__(self, numerator: Length, denominator: int = 1):
		self._numerator = numerator
		self._denominator = Time.Day(denominator)
		Measurement.__init__(self, float(self._numerator) / float(self._denominator))


@NamedSubType
class Hourly(Precipitation):
	def __new__(cls, numerator: Length, denominator: int = 1):
		value = float(numerator) / float(denominator)
		return Measurement.__new__(cls, value)

	def __init__(self, numerator: Length, denominator: int = 1):
		self._numerator = numerator
		self._denominator = Time.Hour(denominator)
		Measurement.__init__(self, float(self._numerator) / float(self._denominator))


@NamedSubType
class Minutely(Precipitation):
	def __new__(cls, numerator: Length, denominator: int = 1):
		value = float(numerator) / float(denominator)
		return Measurement.__new__(cls, value)

	def __init__(self, numerator: Length, denominator: int = 1):
		self._numerator = numerator
		self._denominator = Time.Minute(denominator)
		Measurement.__init__(self, float(self._numerator) / float(self._denominator))


Precipitation.Daily = Daily
Precipitation.Hourly = Hourly
Precipitation.Minutely = Minutely
