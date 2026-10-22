from typing import Union

from ..base.Decorators import UnitType
from . import Measurement, Length

__all__ = ['Volume']


@UnitType
class Volume(Measurement):
	CubicFoot: type
	CubicMeter: type

	_x: Length
	_y: Length
	_z: Length
	_unitClass = Length
	_cube: bool

	def __init__(self, x: Union[Length, int, float], y: Union[Length, int, float] = None, z: Union[Length, int, float] = None):
		if isinstance(x, Volume):
			y = x.y
			z = x.z
			x = x.x
		if not (y and z):
			x = float(x)
			x **= 1./3.
			y = x
			z = x
		self._x = self._unitClass(x)
		self._y = self._unitClass(y)
		self._z = self._unitClass(z)
		float.__init__(x*y*z)

	def __new__(cls, x: Length, y: Length = None, z: Length = None):
		if isinstance(x, Volume):
			y = x.y
			z = x.z
			x = x.x
		if not (y and z):
			x = float(x)
			x **= 1./3.
			y = x
			z = x
		x = cls._unitClass(x)
		y = cls._unitClass(y)
		z = cls._unitClass(z)
		value = float(x)*float(y)*float(z)
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

	@property
	def x(self):
		return self._x

	@property
	def y(self):
		return self._y

	@property
	def z(self):
		return self._z

# class CubicMeter(Volume, Length.Meter, unit='m³', aliases=('m3', 'm^3', 'm'), dimension=(Length, Length, Length)):
# 	_x: Length.Meter
# 	_y: Length.Meter
# 	_z: Length.Meter
# 	_unitClass = Length.Meter
#
# 	@property
# 	def ft(self):
# 		x = self._x.ft
# 		y = self._y.ft
# 		z = self._z.ft
# 		return CubicFoot(x, y, z)
#
# 	@property
# 	def m(self):
# 		return self
#
#
# class CubicFoot(Volume, Length.Foot, unit='ft³', aliases=('ft3', 'ft^3', 'ft'), dimension=(Length, Length, Length)):
# 	_x: Length.Foot
# 	_y: Length.Foot
# 	_z: Length.Foot
# 	_unitClass = Length.Foot
#
# 	@property
# 	def ft(self):
# 		return self
#
# 	@property
# 	def m(self):
# 		x = self._x.m
# 		y = self._y.m
# 		z = self._z.m
# 		return CubicMeter(x, y, z)
#
#
# Volume.CubicMeter = CubicMeter
# Volume.CubicFoot = CubicFoot
