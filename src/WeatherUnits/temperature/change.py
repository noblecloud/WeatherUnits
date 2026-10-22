"""A change in temperature, as distinct from a temperature reading.

``Celsius(30) - Celsius(20)`` is a change of 10 °C, which is also a change of
18 °F, so a change converts by a factor and never by an offset. Adding a change
to a reading gives a reading: ``Fahrenheit(68) + CelsiusChange(10)`` is 86 °F.
"""
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Type

from ..base import Measurement
from ..utils import Self

__all__ = ['TemperatureChange', 'CelsiusChange', 'FahrenheitChange', 'KelvinChange', 'summingReadings']

_summing: ContextVar[bool] = ContextVar('WeatherUnits.summingReadings', default=False)


@contextmanager
def summingReadings():
	"""Let ``reading + reading`` add, in the left operand's unit.

	Off by default: 20 °C + 10 °C is 30 °C, but 68 °F + 50 °F is 118 °F, which is not 86 °F.
	"""
	token = _summing.set(True)
	try:
		yield
	finally:
		_summing.reset(token)


def readingsMaySum() -> bool:
	return _summing.get()


class TemperatureChange(Measurement):
	"""A difference between two temperatures, in one of the three scales' degrees."""
	#: Kelvin per degree of this unit.
	_factor: float = 1.0
	_unit_symbol = '°'
	_show_unit = False
	_id = 'Δ°t'
	_reading: Type[Measurement]

	def __new__(cls, value=0.0, *args, **kwargs):
		if isinstance(value, TemperatureChange) and type(value) is not cls:
			value = float(value) * value._factor / cls._factor
		return Measurement.__new__(cls, value, *args, **kwargs)

	@property
	def kelvin(self) -> 'KelvinChange':
		return KelvinChange(self)

	@property
	def celsius(self) -> 'CelsiusChange':
		return CelsiusChange(self)

	@property
	def fahrenheit(self) -> 'FahrenheitChange':
		return FahrenheitChange(self)

	k = kelvin
	c = celsius
	f = fahrenheit

	def __getitem__(self, item):
		key = str(item).lstrip('Δ°').lower()
		for cls in (CelsiusChange, FahrenheitChange, KelvinChange):
			if key in (cls._unit.lstrip('Δ°').lower(), cls.__name__.lower().replace('change', '')):
				return cls(self)
		return super().__getitem__(item)

	def _kelvins(self) -> float:
		return float(self) * self._factor

	def _operand(self, other) -> float:
		"""`other` as a number of this unit's degrees. A bare number is already in them."""
		if isinstance(other, TemperatureChange):
			return other._kelvins() / self._factor
		if isinstance(other, Measurement):
			raise TypeError(f'a change in temperature does not combine with {type(other).__name__}')
		return float(other)

	def __add__(self, other):
		from .temperature import Temperature
		if isinstance(other, Temperature):
			return other + self
		return type(self)(float(self) + self._operand(other))

	__radd__ = __add__

	def __sub__(self, other):
		return type(self)(float(self) - self._operand(other))

	def __rsub__(self, other):
		return type(self)(self._operand(other) - float(self))

	def __mul__(self, other):
		if isinstance(other, Measurement):
			return super().__mul__(other)
		return type(self)(float(self) * float(other))

	def __rmul__(self, other):
		return self.__mul__(other)

	def __truediv__(self, other):
		if isinstance(other, TemperatureChange):
			return self._kelvins() / other._kelvins()
		if isinstance(other, Measurement):
			return super().__truediv__(other)
		return type(self)(float(self) / float(other))

	def __neg__(self):
		return type(self)(-float(self))

	def __pos__(self):
		return type(self)(float(self))

	def __abs__(self):
		return type(self)(abs(float(self)))

	def __eq__(self, other):
		try:
			return abs(float(self) - self._operand(other)) < 1e-9
		except (TypeError, ValueError):
			return False

	def __lt__(self, other):
		return float(self) < self._operand(other)

	def __le__(self, other):
		return float(self) <= self._operand(other)

	def __gt__(self, other):
		return float(self) > self._operand(other)

	def __ge__(self, other):
		return float(self) >= self._operand(other)

	def __hash__(self):
		return hash(round(self._kelvins(), 9))


class CelsiusChange(TemperatureChange):
	_unit = 'Δ°c'
	_factor = 1.0


class FahrenheitChange(TemperatureChange):
	_unit = 'Δ°f'
	_factor = 5 / 9


class KelvinChange(TemperatureChange):
	_unit = 'Δk'
	_factor = 1.0
