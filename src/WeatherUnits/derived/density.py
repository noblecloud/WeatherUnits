from ..mass import Mass as _Mass
from .. import DerivedMeasurement as _DerivedMeasurement, MeasurementGroup
from .volume import Volume as _Volume


@MeasurementGroup
class Density(_DerivedMeasurement):
	_numerator: _Mass
	_denominator: _Volume
