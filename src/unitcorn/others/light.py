from datetime import timedelta

from ..base.Decorators import UnitType
from ..base import Index, Measurement

__all__ = ['Light', 'PPFD', 'DLI']


@UnitType
class Light(Measurement):
	_dimension = 'J'
	UVI: type
	Illuminance: type
	Irradiance: type
	RadiantFlux: type
	PPFD: type
	DLI: type
	Lux: type
	Brightness: type


class UVI(Index, Light, alias='UVI Index'):
	_id = 'uvi'
	_digit_budget = 2


class Irradiance(Light):
	_unit = 'W/m²'

	@property
	def lux(self) -> 'Illuminance':
		"""Peter Michael, September 20, 2019, "A Conversion Guide: Solar Irradiance and Lux Illuminance ", IEEE Dataport, doi: https://dx.doi.org/10.21227/mxr7-p365."""
		return Illuminance(float(self)*120)


def _hours(photoperiod) -> float:
	"""A photoperiod as hours: a number of hours, a `Time`, or a `timedelta`."""
	if isinstance(photoperiod, timedelta):
		return photoperiod.total_seconds() / 3600
	from ..time_ import Time
	if isinstance(photoperiod, Time):
		return float(Time.Hour(photoperiod))
	return float(photoperiod)


class _OwnQuantity:
	"""A light quantity that adds and compares with itself only.

	`Light` is one family, so a `PPFD` would otherwise add to a `DLI` or an `Irradiance` as a bare
	number: a rate and the total it makes would silently sum.
	"""

	def _sameDimension(self, other) -> bool:
		return isinstance(other, type(self))


class PPFD(_OwnQuantity, Light, alias=('PPFD', 'umol/m2/s', 'μmol/m²/s'), fullName='Photosynthetic Photon Flux Density'):
	"""Photosynthetic photon flux density: moles of photons in 400-700 nm per square metre per second.

	An instantaneous rate; the day's total is a `DLI`. Written µmol/m²/s, and read as
	``umol/m2/s`` or ``PPFD`` too.
	"""
	_unit = 'µmol/m²/s'
	_precision = 1
	_digit_budget = 4
	# Full sun is about 2000: that reads as 2000, not 2k.
	_shorten = False

	def dli(self, photoperiod) -> 'DLI':
		"""The daily light integral of holding this PPFD for ``photoperiod``.

		``photoperiod`` is hours (a number), a `Time` or a `timedelta`, at most 24 hours.
		Exactly ``PPFD × 3600 × hours / 1e6``: 500 µmol/m²/s for 16 h is 28.8 mol/m²/d.
		"""
		hours = _hours(photoperiod)
		if not 0 <= hours <= 24:
			raise ValueError(f'a photoperiod is between 0 and 24 hours a day, not {hours:g}')
		return DLI(float(self) * 3600 * hours / 1e6)


class DLI(_OwnQuantity, Light, alias=('DLI', 'mol/m2/d', 'mol/m²/day'), fullName='Daily Light Integral'):
	"""Daily light integral: moles of photons per square metre accumulated over a day.

	The accumulation that goes with the `PPFD` rate; the two share a number only by
	accident, so the class says which one a value is. Also read as ``mol/m2/d`` or ``DLI``.
	"""
	_unit = 'mol/m²/d'
	_precision = 1
	_digit_budget = 4

	def ppfd(self, photoperiod) -> PPFD:
		"""The steady PPFD that gives this DLI over ``photoperiod`` (hours, a `Time` or a `timedelta`, above 0 and at most 24 hours)."""
		hours = _hours(photoperiod)
		if not 0 < hours <= 24:
			raise ValueError(f'a photoperiod is above 0 and at most 24 hours a day, not {hours:g}')
		return PPFD(float(self) * 1e6 / (3600 * hours))


class Illuminance(Light):
	_unit = 'lux'

	@property
	def wpm2(self) -> Irradiance:
		"""Peter Michael, September 20, 2019, "A Conversion Guide: Solar Irradiance and Lux Illuminance ", IEEE Dataport, doi: https://dx.doi.org/10.21227/mxr7-p365."""
		return Irradiance(float(self)/120)

	def ppfd(self, factor: float) -> PPFD:
		"""An approximate PPFD, with the spectrum factor given explicitly.

		Lux weights light by the eye and PPFD counts photons of every colour from 400 to 700 nm,
		so there is no single conversion: ``factor`` is the µmol/m²/s per **klux** of *your* source
		and there is deliberately no default. Daylight is about 18.5 (Thimijan and Heins 1983,
		0.0185 µmol/m²/s per lux); lamps differ, and each type has its own figure. Use a quantum
		sensor where it matters.
		"""
		return PPFD(float(self) / 1000 * float(factor))


RadiantFlux = Irradiance
Lux = Illuminance
Brightness = Illuminance

Light.UVI = UVI
Light.Illuminance = Illuminance
Light.Irradiance = Irradiance
Light.PPFD = PPFD
Light.DLI = DLI

Light.RadiantFlux = Irradiance
Light.Lux = Illuminance
Light.Brightness = Illuminance
