from ..base import Scale, UnitSystem, BaseUnit, Huge, Large, Small, Tiny
from . import Mass

__all__ = ['Metric', 'Microgram', 'Milligram', 'Gram', 'Kilogram', 'Tonne']


@UnitSystem
class Metric(Mass):

	class _Scale(Scale):
		Microgram = 1
		Milligram = 1000
		Gram = 1000
		Kilogram = 1000
		Tonne = 1000
		Base = 'Gram'

	def _pound(self):
		return self.changeScale(self._Scale.Kilogram) * 2.2046226218


@Tiny
class Microgram(Metric):
	_unit = 'μg'


@Tiny
class Milligram(Metric):
	_unit = 'mg'


@Small
@BaseUnit
class Gram(Metric):
	_unit = 'g'


@Large
class Kilogram(Metric):
	_unit = 'kg'


@Huge
class Tonne(Metric):
	_unit = 't'
