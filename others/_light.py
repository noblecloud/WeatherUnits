from units._unit import Measurement


class Irradiance(Measurement):
	_format = "{:4d}"
	_unit = 'W/m²'
	_suffix = ''


class RadiantFlux(Irradiance):
	pass


class Illuminance(Measurement):
	_format = "{:4d}"
	_unit = 'lux'
	_suffix = ''

	def __new__(cls, value):
		if value > 1000:
			cls._format = '{2:1f}'
			cls._suffix = 'k'
			value /= 1000
		return float.__new__(cls, value)

	def __init__(self, value):
		float.__init__(value)


class Lux(Illuminance):
	pass
