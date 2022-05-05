from math import inf

from . import Temperature


class Kelvin(Temperature):
	_limits = (0, inf)
	_unit = 'k'

	def _kelvin(self):
		return self

	def _celsius(self, delta: bool = False):
		return self - 273.15

	def _fahrenheit(self, delta: bool = False):
		if delta:
			return (self - 273.15) * 1.8
		else:
			return ((self - 273.15) * 1.8) + 32
