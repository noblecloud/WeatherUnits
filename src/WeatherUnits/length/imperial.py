from ..utils import ScaleMeta as _ScaleMeta
from .. import UnitSystem, BaseUnit
from . import Length as _Length


class _Scale(_ScaleMeta):
	Line = 1
	Inch = 12
	Foot = 12
	Yard = 3
	Mile = 1760


@UnitSystem
class Imperial(_Length):
	_format = '{:2.2f}'
	_Scale = _Scale

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

	def _meter(self):
		return self._foot() * 0.3048


class Line(Imperial):
	_format = '{:2.2f}'
	_unit = 'ln'


class Inch(Imperial):
	_format = '{:2.2f}'
	_unit = 'in'


@BaseUnit
class Foot(Imperial):
	_unit = 'ft'


class Yard(Imperial):
	_unit = 'yd'


class Mile(Imperial):
	_unit = 'mi'

