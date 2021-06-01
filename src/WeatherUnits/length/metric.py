from ..utils import ScaleMeta
from . import Length as _Length


class _Scale(ScaleMeta):
	Millimeter = 1
	Centimeter = 10
	Decimeter = 10
	Meter = 10
	Decameter = 10
	Hectometre = 10
	Kilometer = 10


class _Metric(_Length):
	_format = '{:2.1f}'
	_Scale = _Scale

	def _feet(self):
		return self._meter() * 3.2808399

	def _inches(self):
		return self._centimeter() * 0.393701

	def _miles(self):
		return self._meter() * 0.621371

	def _yards(self):
		return self._feet() * 3

	def _millimeter(self):
		return self.changeScale(_Scale.Millimeter)

	def _centimeter(self):
		return self.changeScale(_Scale.Centimeter)

	def _meter(self):
		return self.changeScale(_Scale.Meter)

	def _kilometer(self):
		return self.changeScale(_Scale.Kilometer)


class Millimeter(_Metric):
	_type = 'microDistance'
	_format = '{:3.1f}'
	_unit = 'mm'


class Centimeter(_Metric):
	_type = 'smallDistance'
	_unit = 'cm'


class Meter(_Metric):
	_type = 'mediumDistance'
	_unit = 'm'


class Kilometer(_Metric):
	_type = 'largeDistance'
	_unit = 'km'
