from .._unit import Measurement


class _Heat(Measurement):
	_type = 'heat'
	_decorator = 'º'
	_suffix = ''
	_unitFormat: str = '{value}{decorator}'

	def __repr__(self):
		return str(self)

	def __str__(self) -> str:
		return self.formatString.format(self).rstrip('0').rstrip('.')+'º'

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

	def _fahrenheit(self, delta=None):
		pass

	def _kelvin(self):
		pass

	def _celsius(self, delta=None):
		pass
