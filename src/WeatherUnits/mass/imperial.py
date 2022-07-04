from ..base.Decorators import Tiny, Small, Large, Huge
from ..base import Scale, ScalingMeasurement, Dimension, imperial
from .mass import Mass

__all__ = ['Dram', 'Ounce', 'Pound', 'Hundredweight', 'Ton']


class Imperial(ScalingMeasurement, Mass, metaclass=Dimension, system=imperial, baseUnit='Pound'):
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
class Pound(Imperial):
	_unit = 'lbs'


@Large
class Hundredweight(Imperial):
	_unit = 'cwt'


@Huge
class Ton(Imperial):
	_id = 'tUS'
	_unit = 't'
