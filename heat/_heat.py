from units._unit import Measurement


class _Heat(Measurement):
	_type = 'heat'
	_decorator = 'º'
	_suffix = 'º'

	def __repr__(self):
		return str(self)

	def __str__(self) -> str:
		return self.formatString.format(self).rstrip('0').rstrip('.')+'º'

	@property
	def f(self):
		from units.heat import Fahrenheit
		return Fahrenheit(self._fahrenheit())

	@property
	def kel(self):
		from units.heat import Kelvin
		return Kelvin(self._kelvin())

	@property
	def fDelta(self):
		from units.heat import Fahrenheit
		return Fahrenheit(self._fahrenheit(delta=True))

	@property
	def c(self):
		from units.heat import Celsius
		return Celsius(self._celsius())

	@property
	def cDelta(self):
		from units.heat import Celsius
		return Celsius(self._celsius(delta=True))
