from math import log as _log
from typing import Callable

from .._unit import Measurement


class _Temperature(Measurement):
	_type = 'heat'
	_decorator = 'º'
	_unitFormat: str = '{decorated}{unit}'

	_celsius: Callable
	_fahrenheit: Callable
	_kelvin: Callable

	@property
	def celsius(self):
		from ..temperature import Celsius
		return Celsius(self._celsius())

	@property
	def fahrenheit(self):
		from ..temperature import Fahrenheit
		return Fahrenheit(self._fahrenheit())

	@property
	def kelvin(self):
		from ..temperature import Kelvin
		return Kelvin(self._kelvin())

	@property
	def fDelta(self):
		from ..temperature import Fahrenheit
		return Fahrenheit(self._fahrenheit(delta=True))

	@property
	def cDelta(self):
		from ..temperature import Celsius
		return Celsius(self._celsius(delta=True))

	def dewpoint(self, rh: float):
		from ..temperature import Celsius

		# Keep rh within reasonable ranges
		rh = self.normalizeRh(rh)

		a, b = 17.27, 237.7
		n = ((a * self.c) / (b + self.c)) + _log(rh / 100.0)
		value = (b * n) / (a - n)
		return Celsius(round(value, self._precision))[self._unit]

	def heatIndex(self, rh: float):

		if self._unit == 'c':
			c = [-8.78469475556, 1.61139411, 2.33854883889, -0.14611605, -0.012308094, -0.0164248277778, 0.002211732, 0.00072546, -0.000003582]
		elif self._unit == 'f':
			c = [-42.379, 2.04901523, 10.14333427, -0.22477541, -0.00683783, -0.05481717, 0.00122874, 0.00085282, -0.00000199]
		else:
			c = [-8.78469475556, 1.61139411, 2.33854883889, -0.14611605, -0.012308094, -0.0164248277778, 0.002211732, 0.00072546, -0.000003582]

		T = self if self._unit != 'k' else self.c
		T2 = T ^ 2
		R = self.normalizeRh(rh)
		R2 = R ^ 2

		hi = c[0] + (c[1] * T) + (c[2] * R) + (c[3] * T * R) + (c[4] * T2) + (c[5] * R2) + (c[6] * T2 * R) + (c[7] * T * R2) + (c[8] * T2 * R2)

		hi = hi if self._unit != 'k' else hi + 273.15

		return self.__class__(round(hi, self._precision))

	def windChill(self, wind):
		if self._unit == 'c':
			v = wind.kmh
			value = 13.12 + (0.6215 * self) - (11.37 * v ^ 0.16) + (0.3965 * self * v ^ 0.16)
		elif self._unit == 'f':
			v = wind.mih
			value = 35.74 + (0.6215 * self) - (35.75 * v ^ 0.16) + (0.4275 * self * v ^ 0.16)
		else:
			v = wind.kmh
			T = self.c
			value = (13.12 + (0.6215 * T) - (11.37 * v ^ 0.16) + (0.3965 * T * v ^ 0.16)) + 273.15

		return self.__class__(round(value, self._precision))

	@staticmethod
	def normalizeRh(rh):
		if 1 > rh > 0:
			rh *= 100
		rh = min(100, max(rh, 0))
		return rh

	# abbreviations
	c = celsius
	k = kelvin
	kel = kelvin
	f = fahrenheit
