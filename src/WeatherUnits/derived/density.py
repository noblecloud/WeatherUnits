from ..mass import Mass as _Mass
from ..base import NamedType
from ..base.Measurement import DerivedMeasurement as _DerivedMeasurement
from .volume import Volume as _Volume

__all__ = ['Density']


@NamedType
class Density(_DerivedMeasurement):
	_numerator: _Mass
	_denominator: _Volume
