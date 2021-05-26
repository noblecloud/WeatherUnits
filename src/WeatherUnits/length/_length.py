from typing import Callable, Union
from .._unit import Measurement


class _Length(Measurement):
	_type = 'length'

	_millimeter: Callable
	_centimeter: Callable
	_meter: Callable
	_kilometer: Callable
	_lines: Callable
	_inches: Callable
	_feet: Callable
	_yards: Callable
	_miles: Callable

	@property
	def mm(self):
		from . import Millimeter
		return Millimeter(self._millimeter())

	@property
	def cm(self):
		from . import Centimeter
		return Centimeter(self._centimeter())

	@property
	def m(self):
		from . import Meter
		return Meter(self._meter())

	@property
	def km(self):
		from . import Kilometer
		return Kilometer(self._kilometer())

	@property
	def inch(self):
		from . import Inch
		return Inch(self._inches())

	@property
	def ft(self):
		from . import Foot
		return Foot(self._feet())

	@property
	def yd(self):
		from . import Yard
		return Yard(self._yards())

	@property
	def mi(self):
		from . import Mile
		return Mile(self._miles())
