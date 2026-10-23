from ..base.Decorators import UnitType
from . import Length, Time, DistanceOverTime, Direction

__all__ = ['Wind']


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
Wind.MetersPerSecond = MetersPerSecond
Wind.MetersPerHour = MetersPerSecond
