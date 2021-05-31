from .._unit import Measurement


class Humidity(Measurement):
	_type = 'concentration'
	_format = "{:2d}"
	_unit = ''
	_decorator = '%'


class MultiUnit(Measurement):
	_type = 'base'
	_numerator: Measurement
	_denominator: Measurement

	def __new__(cls, numerator, denominator):
		value = numerator / denominator
		return Measurement.__new__(cls, value)

	def __init__(self, numerator, denominator):
		self._numerator = numerator
		self._denominator = denominator
		Measurement.__init__(self, self._numerator / self._denominator)
