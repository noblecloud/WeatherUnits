import logging

from units._unit import Measurement


class _Derived(Measurement):
	_type = 'derived'
	_numerator: Measurement
	_denominator: Measurement

	def __new__(cls, numerator, denominator):
		value = numerator / denominator
		return Measurement.__new__(cls, value)

	def __init__(self, numerator, denominator):
		self._numerator = numerator
		self._denominator = denominator
		Measurement.__init__(self, self._numerator / self._denominator)

	@property
	def localized(self):
		try:
			newClass = self.__class__
			n, d = self._config['Units'][self._type.lower()].split(',')
			n = 'inch' if n == 'in' else n
			return newClass(self._numerator[n], self._denominator[d])
		except KeyError:
			logging.error('Measurement {} was unable to localize from {}'.format(self.name, self.unit))
			return self

	@property
	def unit(self):
		if self._suffix:
			return self._suffix
		elif self._numerator.unit == 'mi' and self._denominator.unit == 'hr':
			return 'mph'
		else:
			return '{}/{}'.format(self._numerator.unit, self._denominator.unit)

	@property
	def numerator(self):
		return self._numerator

	@property
	def denominator(self):
		return self._denominator


from ._wind import Wind
from ._precipitation import Precipitation
from ._volume import Volume, CubicFoot, CubicMeter
from ._density import Density
