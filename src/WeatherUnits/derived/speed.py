from ..length import Length as _Length
from ..time import Time as _Time
from .. import DerivedMeasurement as _DerivedMeasurement
from .. import NamedType


@NamedType
class Speed(_DerivedMeasurement):
	_numerator: _Length
	_denominator: _Time
