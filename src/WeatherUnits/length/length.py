from .._unit import Measurement as _Measurement


class _Length(_Measurement):
	_type = 'length'

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

	def __getitem__(self, item):
		item = 'inch' if item == 'in' else item
		super().__getitem__(item)
