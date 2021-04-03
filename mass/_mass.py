from units import Callable

from units._unit import Measurement


class _Mass(Measurement):
	_type = 'mass'

	_milligram: Callable
	_gram: Callable
	_kilogram: Callable
	_ounce: Callable
	_pound: Callable

	def __str__(self) -> str:
		return self.formatString.format(self).rstrip('0').rstrip('.')

	@property
	def mg(self):
		from units.mass import Milligram
		return Milligram(self._milligram())

	@property
	def g(self):
		from units.mass import Gram
		return Gram(self._gram())

	@property
	def kg(self):
		from units.mass import Kilogram
		return Kilogram(self._kilogram())

	@property
	def oz(self):
		from units.mass import Ounce
		return Ounce(self._ounce())

	@property
	def lbs(self):
		from units.mass import Pound
		return Pound(self._pound())
