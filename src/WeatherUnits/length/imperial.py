from ..base.Decorators import Tiny, Small, Medium, Large
from ..base import Scale, ScalingMeasurement
from ..base import imperial
from .length import Length


class ImperialLength(ScalingMeasurement, Length, system=imperial, baseUnit='Foot'):
	class _Scale(Scale):
		Line = 1
		Inch = 12
		Foot = 12
		Yard = 3
		Mile = 1760
		Base = 'Foot'

	def _meter(self):
		return self.changeScale(self._Scale.Foot) * 0.3048


@Tiny
class Line(ImperialLength):
	_unit = 'ln'


@Small
class Inch(ImperialLength):
	_unit = 'in'


@Medium
class Foot(ImperialLength, pluralName='Feet'):
	_unit = 'ft'


@Medium
class Yard(ImperialLength):
	_unit = 'yd'


@Large
class Mile(ImperialLength):
	_unit = 'mi'
	_precision = 1
