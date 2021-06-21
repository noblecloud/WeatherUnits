from ..base.Decorators import Large, Medium, Small, Tiny
from ..utils import ScaleMeta as _ScaleMeta
from ..base.Decorators import UnitSystem, BaseUnit
from .length import Length as _Length


@UnitSystem
class Imperial(_Length):
	class _Scale(_ScaleMeta):
		Line = 1
		Inch = 12
		Foot = 12
		Yard = 3
		Mile = 1760
		Base = 'Foot'

	def _line(self):
		return self.changeScale(self.scale.Line)

	def _inch(self):
		return self.changeScale(self.scale.Inch)

	def _foot(self):
		return self.changeScale(self.scale.Foot)

	def _yard(self):
		return self.changeScale(self.scale.Yard)

	def _mile(self):
		return self.changeScale(self.scale.Mile)

	def _meter(self):
		return self._foot() * 0.3048


@Tiny
class Line(Imperial):
	_unit = 'ln'


@Small
class Inch(Imperial):
	_unit = 'in'


@Medium
@BaseUnit
class Foot(Imperial):
	_unit = 'ft'


@Medium
class Yard(Imperial):
	_unit = 'yd'


@Large
class Mile(Imperial):
	_unit = 'mi'
	_precision = 1

