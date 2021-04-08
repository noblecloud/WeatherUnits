from typing import Callable

from .._unit import Measurement


class _Heat(Measurement):
	_type = 'heat'
	_decorator = 'º'
	_suffix = ''
	_unitFormat: str = '{decorated}{unit}'

	_celsius: Callable
	_fahrenheit: Callable
	_kelvin: Callable

	@property
	def f(self):
		from ..heat import Fahrenheit
		return Fahrenheit(self._fahrenheit())

	@property
	def kel(self):
		from ..heat import Kelvin
		return Kelvin(self._kelvin())

	@property
	def fDelta(self):
		from ..heat import Fahrenheit
		return Fahrenheit(self._fahrenheit(delta=True))

	@property
	def c(self):
		from ..heat import Celsius
		return Celsius(self._celsius())

	@property
	def cDelta(self):
		from ..heat import Celsius
		return Celsius(self._celsius(delta=True))
