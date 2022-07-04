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
