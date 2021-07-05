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

	def _dram(self):
		return self.changeScale(self.scale.Dram)

	def _ounce(self):
		return self.changeScale(self.scale.Ounce)

	def _pound(self):
		return self.changeScale(self.scale.Pound)

	def _hundredweight(self):
		return self.changeScale(self.scale.Hundredweight)

	def _ton(self):
		return self.changeScale(self.scale.Ton)

	def _milligram(self):
		return self._ounce() * 0.02834952312

	def _gram(self):
		return self._ounce() * 28.349523125

	def _kilogram(self):
		return self._pound() * 0.45359237


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
