from math import isclose, isnan, nan

from ..base.Decorators import UnitType
from ..base import Index
from . import Length, Time, DistanceOverTime, Direction, DerivedMeasurement

__all__ = ['Wind', 'Beaufort']


@UnitType
class Wind(DistanceOverTime):
	# TODO: Add support for setting both speed and direction
	__direction: Direction = None

	@property
	def direction(self):
		return self.__direction

	@direction.setter
	def direction(self, value):
		if not isinstance(value, Direction) and isinstance(value, (float, int)):
			value = Direction(value)
		self.__direction = value


class PerSecond(Wind, DistanceOverTime.PerSecond):
	...


class PerMinute(Wind, DistanceOverTime.PerMinute):
	...


class PerHour(Wind, DistanceOverTime.PerHour):
	...


class MilesPerHour(Wind, DistanceOverTime.MilesPerHour):
	...


class MetersPerSecond(Wind, DistanceOverTime.MetersPerSecond):
	...


class Knot(Wind, DistanceOverTime.Knot):
	...


# Attach the concrete units to Wind, the same way rate.py attaches its own.
# Without this, `Wind.MilesPerHour` resolves by ordinary inheritance to
# DistanceOverTime's class, whose type is 'Distance Over Time' rather than
# 'Wind'. Localization looks the unit type up in the config by that name, so
# it found no `wind` key, returned None, and every wind reading stayed in its
# source unit - a `wind = mph` config still displayed m/s.
Wind.PerSecond = PerSecond
Wind.PerMinute = PerMinute
Wind.PerHour = PerHour
Wind.MilesPerHour = MilesPerHour
Wind.Knot = Knot
Wind.MetersPerSecond = MetersPerSecond
Wind.MetersPerHour = MetersPerSecond


class Beaufort(Index, limits=(0, 12), alias=('Bft', 'Beaufort')):
	"""Wind force on the Beaufort scale, 0 (calm) to 12 (hurricane force). Shown as ``4 Bft``.

	The scale is not linear, so it is not a unit of ``Wind`` and speeds do not convert to it
	by a factor. It is an ``Index``: a whole-number force, with an explicit way in and out.

	``Beaufort.from_speed(speed)`` reads a speed in any unit (a plain number is m/s) against
	the WMO table. The upper bound of each band belongs to that band, so 0.5 m/s is force 0
	and 0.51 m/s is force 1; bounds are compared to a relative 1e-9, so ``5.4 km/h`` (1.5 m/s
	after float noise) is still force 1.

	The upper bounds in m/s are 0.5, 1.5, 3.3, 5.5, 7.9, 10.7, 13.8, 17.1, 20.7, 24.4, 28.4 and
	32.6 for forces 0 to 11; anything faster is force 12.

	``.speed`` goes back the other way and gives the **midpoint** of the band, in m/s, as a
	``Wind.MetersPerSecond`` (force 4 is 5.5 to 7.9, so 6.7 m/s). That is a representative
	speed, not the speed the force came from; the original is gone. Force 0 has no lower
	bound below zero, so its midpoint is 0.25 m/s. Force 12 has no upper bound, so its
	midpoint is taken as its lower edge plus half the width of force 11 (34.7 m/s). A force
	that is not whole is rounded to the nearest one first.
	"""
	_unit = 'Bft'
	_unit_spacer = True
	_id = 'bft'
	_digit_budget = 2
	_precision = 0

	# Upper bound of forces 0 to 11, m/s (WMO). Force 12 starts above the last one.
	_bounds = (0.5, 1.5, 3.3, 5.5, 7.9, 10.7, 13.8, 17.1, 20.7, 24.4, 28.4, 32.6)

	def __new__(cls, value, *args, **kwargs):
		if isinstance(value, DerivedMeasurement):
			raise TypeError('a Beaufort force is not a factor away from a speed: use Beaufort.from_speed(speed)')
		return super().__new__(cls, value, *args, **kwargs)

	@property
	def unit(self) -> str:
		return self._unit

	@classmethod
	def from_speed(cls, speed) -> 'Beaufort':
		"""The force of ``speed``: a speed measurement in any unit, or a number in m/s."""
		ms = float(MetersPerSecond(speed)) if isinstance(speed, DerivedMeasurement) else float(speed)
		if isnan(ms):
			return cls(nan)
		for force, bound in enumerate(cls._bounds):
			if ms <= bound or isclose(ms, bound, rel_tol=1e-9):
				return cls(force)
		return cls(12)

	@property
	def speed(self) -> 'Wind':
		"""The midpoint of this force's band, as m/s; see the class docstring."""
		value = float(self)
		if isnan(value):
			return MetersPerSecond(nan)
		force = min(max(round(value), 0), 12)
		bounds = (0.0, *self._bounds)
		lower = bounds[force]
		upper = self._bounds[force] if force < 12 else lower + (self._bounds[11] - self._bounds[10])
		return MetersPerSecond((lower + upper) / 2)


Wind.Beaufort = Beaufort
