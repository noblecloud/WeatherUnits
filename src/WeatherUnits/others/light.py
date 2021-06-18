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


@NamedType
class Illuminance(Light):
	_unit = 'lux'


RadiantFlux = Irradiance
Lux = Illuminance
Brightness = Illuminance
