from typing import Union

from ..base.Decorators import NamedType
from ..base.Measurement import Measurement
from ..length import Length

__all__ = ['Volume']


@NamedType
class Volume(Measurement):

	CubicFoot: type
	CubicMeter: type

	_x: Length
	_y: Length
	_z: Length
	_unitClass = Length
	_cube: bool

	def __init__(self, x: Union[Length, int, float], y: Union[Length, int, float] = 0, z: Union[Length, int, float] = 0, cube: bool = True):
		if cube and not (z and y):
			x **= 1. / 3.
			y = x
			z = x
		self._cube = cube
		self._x: Length = self._unitClass(x)
		self._y: Length = self._unitClass(y)
		self._z: Length = self._unitClass(z)
		float.__init__(x * y * z)

	def __new__(cls, x: Length, y: Length = 1, z: Length = 1, cube: bool = False):
		if cube and not (z and y):
			y = x
			z = x
		value = x * y * z
		return float.__new__(cls, value)

	@property
	def width(self) -> Length:
		return self._x

	@property
	def length(self) -> Length:
		return self._y

	@property
	def depth(self) -> Length:
		return self._z

	@property
	def unit(self) -> str:
		return self._x.unit + "³"

	def scale(self, value: float):
		x = self._x * value
		y = self._y * value
		z = self._z * value
		return x, y, z


class CubicMeter(Volume):
	_x: Length.Meter
	_y: Length.Meter
	_z: Length.Meter
	_unitClass = Length.Meter

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
	_x: Length.Foot
	_y: Length.Foot
	_z: Length.Foot
	_unitClass = Length.Foot

	@property
	def ft(self):
		return self

	@property
	def m(self):
		x = self._x.m
		y = self._y.m
		z = self._z.m
		return CubicMeter(x, y, z)


Volume.CubicMeter = CubicMeter
Volume.CubicFoot = CubicFoot
