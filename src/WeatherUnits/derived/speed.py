from ..length import Length as _Length
from ..time import Time as _Time
from ..base.Measurement import DerivedMeasurement as _DerivedMeasurement
from ..base.Decorators import NamedType


@NamedType
class Speed(_DerivedMeasurement):
	_numerator: _Length
	_denominator: _Time
