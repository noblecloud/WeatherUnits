from ..base.Decorators import UnitType, Tiny, Small, Medium, Large, Huge
from ..base import both, Scale, ScalingMeasurement

__all__ = ['Power']


@UnitType
class Power(ScalingMeasurement, baseUnit='Watt', system=both):
	Watt: type
	Kilowatt: type
	Megawatt: type
	Gigawatt: type
	Horsepower: type
	BritishThermalUnitPerHour: type

	class _Scale(Scale):
		Watt = 1
		Kilowatt = 1000
		Megawatt = 1000
		Gigawatt = 1000
		Base = 'Watt'
		# Variants are given as their size in watts.
		Horsepower = 745.69987158227
		BritishThermalUnitPerHour = 0.29307107

	@property
	def watt(self):
		return Watt(self)

	@property
	def kilowatt(self):
		return Kilowatt(self)

	@property
	def megawatt(self):
		return Megawatt(self)

	@property
	def gigawatt(self):
		return Gigawatt(self)

	@property
	def horsepower(self):
		return Horsepower(self)


@Tiny
class Watt(Power):
	_unit = 'W'


@Small
class Kilowatt(Power):
	_unit = 'kW'


@Medium
class Megawatt(Power):
	_unit = 'MW'


@Large
class Gigawatt(Power):
	_unit = 'GW'


class Horsepower(Power):
	_unit = 'hp'


class BritishThermalUnitPerHour(Power):
	_unit = 'BTU/h'


Power.Watt = Watt
Power.Kilowatt = Kilowatt
Power.Megawatt = Megawatt
Power.Gigawatt = Gigawatt
Power.Horsepower = Horsepower
Power.BritishThermalUnitPerHour = BritishThermalUnitPerHour
Power.W = Power.watt
Power.kW = Power.kilowatt
Power.MW = Power.megawatt
