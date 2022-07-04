from ..base.Decorators import UnitType
from ..base import Index, Measurement

__all__ = ['Light']


@UnitType
class Light(Measurement):
	_dimension = 'J'
	UVI: type
	Illuminance: type
	Irradiance: type
	RadiantFlux: type
	Lux: type
	Brightness: type


class UVI(Index, Light, alias='UVI Index'):
	_id = 'uvi'
	_max = 2


class Irradiance(Light):
	_unit = 'W/m²'

	@property
	def lux(self) -> 'Illuminance':
		"""Peter Michael, September 20, 2019, "A Conversion Guide: Solar Irradiance and Lux Illuminance ", IEEE Dataport, doi: https://dx.doi.org/10.21227/mxr7-p365."""
		return Illuminance(float(self)*120)


class Illuminance(Light):
	_unit = 'lux'

	@property
	def wpm2(self) -> Irradiance:
		"""Peter Michael, September 20, 2019, "A Conversion Guide: Solar Irradiance and Lux Illuminance ", IEEE Dataport, doi: https://dx.doi.org/10.21227/mxr7-p365."""
		return Irradiance(float(self)/120)


RadiantFlux = Irradiance
Lux = Illuminance
Brightness = Illuminance

Light.UVI = UVI
Light.Illuminance = Illuminance
Light.Irradiance = Irradiance

Light.RadiantFlux = Irradiance
Light.Lux = Illuminance
Light.Brightness = Illuminance
