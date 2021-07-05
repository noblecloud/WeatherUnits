from ..mass import Mass
from ..base import NamedType
from ..base.Measurement import DerivedMeasurement
from .volume import Volume

__all__ = ['Density']


@NamedType
class Density(DerivedMeasurement):
	_numerator: Mass
	_denominator: Volume
