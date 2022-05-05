from math import inf

from . import Temperature


class Fahrenheit(Temperature):
	_limits = (-459.6699, inf)
	_unit = 'f'

	def _celsius(self, delta: bool = False):
		if delta:
			return self / 1.8
		else:
			return (self - 32) / 1.8

	def _fahrenheit(self, delta: bool = False):
		return self

	def _kelvin(self):
		# (32°F − 32) × 1.8 + 273.15
		return (self - 32) / 1.8 + 273.15
