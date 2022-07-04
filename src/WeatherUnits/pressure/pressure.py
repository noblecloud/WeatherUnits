from enum import Enum

from ..base.Decorators import UnitType, Tiny, Small, Medium, Large, Huge, Synonym
from ..base import both, Scale, ScalingMeasurement, SystemVariant


@UnitType
class Pressure(ScalingMeasurement, baseUnit='Pascal', system=both):
	Pascal: type
	Decapascal: type
	Hectopascal: type
	Kilopascal: type
	Gigapascal: type
	Atmosphere: type
	TechnicalAtmosphere: type
	PoundsPerSquareInch: type
	MillimeterOfMercury: type
	InchOfMercury: type
	Bar: type
	Kilopascal: type
	Millibar: type
	PoundsPerSquareInch: type

	class Trend(Enum):
		Falling = -1
		Steady = 0
		Rising = 1

	class _Scale(Scale):
		Pascal = 1
		Decapascal = 10
		Hectopascal = 10
		Kilopascal = 10
		Megapascal = 1000
		Gigapascal = 1000
		Base = 'Pascal'
		Bar = 1000.
		Atmosphere = 101325.
		TechnicalAtmosphere = 98066.5
		PoundsPerSquareInch = 6894.757293168
		MillimeterOfMercury = 1 / 0.00750062
		InchOfMercury = 1 / 0.00029530

	@property
	def pascal(self):
		return Pascal(self)

	@property
	def decapascal(self):
		return Decapascal(self)

	@property
	def hectopascal(self):
		return Hectopascal(self)

	@property
	def kilopascal(self):
		return Kilopascal(self)

	@property
	def megapascal(self):
		return Megapascal(self)

	@property
	def gigapascal(self):
		return Gigapascal(self)

	@property
	def bar(self):
		return Bar(self)

	@property
	def millimeterOfMercury(self):
		return MillimeterOfMercury(self)

	@property
	def inchOfMercury(self):
		return InchOfMercury(self)

	@property
	def atmosphere(self):
		return Atmosphere(self)

	@property
	def technicalAtmosphere(self):
		return TechnicalAtmosphere(self)

	@property
	def poundsPerSquareInch(self):
		return PoundsPerSquareInch(self)

	@property
	def millibar(self):
		return Millibar(self)


@Tiny
class Pascal(Pressure):
	_unit = 'Pa'


@Small
class Decapascal(Pressure):
	_unit = 'daPa'


@Medium
class Hectopascal(Pressure):
	_unit = 'hPa'


@Large
class Kilopascal(Pressure):
	_unit = 'kPa'


@Huge
class Megapascal(Pressure):
	_unit = 'MPa'


@Huge
class Gigapascal(Pressure):
	_unit = 'GPa'


class Bar(Pascal):
	_unit = 'bar'


class MillimeterOfMercury(Pascal):
	_unit = "mmHg"


class InchOfMercury(Pascal):
	_unit = 'inHg'


class Atmosphere(Pascal):
	_unit = 'atm'


class TechnicalAtmosphere(Pascal):
	_unit = 'at'


class PoundsPerSquareInch(Pascal):
	_unit = 'psi'


@Synonym
class Millibar(Hectopascal):
	_unit = 'mBar'
	_max = 4


Pressure.Pascal = Pascal
Pressure.Decapascal = Decapascal
Pressure.Hectopascal = Hectopascal
Pressure.Kilopascal = Kilopascal
Pressure.Gigapascal = Gigapascal
Pressure.Atmosphere = Atmosphere
Pressure.Bar = Bar
Pressure.Millibar = Millibar
Pressure.InchOfMercury = InchOfMercury
Pressure.MillimeterOfMercury = MillimeterOfMercury
Pressure.Atmosphere = Atmosphere
Pressure.TechnicalAtmosphere = TechnicalAtmosphere
Pressure.PoundsPerSquareInch = PoundsPerSquareInch
Pressure.mbar = Pressure.mBar = Pressure.millibar
Pressure.psi = Pressure.poundsPerSquareInch
Pressure.at = Pressure.technicalAtmosphere
Pressure.atm = Pressure.atmosphere
Pressure.inHg = Pressure.inchOfMercury
Pressure.mmHg = Pressure.millimeterOfMercury
Pressure.gPa = Pressure.gigapascal
Pressure.kPa = Pressure.kilopascal
Pressure.hPa = Pressure.hectopascal
Pressure.p = Pressure.pascal
Pressure.dPa = Pressure.decapascal
