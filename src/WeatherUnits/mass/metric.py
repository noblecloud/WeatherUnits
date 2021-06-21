from ..base import Large, Small, Tiny
from ..utils import ScaleMeta as _ScaleMeta
from . import Mass as _Mass
from ..base import UnitSystem, BaseUnit


@UnitSystem
class Metric(_Mass):

	class _Scale(_ScaleMeta):
		Milligram = 1
		Gram = 1000
		Kilogram = 1000
		Base = 'Gram'

	def _dram(self):
		return self._ounce() * 16

	def _ounce(self):
		return self._pound() * 16

	def _pound(self):
		return self._kilogram() * 2.2046226218

	def _milligram(self):
		return self.changeScale(self._Scale.Milligram)

	def _gram(self):
		return self.changeScale(self._Scale.Gram)

	def _kilogram(self):
		return self.changeScale(self._Scale.Kilogram)


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
