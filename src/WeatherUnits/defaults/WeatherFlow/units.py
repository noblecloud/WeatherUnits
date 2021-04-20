from enum import Enum

from ... import derived, temperature, length, mass, time
from ..._unit import Measurement


class Wind(derived.Wind):

	def __new__(cls, numerator):
		value = numerator / 1
		return Measurement.__new__(cls, value)

	def __init__(self, value):
		numerator = length.Meter(float(value))
		denominator = time.Second(1)
		n, d = self._config['Units']['wind'].split(',')
		super(Wind, self).__init__(numerator[n], denominator[d])

	@property
	def localized(self):
		return self


class Temperature(temperature.Celsius):
	pass


class Density(derived.Density):

	def __new__(cls, numerator: mass.Mass):
		numerator = mass.Kilogram(float(numerator))
		denominator = derived.CubicMeter(1)
		n, d = cls._config['Units']['density'].split(',')
		value = numerator[n]/denominator[d]
		return Measurement.__new__(cls, value)

	def __init__(self, value):
		numerator = mass.Kilogram(float(value))
		denominator = derived.CubicMeter(1)
		n, d = self._config['Units']['density'].split(',')
		super(Density, self).__init__(numerator[n], denominator[d])

	@property
	def localized(self):
		return self


class Precipitation(derived.Precipitation):
	def __new__(cls, numerator):
		value = numerator / 1
		return Measurement.__new__(cls, value)

	def __init__(self, value):
		numerator = length.Millimeter(float(value))
		denominator = time.Hour(1)
		n, d = self._config['Units']['precipitationRate'].split(',')
		super(Precipitation, self).__init__(numerator[n], denominator[d])

	@property
	def localized(self):
		return self


class PrecipitationDaily(derived.Precipitation):
	def __new__(cls, numerator):
		value = numerator / 1
		return Measurement.__new__(cls, value)

	def __init__(self, value):
		numerator = length.Millimeter(float(value))
		denominator = time.Day(1)
		n, d = self._config['Units']['wind'].split(',')
		super(PrecipitationDaily, self).__init__(numerator[n], denominator[d])


class PrecipitationType(Enum):
	NONE = 0
	RAIN = 1
	HAIL = 2

