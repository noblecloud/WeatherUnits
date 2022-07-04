from math import inf

from ..base import metric
from .temperature import Temperature

__all__ = ['Kelvin']


class Kelvin(Temperature, system=metric):
	_limits = (0, inf)
	_unit = 'k'

	def _kelvin(self):
		return self

	def _celsius(self, delta: bool = False):
		return float(self) - 273.15

	def _fahrenheit(self, delta: bool = False):
		if delta:
			return (float(self) - 273.15)*1.8
		else:
			return ((float(self) - 273.15)*1.8) + 32
