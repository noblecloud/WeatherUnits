from ..utils import ScaleMeta
from . import Length as _Length


class Scale(ScaleMeta):
	Line = 1
	Inch = 12
	Foot = 12
	Yard = 3
	Mile = 1760


class _Imperial(_Length):
	_format = '{:2.2f}'
	_Scale = Scale

	def _lines(self):
		return self.changeScale(self._scale.Line)

	def _inches(self):
		return self.changeScale(self._scale.Inch)

	def _feet(self):
		return self.changeScale(self._scale.Foot)

	def _yards(self):
		return self.changeScale(self._scale.Yard)

	def _miles(self):
		return self.changeScale(self._scale.Mile)

	def _millimeter(self):
		return self._lines() * 2.11666666

	def _centimeter(self):
		return self._inches() * 2.54

	def _meter(self):
		return self._feet() * 0.3048

	def _kilometer(self):
		return self._miles() * 1.609344


class Line(_Imperial):
	_type = 'microDistance'
	_format = '{:2.2f}'
	_unit = 'ln'

	def __init__(self, value):
		super().__init__(value)


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

