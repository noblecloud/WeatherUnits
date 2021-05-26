from typing import Callable
from .._unit import Measurement


class _Mass(Measurement):
	_type = 'mass'

	_milligram: Callable
	_gram: Callable
	_kilogram: Callable
	_ounce: Callable
	_pound: Callable

	@property
	def milligram(self):
		from . import Milligram
		return Milligram(self._milligram())

	@property
	def gram(self):
		from . import Gram
		return Gram(self._gram())

	@property
	def kilogram(self):
		from . import Kilogram
		return Kilogram(self._kilogram())

	@property
	def ounce(self):
		from . import Ounce
		return Ounce(self._ounce())

	@property
	def pound(self):
		from . import Pound
		return Pound(self._pound())

	mg = milligram
	g = gram
	kg = kilogram
	oz = ounce
	lbs = pound

