from .._unit import MeasurementSystem as _MS


class Length(_MS):
	_type = 'length'


	@property
	def millimeter(self):
		from . import Millimeter
		return Millimeter(self._millimeter())
	mm = millimeter

	@property
	def centimeter(self):
		from . import Centimeter
		return Centimeter(self._centimeter())
	cm = centimeter

	@property
	def meter(self):
		from . import Meter
		return Meter(self._meter())
	m = meter

	@property
	def kilometer(self):
		from . import Kilometer
		return Kilometer(self._kilometer())
	km = kilometer

	@property
	def inch(self):
		from . import Inch
		return Inch(self._inch())

	@property
	def foot(self):
		from . import Foot
		return Foot(self._foot())
	ft = foot

	@property
	def yard(self):
		from . import Yard
		return Yard(self._yard())
	yd = yard

	@property
	def mile(self):
		from . import Mile
		return Mile(self._mile())
	mi = mile

	def __getitem__(self, item):
		item = 'inch' if item == 'in' else item
		super().__getitem__(item)
