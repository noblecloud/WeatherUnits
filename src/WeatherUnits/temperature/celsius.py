from math import inf

from ..base import metric
from .temperature import Temperature

__all__ = ['Celsius']


class Celsius(Temperature, system=metric):
	_limits = (-273.15, inf)
	_unit = 'c'

	def _celsius(self, delta: bool = False):
		return self

	def _fahrenheit(self, delta: bool = False):
		if delta:
			return float(self)*1.8
		else:
			return (float(self)*1.8) + 32

	def _kelvin(self):
		return float(self) + 273.15
