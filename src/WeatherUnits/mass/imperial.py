from src.WeatherUnits import Huge, Large, Small, Tiny
from ..utils import ScaleMeta as _ScaleMeta
from . import Mass as _Mass
from .. import UnitSystem, BaseUnit


class _Scale(_ScaleMeta):
	Dram = 1
	Ounce = 16
	Pound = 16
	Hundredweight = 100
	Ton = 20


@UnitSystem
class Imperial(_Mass):
	_format = '{:2.1f}'
	_Scale = _Scale

	def _dram(self):
		return self.changeScale(self._scale.Dram)

	def _ounce(self):
		return self.changeScale(self._scale.Ounce)

	def _pound(self):
		return self.changeScale(self._scale.Pound)

	def _hundredweight(self):
		return self.changeScale(self._scale.Hundredweight)

	def _ton(self):
		return self.changeScale(self._scale.Ton)

	def _milligram(self):
		return self._ounce() * 0.02834952312

	def _gram(self):
		return self._ounce() * 28.349523125

	def _kilogram(self):
		return self._pound() * 0.45359237


@Tiny
class Dram(Imperial):
	_format = '{:1.1f}'
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
