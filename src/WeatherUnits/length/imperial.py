from ..utils import ScaleMeta
from . import Length as _Length


class _Scale(ScaleMeta):
	Line = 1
	Inch = 12
	Foot = 12
	Yard = 3
	Mile = 1760


class _Imperial(_Length):
	_format = '{:2.2f}'
	_Scale = _Scale
	_baseUnit = 'foot'

	def _line(self):
		return self.changeScale(self._scale.Line)

	def _inch(self):
		return self.changeScale(self._scale.Inch)

	def _foot(self):
		return self.changeScale(self._scale.Foot)

	def _yard(self):
		return self.changeScale(self._scale.Yard)

	def _mile(self):
		return self.changeScale(self._scale.Mile)

	def _millimeter(self):
		return self._line() * 2.11666666

	def _centimeter(self):
		return self._inch() * 2.54

	def _meter(self):
		return self._foot() * 0.3048

	def _kilometer(self):
		return self._mile() * 1.609344


class Line(_Imperial):
	_type = 'microDistance'
	_format = '{:2.2f}'
	_unit = 'ln'


class Inch(_Imperial):
	_type = 'smallDistance'
	_format = '{:2.2f}'
	_unit = 'in'


class Foot(_Imperial):
	_type = 'mediumDistance'
	_unit = 'ft'


class Yard(_Imperial):
	_type = 'mediumDistance'
	_unit = 'yd'


class Mile(_Imperial):
	_type = 'largeDistance'
	_unit = 'mi'

