from ..base.Decorators import UnitType
from . import Length, Mass, DerivedMeasurement, Volume

__all__ = ['Density']


@UnitType
class Density(DerivedMeasurement, min=0, numerator=Mass, denominator=Volume):
	_id = 'density'

	def __new__(cls, numerator: Mass, denominator: Volume = 1):
		if not isinstance(denominator, Volume) and isinstance(denominator, Length):
			denominator = Volume.compatibleUnits[denominator.unit](denominator)
		return super().__new__(cls, numerator, denominator)

	@property
	def localize(self):
		self.unit
		return super().localize

	@property
	def unit(self):
		return super().unit

	def __class_getitem__(cls, item):
		return super().__class_getitem__(item)
