from ..base.Decorators import Tiny, Small, Large, Huge
from ..base import Scale, ScalingMeasurement, metric
from .mass import Mass

__all__ = ['Metric', 'Microgram', 'Milligram', 'Gram', 'Kilogram', 'Tonne']


class Metric(ScalingMeasurement, Mass, system=metric, baseUnit='Kilogram'):
	class _Scale(Scale):
		Microgram = 1
		Milligram = 1000
		Gram = 1000
		Kilogram = 1000
		Tonne = 1000
		Base = 'Kilogram'

	def _pound(self):
		return self.changeScale(self._Scale.Kilogram) * 2.2046226218


@Tiny
class Microgram(Metric):
	_unit = 'μg'


@Tiny
class Milligram(Metric):
	_unit = 'mg'


@Small
class Gram(Metric):
	_unit = 'g'


@Large
class Kilogram(Metric):
	_unit = 'kg'


@Huge
class Tonne(Metric):
	_id = 'tSI'
	_unit = 't'
