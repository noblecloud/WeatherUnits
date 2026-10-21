from ..base.Decorators import UnitType, Tiny, Small, Medium, Large, Huge
from ..base import both, Scale, ScalingMeasurement

__all__ = ['Energy']


@UnitType
class Energy(ScalingMeasurement, baseUnit='Joule', system=both):
	Joule: type
	Kilojoule: type
	Megajoule: type
	Gigajoule: type
	WattHour: type
	KilowattHour: type
	MegawattHour: type
	Calorie: type
	BritishThermalUnit: type

	class _Scale(Scale):
		Joule = 1
		Kilojoule = 1000
		Megajoule = 1000
		Gigajoule = 1000
		Base = 'Joule'
		# Variants are given as their size in joules.
		WattHour = 3600.
		KilowattHour = 3.6e6
		MegawattHour = 3.6e9
		Calorie = 4.184
		BritishThermalUnit = 1055.05585262

	@property
	def joule(self):
		return Joule(self)

	@property
	def kilojoule(self):
		return Kilojoule(self)

	@property
	def megajoule(self):
		return Megajoule(self)

	@property
	def gigajoule(self):
		return Gigajoule(self)

	@property
	def wattHour(self):
		return WattHour(self)

	@property
	def kilowattHour(self):
		return KilowattHour(self)

	@property
	def megawattHour(self):
		return MegawattHour(self)

	@property
	def calorie(self):
		return Calorie(self)

	@property
	def britishThermalUnit(self):
		return BritishThermalUnit(self)


@Tiny
class Joule(Energy):
	_unit = 'J'


@Small
class Kilojoule(Energy):
	_unit = 'kJ'


@Medium
class Megajoule(Energy):
	_unit = 'MJ'


@Large
class Gigajoule(Energy):
	_unit = 'GJ'


class WattHour(Energy):
	_unit = 'Wh'


class KilowattHour(Energy):
	_unit = 'kWh'


class MegawattHour(Energy):
	_unit = 'MWh'


class Calorie(Energy):
	_unit = 'cal'


class BritishThermalUnit(Energy):
	_unit = 'BTU'


Energy.Joule = Joule
Energy.Kilojoule = Kilojoule
Energy.Megajoule = Megajoule
Energy.Gigajoule = Gigajoule
Energy.WattHour = WattHour
Energy.KilowattHour = KilowattHour
Energy.MegawattHour = MegawattHour
Energy.Calorie = Calorie
Energy.BritishThermalUnit = BritishThermalUnit
Energy.Wh = Energy.wattHour
Energy.kWh = Energy.kilowattHour
Energy.MWh = Energy.megawattHour
