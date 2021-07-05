from ..base import Scale, UnitSystem, BaseUnit, Large, Medium, Small, Tiny
from .length import Length

@UnitSystem
class Metric(Length):

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
		return self._meter() * 3.280839895013123

	def _millimeter(self):
		return self.changeScale(self._Scale.Millimeter)

	def _centimeter(self):
		return self.changeScale(self._Scale.Centimeter)

	def _meter(self):
		return self.changeScale(self._Scale.Meter)

	def _kilometer(self):
		return self.changeScale(self._Scale.Kilometer)


@Tiny
class Millimeter(Metric):
	_unit = 'mm'


@Small
class Centimeter(Metric):
	_unit = 'cm'


@Small
class Decimeter(Metric):
	_unit = 'dm'


@Medium
@BaseUnit
class Meter(Metric):
	_unit = 'm'


@Medium
class Decameter(Metric):
	_unit = 'dam'


@Large
class Hectometer(Metric):
	_unit = 'hm'


@Large
class Kilometer(Metric):
	_unit = 'km'
