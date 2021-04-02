from .._unit import Measurement
from ..length._length import _Length


class Volume(Measurement):
	_x: _Length
	_y: _Length
	_z: _Length
	_cube: bool

	def __init__(self, x: _Length, y: _Length = 1, z: _Length = 1, cube: bool = True):
		unitClass = x.__class__
		if cube:
			x = unitClass(x**(1./3.))
			y = x
			z = x
		self._cube = cube
		self._x: _Length = x
		self._y: _Length = y
		self._z: _Length = z
		float.__init__(x * y * z)

	def __new__(cls, x: _Length, y: _Length = 1, z: _Length = 1, cube: bool = False):
		if cube:
			y = x
			z = x
		value = x * y * z
		return float.__new__(cls, value)

	@property
	def width(self) -> _Length:
		return self._x

	@property
	def length(self) -> _Length:
		return self._y

	@property
	def depth(self) -> _Length:
		return self._z

