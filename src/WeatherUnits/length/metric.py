from ..base.Decorators import Tiny, Small, Medium, Large
from ..base import Scale, ScalingMeasurement
from ..base import metric
from .length import Length


class MetricLength(ScalingMeasurement, Length, system=metric, baseUnit='Meter'):
	class _Scale(Scale):
		Millimeter = 1
		Centimeter = 10
		Decimeter = 10
		Meter = 10
		Decameter = 10
		Hectometer = 10
		Kilometer = 10
		Base = 'Meter'

	def _foot(self):
		return self.changeScale(self._Scale.Meter) * 3.280839895013123


@Tiny
class Millimeter(MetricLength):
	_unit = 'mm'


@Small
class Centimeter(MetricLength):
	_unit = 'cm'


@Small
class Decimeter(MetricLength):
	_unit = 'dm'


@Medium
class Meter(MetricLength):
	_unit = 'm'


@Medium
class Decameter(MetricLength):
	_unit = 'dam'


@Large
class Hectometer(MetricLength):
	_unit = 'hm'


@Large
class Kilometer(MetricLength):
	_unit = 'km'
