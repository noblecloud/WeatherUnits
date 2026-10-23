from ..base import Dimension


class Length(metaclass=Dimension, symbol='L'):
	Millimeter: type
	Centimeter: type
	Decimeter: type
	Meter: type
	Decameter: type
	Hectometer: type
	Kilometer: type

	Line: type
	Inch: type
	Foot: type
	Yard: type
	Mile: type

	@property
	def millimeter(self):
		from . import Millimeter
		return Millimeter(self)
	mm = millimeter

	@property
	def centimeter(self):
		from . import Centimeter
		return Centimeter(self)
	cm = centimeter

	@property
	def meter(self):
		from . import Meter
		return Meter(self)
	m = meter

	@property
	def kilometer(self):
		from . import Kilometer
		return Kilometer(self)
	km = kilometer

	@property
	def line(self):
		from . import Line
		return Line(self)
	ln = line

	@property
	def inch(self):
		from . import Inch
		return Inch(self)

	@property
	def foot(self):
		from . import Foot
		return Foot(self)
	ft = foot

	@property
	def yard(self):
		from . import Yard
		return Yard(self)
	yd = yard

	@property
	def mile(self):
		from . import Mile
		return Mile(self)
	mi = mile

	def __getitem__(self, item):
		item = 'inch' if item == 'in' else item
		super().__getitem__(item)
