from ..base import NamedType, synonym
from ..base import MeasurementSystem as _MeasurementSystem
from ..base import BaseUnit, Huge, Large, Medium, Small, SystemVariant, Tiny, UnitSystem
from ..utils import ScaleMeta as _ScaleMeta
from enum import Enum

__all__ = ['Pressure']


@NamedType
@UnitSystem
class Pressure(_MeasurementSystem):
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

	class _Scale(_ScaleMeta):
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
	p = pascal

	@property
	def decapascal(self):
		return Decapascal(self)
	dPa = decapascal

	@property
	def hectopascal(self):
		return Hectopascal(self)
	hPa = hectopascal

	@property
	def kilopascal(self):
		return Kilopascal(self)
	kPa = kilopascal

	@property
	def megapascal(self):
		return Megapascal(self)

	@property
	def gigapascal(self):
		return Gigapascal(self)
	gPa = gigapascal

	@property
	def bar(self):
		return Bar(self)

	@property
	def millimeterOfMercury(self):
		return MillimeterOfMercury(self)
	mmHg = millimeterOfMercury

	@property
	def inchOfMercury(self):
		return InchOfMercury(self)
	inHg = inchOfMercury

	@property
	def atmosphere(self):
		return Atmosphere(self)
	atm = atmosphere

	@property
	def technicalAtmosphere(self):
		return TechnicalAtmosphere(self)
	at = technicalAtmosphere

	@property
	def poundsPerSquareInch(self):
		return PoundsPerSquareInch(self)
	psi = poundsPerSquareInch

	@property
	def millibar(self):
		return Millibar(self)

	mbar = mBar = millibar



@Tiny
@BaseUnit
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


class Bar(Pascal, SystemVariant):
	_unit = 'bar'


class MillimeterOfMercury(Pascal, SystemVariant):
	_unit = "mmHg"


class InchOfMercury(Pascal, SystemVariant):
	_unit = 'inHg'


class Atmosphere(Pascal, SystemVariant):
	_unit = 'atm'


class TechnicalAtmosphere(Pascal, SystemVariant):
	_unit = 'at'


class PoundsPerSquareInch(Pascal, SystemVariant):
	_unit = 'psi'


@synonym
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
