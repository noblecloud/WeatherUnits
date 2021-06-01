from . import Mass


class _Metric(Mass):
	_format = '{:2.1f}'
	_magnitude: int
	_scale: int

	def _dram(self):
		return self._ounce() * 16

	def _ounce(self):
		return self._pound() * 16

	def _pound(self):
		return self._kilogram() * 2.2046226218

	def _milligram(self):
		return self * pow(10, self._magnitude + 2)

	def _gram(self):
		return self * pow(10, self._magnitude)

	def _kilogram(self):
		return self * pow(10, self._magnitude - 3)


class Milligram(_Metric):
	_format = '{:3.1f}'
	_magnitude = -2
	_scale = 1
	_unit = 'mg'


class Gram(_Metric):
	_magnitude = 0
	_scale = 2
	_unit = 'g'


class Kilogram(_Metric):
	_magnitude = 3
	_scale = 4
	_unit = 'kg'