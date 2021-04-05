from . import Mass, Gram, Kilogram
from .._unit import AbnormalScale


class _Imperial(Mass, AbnormalScale):
	# 0 base, 1 line, 2 inch, 3 foot, 4 yard
	_factors = [1.0, 16.0, 1.0]
	_format = '{:2.2f}'
	_metric: Kilogram
	_scale: int

	def _ounce(self):
		return self.changeScale(0)

	def _pound(self):
		return self.changeScale(1)

	def _milligram(self):
		return self._metric.mg

	def _gram(self):
		return self._metric.g

	def _kilogram(self):
		return self._metric.kg


class Ounce(_Imperial):
	_type = 'small'
	_format = '{:2.2f}'
	_scale = 0
	_metric: Gram
	_unit = 'oz'

	def __init__(self, value):
		super().__init__(value)
		self._metric = Gram(value * 28.349523125)


class Pound(_Imperial):
	_type = 'medium'
	_scale = 1
	_metric: Kilogram
	_unit = 'lbs'

	def __init__(self, value):
		super().__init__(value)
		self._metric = Kilogram(value * 0.45359237)
