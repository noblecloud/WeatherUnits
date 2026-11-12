from ..base.Decorators import UnitType, Tiny, Small, Medium, Large, Huge
from ..base import both, Scale, ScalingMeasurement

__all__ = ['Area']


@UnitType
class Area(ScalingMeasurement, baseUnit='SquareMeter', system=both):
	SquareMeter: type
	SquareCentimeter: type
	SquareKilometer: type
	Hectare: type
	SquareInch: type
	SquareFoot: type
	SquareMile: type
	Acre: type

	class _Scale(Scale):
		SquareMeter = 1
		Base = 'SquareMeter'
		# Variants are given as their size in square metres.
		SquareCentimeter = 1e-4
		SquareKilometer = 1e6
		Hectare = 1e4
		SquareInch = 0.00064516
		SquareFoot = 0.09290304
		SquareMile = 2589988.110336
		Acre = 4046.8564224

	@property
	def squareMeter(self):
		return SquareMeter(self)

	@property
	def squareCentimeter(self):
		return SquareCentimeter(self)

	@property
	def squareKilometer(self):
		return SquareKilometer(self)

	@property
	def hectare(self):
		return Hectare(self)

	@property
	def squareInch(self):
		return SquareInch(self)

	@property
	def squareFoot(self):
		return SquareFoot(self)

	@property
	def squareMile(self):
		return SquareMile(self)

	@property
	def acre(self):
		return Acre(self)


@Medium
class SquareMeter(Area):
	_unit = 'm²'


class SquareCentimeter(Area):
	_unit = 'cm²'


class SquareKilometer(Area):
	_unit = 'km²'


class Hectare(Area):
	_unit = 'ha'


class SquareInch(Area):
	_unit = 'in²'


class SquareFoot(Area):
	_unit = 'ft²'


class SquareMile(Area):
	_unit = 'mi²'


class Acre(Area):
	_unit = 'ac'


Area.SquareMeter = SquareMeter
Area.SquareCentimeter = SquareCentimeter
Area.SquareKilometer = SquareKilometer
Area.Hectare = Hectare
Area.SquareInch = SquareInch
Area.SquareFoot = SquareFoot
Area.SquareMile = SquareMile
Area.Acre = Acre
