from ..base import Integer
from ..base import NamedType
from ..base import Measurement


@NamedType
class Light(Measurement):
	pass

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
