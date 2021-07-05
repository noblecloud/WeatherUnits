from ..length import Length
from ..time import Time
from .rate import DistanceOverTime
from ..base import NamedType
from ..others import Direction

__all__ = ['Wind']


@NamedType
class Wind(DistanceOverTime):
	_numerator: Length
	_denominator: Time

	# TODO: Add support for setting both speed and direction
	__direction: Direction = None

	# def __init__(self, speed: DistanceOverTime = None, direction: Direction = None):
	# 	if direction is not None:
	# 		self.__direction = direction
	# 	if
	# 	super(Wind, self).__init__(DistanceOverTime)

	@property
	def direction(self):
		return self.__direction

	@direction.setter
	def direction(self, value):
		if isinstance(value, Direction):
			self.__direction |= value
		else:
			self.__direction = value
