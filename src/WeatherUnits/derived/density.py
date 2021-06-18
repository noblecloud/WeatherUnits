from ..mass import Mass as _Mass
from .. import DerivedMeasurement as _DerivedMeasurement, NamedType
from .volume import Volume as _Volume


@NamedType
class Density(_DerivedMeasurement):
	_numerator: _Mass
	_denominator: _Volume
