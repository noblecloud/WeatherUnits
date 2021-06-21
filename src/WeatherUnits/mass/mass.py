from ..base import NamedType
from ..base import MeasurementSystem as _MS

__all__ = ['Mass']

@NamedType
class Mass(_MS):
	Gram: type
	Milligram: type
	Kilogram: type
	Dram: type
	Ounce: type
	Pound: type
	Hundredweight: type
	Ton: type

	@property
	def milligram(self):
		from . import Milligram
		return Milligram(self)

	@property
	def gram(self):
		from . import Gram
		return Gram(self)

	@property
	def kilogram(self):
		from . import Kilogram
		return Kilogram(self)

	@property
	def dram(self):
		from . import Dram
		return Dram(self)

	@property
	def ounce(self):
		from . import Ounce
		return Ounce(self)

	@property
	def pound(self):
		from . import Pound
		return Pound(self)

	mg = milligram
	g = gram
	kg = kilogram
	oz = ounce
	lbs = pound
