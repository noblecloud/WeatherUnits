"""Vapour pressure deficit, from air temperature and relative humidity.

Plants pay attention to this rather than to humidity alone: the same 60 % RH is gentle at
15 °C and harsh at 30 °C. Saturation vapour pressure is the Tetens equation,
``es(T) = 0.6108 × exp(17.27 T / (T + 237.3))`` kPa with ``T`` in °C, and
``VPD = es × (1 − RH)``.
"""
from math import exp, isnan

from ..others import Percentage
from .pressure import Pressure

__all__ = ['vpd', 'saturationVapourPressure']


def _celsius(temperature) -> float:
	"""``temperature`` in °C: a `Temperature` in any scale, or a plain number already in °C."""
	from ..temperature import Temperature, Celsius
	if isinstance(temperature, Temperature):
		return float(Celsius(temperature))
	return float(temperature)


def _tetens(celsius: float) -> float:
	return 0.6108 * exp(17.27 * celsius / (celsius + 237.3))


def saturationVapourPressure(temperature) -> Pressure.Kilopascal:
	"""The vapour pressure of saturated air at ``temperature`` (Tetens), in kPa.

	``temperature`` is a `Temperature` in any scale, or a plain number in °C.
	"""
	return Pressure.Kilopascal(_tetens(_celsius(temperature)))


def vpd(temperature, humidity, leafOffset=0.0) -> Pressure.Kilopascal:
	"""Vapour pressure deficit in kPa, from air ``temperature`` and relative ``humidity``.

	``temperature``: a `Temperature` in any scale (Celsius, Fahrenheit, Kelvin), or a plain
	number, which is **°C**.

	``humidity``: a `Humidity` (or any `Percentage`), or a plain number, which is a **percent
	from 0 to 100**. A plain number is never guessed to be a fraction, so ``0.6`` is 0.6 %: pass
	``Humidity.fromFraction(0.6)`` for that. A value outside 0 to 100 % raises ``ValueError``.

	``leafOffset``: how far the leaf sits below the air, as a plain number of °C or a
	`TemperatureChange` (default 0, the usual air VPD). Leaves transpiring in the light run a
	degree or two cooler than the air, and the *leaf* VPD is then the leaf's saturation pressure
	(at ``temperature − leafOffset``) minus the air's actual vapour pressure
	(``es(temperature) × RH``). A negative offset is a warmer leaf.

	``vpd(25, 60)`` is 1.27 kPa.
	"""
	celsius = _celsius(temperature)
	if isinstance(humidity, Percentage):
		fraction = float(humidity)
	else:
		fraction = float(humidity) / 100
	if not isnan(fraction) and not 0 <= fraction <= 1:
		raise ValueError(f'relative humidity is between 0 and 100 %, not {fraction * 100:g} %')
	from ..temperature import TemperatureChange, CelsiusChange
	if isinstance(leafOffset, TemperatureChange):
		leafOffset = float(CelsiusChange(leafOffset))
	air = _tetens(celsius)
	value = Pressure.Kilopascal(_tetens(celsius - leafOffset) - air * fraction, title='VPD')
	# kPa shows one decimal by default; a VPD is read to the hundredth (1.27, not 1.3).
	value.precision = 2
	value.calculated = True
	return value
