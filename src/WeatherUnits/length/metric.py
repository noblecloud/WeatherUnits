from ..utils import ScaleMeta
from . import Length as _Length


class _Scale(ScaleMeta):
	Millimeter = 1
	Centimeter = 10
	Decimeter = 10
	Meter = 10
	Decameter = 10
	Hectometer = 10
	Kilometer = 10


class _Metric(_Length):
	_format = '{:2.1f}'
	_Scale = _Scale
	_baseUnit = 'meter'

	def _line(self):
		return self._millimeter() * 0.4724409448818898

	def _foot(self):
		return self._meter() * 3.280839895013123

	def _inch(self):
		return self._centimeter() * 0.3937007874015748

	def _mile(self):
		return self._kilometer() * 0.6213711922373338

	def _yard(self):
		return self._foot() * 3

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


class Decimeter(_Metric):
	_type = 'mediumSmallDistance'
	_unit = 'dm'


class Meter(_Metric):
	_type = 'mediumDistance'
	_unit = 'm'


class Decameter(_Metric):
	_type = 'mediumLargeDistance'
	_unit = 'dam'


class Hectometer(_Metric):
	_type = 'largeDistance'
	_unit = 'hm'


class Kilometer(_Metric):
	_type = 'largeDistance'
	_unit = 'km'
