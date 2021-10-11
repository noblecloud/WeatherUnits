from ..base import Scale, UnitSystem, BaseUnit, Huge, Large, Small, Tiny
from . import Mass

__all__ = ['Dram', 'Ounce', 'Pound', 'Hundredweight', 'Ton']


@UnitSystem
class Imperial(Mass):

	class _Scale(Scale):
		Dram = 1
		Ounce = 16
		Pound = 16
		Hundredweight = 100
		Ton = 20
		Base = 'Pound'

	def _gram(self):
		return self.changeScale(self._Scale.Ounce) * 28.349523125


@Tiny
class Dram(Imperial):
	_unit = 'dr'


@Small
class Ounce(Imperial):
	_unit = 'oz'


@Small
@BaseUnit
class Pound(Imperial):
	_unit = 'lbs'


@Large
class Hundredweight(Imperial):
	_unit = 'cwt'


@Huge
class Ton(Imperial):
	_unit = 't'
