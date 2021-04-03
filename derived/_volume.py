from typing import Union

from .._unit import Measurement
from ..length import Meter, Foot
from ..length._length import _Length


class Volume(Measurement):
	_x: _Length
	_y: _Length
	_z: _Length
	_unitClass = _Length
	_cube: bool
	_type = 'volume'

	def __init__(self, x: Union[_Length, int, float], y: Union[_Length, int, float] = 0, z: Union[_Length, int, float] = 0, cube: bool = True):
		if cube and not(z and y):
			x **= 1. / 3.
			y = x
			z = x
		self._cube = cube
		self._x: _Length = self._unitClass(x)
		self._y: _Length = self._unitClass(y)
		self._z: _Length = self._unitClass(z)
		float.__init__(x * y * z)

	def __new__(cls, x: _Length, y: _Length = 1, z: _Length = 1, cube: bool = False):
		if cube and not(z and y):
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

	@property
	def m3(self):
		return

	@property
	def unit(self) -> str:
		return self._x.unit + "³"

	def scale(self, value: float):
		x = self._x * value
		y = self._y * value
		z = self._z * value
		return x, y, z


class CubicMeter(Volume):
	_x: Meter
	_y: Meter
	_z: Meter
	_unitClass = Meter

	@property
	def ft(self):
		x = self._x.ft
		y = self._y.ft
		z = self._z.ft
		return CubicFoot(x, y, z)

	@property
	def m(self):
		return self

class CubicFoot(Volume):
	_x: Foot
	_y: Foot
	_z: Foot
	_unitClass = Foot

	@property
	def ft(self):
		return self

	@property
	def m(self):
		x = self._x.m
		y = self._y.m
		z = self._z.m
		return CubicMeter(x, y, z)
