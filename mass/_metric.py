from typing import Any

from . import Mass


class _Metric(Mass):
	_format = '{:2.1f}'
	_magnitude: int
	_scale: int
	_imperial: Any

	def _lbs(self):
		return self._kilogram() * 0.45359237

	def _ounces(self):
		return self._lbs() * 16

	def _milligram(self):
		return self * pow(10, self._magnitude + 2)

	def _gram(self):
		return self * pow(10, self._magnitude)

	def _kilogram(self):
		return self * pow(10, self._magnitude - 3)


class Milligram(_Metric):
	_type = 'micro'
	_format = '{:3.1f}'
	_magnitude = -2
	_scale = 1
	_unit = 'mm'


class Gram(_Metric):
	_type = 'small'
	_magnitude = 0
	_scale = 2
	_unit = 'cm'


class Kilogram(_Metric):
	_type = 'large'
	_magnitude = 3
	_scale = 4
	_unit = 'km'
