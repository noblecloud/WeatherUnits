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
	Hectopascals: type
	Kilopascal: type
	Gigapascal: type
	Atmosphere: type
	TechnicalAtmosphere: type
	PoundsPerSquareInch: type
	mmHg: type
	inHg: type
	Bar: type
	kPa: type
	mbar: type
	mBar: type
	hPa: type
	psi: type

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
		Bar = 1 / 1000
		Atmosphere = 101325.
		TechnicalAtmosphere = 98066.5
		PoundsPerSquareInch = 6894.757293168
		mmHg = 1 / 0.00750062
		inHg = 1 / 0.00029530


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


class mmHg(Pascal, SystemVariant):
	_unit = "mmHg"


class inHg(Pascal, SystemVariant):
	_unit = 'inHg'


class Atmosphere(Pascal, SystemVariant):
	_unit = 'atm'


class TechnicalAtmosphere(Pascal, SystemVariant):
	_unit = 'at'


class PoundsPerSquareInch(Pascal, SystemVariant):
	_unit = 'psi'


@synonym
class mBar(Hectopascal):
	_unit = 'mBar'
	_max = 4




Pressure.Pascal = Pascal
Pressure.Decapascal = Decapascal
Pressure.Hectopascals = Hectopascal
Pressure.Kilopascal = Kilopascal
Pressure.Gigapascal = Gigapascal
Pressure.Atmosphere = Atmosphere
Pressure.TechnicalAtmosphere = TechnicalAtmosphere
Pressure.PoundsPerSquareInch = PoundsPerSquareInch
Pressure.mmHg = mmHg
Pressure.inHg = inHg
Pressure.Bar = Bar
Pressure.kPa = Kilopascal
Pressure.mbar = mBar
Pressure.mBar = mBar
Pressure.hPa = Hectopascal
Pressure.psi = PoundsPerSquareInch
