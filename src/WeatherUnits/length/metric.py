from src.WeatherUnits import Large, Medium, Small, Tiny
from ..utils import ScaleMeta as _ScaleMeta
from . import Length as _Length
from .. import UnitSystem, BaseUnit


class _Scale(_ScaleMeta):
	Millimeter = 1
	Centimeter = 10
	Decimeter = 10
	Meter = 10
	Decameter = 10
	Hectometer = 10
	Kilometer = 10
	Base = 'Meter'


@UnitSystem
class Metric(_Length):
	_Scale = _Scale

	def _foot(self):
		return self._meter() * 3.280839895013123

	def _millimeter(self):
		return self.changeScale(_Scale.Millimeter)

	def _centimeter(self):
		return self.changeScale(_Scale.Centimeter)

	def _meter(self):
		return self.changeScale(_Scale.Meter)

	def _kilometer(self):
		return self.changeScale(_Scale.Kilometer)


@Tiny
class Millimeter(Metric):
	_unit = 'mm'


@Small
class Centimeter(Metric):
	_unit = 'cm'


@Small
class Decimeter(Metric):
	_unit = 'dm'


@Medium
@BaseUnit
class Meter(Metric):
	_unit = 'm'


@Medium
class Decameter(Metric):
	_unit = 'dam'


@Large
class Hectometer(Metric):
	_unit = 'hm'


@Large
class Kilometer(Metric):
	_unit = 'km'
