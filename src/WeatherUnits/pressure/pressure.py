from .. import MeasurementSystem as _MeasurementSystem, NamedType
from src.WeatherUnits import BaseUnit, Huge, Large, Medium, PropertiesFromConfig, Small, SystemVariant, Tiny, UnitSystem
from utils import ScaleMeta as _ScaleMeta


@NamedType
@UnitSystem
class Pressure(_MeasurementSystem):

	class _Scale(_ScaleMeta):
		Pascal = 1
		Decapascal = 10
		Hectopascals = 10
		Kilopascal = 10
		Megapascal = 10
		Gigapascal = 10
		Base = 'Pascal'
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
class Hectopascals(Pressure):
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


@PropertiesFromConfig
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


# Other Names #
Bar = Kilopascal
kPa = Kilopascal
mbar = Hectopascals
hPa = Hectopascals
psi = PoundsPerSquareInch
