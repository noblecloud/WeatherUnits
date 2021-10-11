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

	@property
	def lux(self) -> 'Illuminance':
		"""Peter Michael, September 20, 2019, "A Conversion Guide: Solar Irradiance and Lux Illuminance ", IEEE Dataport, doi: https://dx.doi.org/10.21227/mxr7-p365."""
		return Illuminance(float(self) * 120)


@NamedType
class Illuminance(Light):
	_unit = 'lux'

	@property
	def wpm2(self) -> Irradiance:
		"""Peter Michael, September 20, 2019, "A Conversion Guide: Solar Irradiance and Lux Illuminance ", IEEE Dataport, doi: https://dx.doi.org/10.21227/mxr7-p365."""
		return Irradiance(float(self) / 120)


RadiantFlux = Irradiance
Lux = Illuminance
Brightness = Illuminance


Light.UVI = UVI
Light.Illuminance = Illuminance
Light.Irradiance = Irradiance

Light.RadiantFlux = Irradiance
Light.Lux = Illuminance
Light.Brightness = Illuminance
