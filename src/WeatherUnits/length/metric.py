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


@UnitSystem
class Metric(_Length):
	_format = '{:2.1f}'
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


class Millimeter(Metric):
	_format = '{:3.1f}'
	_unit = 'mm'


class Centimeter(Metric):
	_unit = 'cm'


class Decimeter(Metric):
	_unit = 'dm'


@BaseUnit
class Meter(Metric):
	_unit = 'm'


class Decameter(Metric):
	_unit = 'dam'


class Hectometer(Metric):
	_unit = 'hm'


class Kilometer(Metric):
	_unit = 'km'
