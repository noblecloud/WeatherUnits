from ..base import Integer
from ..base import NamedType
from ..base import Measurement


__all__ = ['Light']

@NamedType
class Light(Measurement):
	UVI: type
	Illuminance: type
	Irradiance: type
	RadiantFlux: type
	Lux: type
	Brightness: type

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


Light.UVI = UVI
Light.Illuminance = Illuminance
Light.Irradiance = Irradiance

Light.RadiantFlux = Irradiance
Light.Lux = Illuminance
Light.Brightness = Illuminance
