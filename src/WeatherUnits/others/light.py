from src.WeatherUnits import Integer
from .. import Measurement, NamedType


@NamedType
class Light(Measurement):
	pass

@Integer
@NamedType
class UVI(Light):
	_max = 2


@NamedType
class Irradiance(Light):
	_unit = 'W/m²'


@MeasurementGroup
class Illuminance(Light):
	_unit = 'lux'

	def __new__(cls, value):
		if value > 1000:
			cls._format = '{2:1f}'
			cls._decorator = 'k'
			value /= 1000
		return float.__new__(cls, value)

	def __init__(self, value):
		float.__init__(value)


RadiantFlux = Irradiance
Lux = Illuminance
Brightness = Illuminance
