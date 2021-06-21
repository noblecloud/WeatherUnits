from .speed import Speed
from ..base import NamedType
from ..others import Direction

__all__ = ['Wind']


@NamedType
class Wind(Speed):

	# TODO: Add support for setting both speed and direction
	__direction: Direction = None


	# def __init__(self, speed: Speed = None, direction: Direction = None):
	# 	if direction is not None:
	# 		self.__direction = direction
	# 	if
	# 	super(Wind, self).__init__(Speed)

	@property
	def direction(self):
		return self.__direction

	@direction.setter
	def direction(self, value):
		if isinstance(value, Direction):
			self.__direction |= value
		else:
			self.__direction = value
