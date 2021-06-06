from ..utils import ScaleMeta as _ScaleMeta
from . import Mass as _Mass
from .. import UnitSystem, BaseUnit


class _Scale(_ScaleMeta):
	Milligram = 1
	Gram = 1000
	Kilogram = 1000


@UnitSystem
class Metric(_Mass):
	_format = '{:2.1f}'
	_Scale = _Scale

	def _dram(self):
		return self._ounce() * 16

	def _ounce(self):
		return self._pound() * 16

	def _pound(self):
		return self._kilogram() * 2.2046226218

	def _milligram(self):
		return self.changeScale(_Scale.Milligram)

	def _gram(self):
		return self.changeScale(_Scale.Gram)

	def _kilogram(self):
		return self.changeScale(_Scale.Kilogram)


class Milligram(Metric):
	_format = '{:3.1f}'
	_unit = 'mg'


@BaseUnit
class Gram(Metric):
	_unit = 'g'


class Kilogram(Metric):
	_unit = 'kg'
