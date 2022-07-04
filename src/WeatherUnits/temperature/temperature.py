from typing import Union
from math import log

from ..others import Humidity
from ..base.Decorators import UnitType
from ..base import Measurement, Dimension


@UnitType
class Temperature(Measurement, metaclass=Dimension, symbol='Θ'):
	Celsius: type
	Fahrenheit: type
	Kelvin: type

	_decorator = 'º'
	_id = 'ºt'

	def __new__(cls, value: float | int | Measurement):
		if isinstance(value, Temperature) and not isinstance(value, cls):
			value = value[cls.unit]
		return super().__new__(cls, value)

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

		# a, b = 17.27, 237.7
		# n = ((a * T) / (b + T)) + logRH
		# value = Celsius((b * n) / (a - n))

		T = float(self.c)
		logRH = log(rh/100)
		A = 243.04
		B = 17.625
		value = Celsius(A*(logRH + ((B*T)/(A + T)))/(B - logRH - ((B*T)/(A + T))))

		value = self.__class__(value[self._unit])
		value = self.transform(value)
		value.title = 'Dewpoint'
		value.calculated = True
		return self.transform(value)

	def heatIndex(self, rh: float):
		R = float(self.normalizeRh(rh))

		if 300 > self.kelvin < 318 or R < 13:
			return self

		if self._unit == 'f':
			c = [-42.379, 2.04901523, 10.14333427, -0.22477541, -0.00683783, -0.05481717, 0.00122874, 0.00085282, -0.00000199]
		else:
			c = [-8.78469475556, 1.61139411, 2.33854883889, -0.14611605, -0.012308094, -0.0164248277778, 0.002211732, 0.00072546, -0.000003582]

		T = float(self if self._unit != 'k' else self.c)
		T2 = pow(T, 2)
		R2 = pow(R, 2)

		hi = c[0] + (c[1]*T) + (c[2]*R) + (c[3]*T*R) + (c[4]*T2) + (c[5]*R2) + (c[6]*T2*R) + (c[7]*T*R2) + (c[8]*T2*R2)

		hi = hi if self._unit != 'k' else hi + 273.15
		value = self.transform(self.__class__(hi))
		value.title = 'Heat Index'
		value.calculated = True
		return value

	def windChill(self, wind: 'Wind'):
		if wind.mph < 3:
			return type(self)(self)
		if self._unit == 'f':
			w = float(wind.mih)
			t = float(self)
			value = 35.74 + (0.6215*t) - (35.75*pow(w, 0.16)) + (0.4275*t*pow(w, 0.16))
		else:
			w = float(wind.kmh)
			t = float(self.c)
			value = 13.12 + (0.6215*t) - (11.37*pow(w, 0.16)) + (0.3965*t*pow(w, 0.16))

		value = self.transform(self.__class__(round(value, self._precision)))
		value.title = 'Wind Chill'
		value.calculated = True
		return value

	@staticmethod
	def normalizeRh(rh: Union[int, float, 'Humidity']):
		if not isinstance(rh, Humidity):
			rh = Humidity(rh)
		return int(rh)

	def _convert(self, value: Measurement):
		if isinstance(value, Measurement):
			return value[self.unit]
		return value[self.unit]

	# abbreviations
	c = celsius
	k = kelvin
	kel = kelvin
	f = fahrenheit
