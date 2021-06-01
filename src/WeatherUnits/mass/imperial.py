

from . import Mass as _Mass
from utils import ScaleMeta as _ScaleMeta


class Scale(_ScaleMeta):
	Base = 1
	Dram = 1
	Ounce = 16
	Pound = 16
	Hundredweight = 100
	Ton = 20


class _Imperial(_Mass):
	_format = '{:2.1f}'
	_Scale = Scale

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


class Dram(_Imperial):
	_format = '{:1.1f}'
	_unit = 'dr'


class Ounce(_Imperial):
	_unit = 'oz'


class Pound(_Imperial):
	_unit = 'lbs'


class Hundredweight(_Imperial):
	_unit = 'cwt'


class Ton(_Imperial):
	_unit = 't'
