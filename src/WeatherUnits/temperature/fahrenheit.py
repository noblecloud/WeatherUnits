from math import inf

from ..base import imperial
from .temperature import Temperature

__all__ = ['Fahrenheit']


class Fahrenheit(Temperature, system=imperial):
	_limits = (-459.6699, inf)
	_unit = 'f'

	def _celsius(self, delta: bool = False):
		if delta:
			return self/1.8
		else:
			return (float(self) - 32)/1.8

	def _fahrenheit(self, delta: bool = False):
		return self

	def _kelvin(self):
		# (32°F − 32) × 1.8 + 273.15
		return (float(self) - 32)/1.8 + 273.15
