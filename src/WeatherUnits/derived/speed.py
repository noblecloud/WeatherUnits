from ..length import Length as _Length
from ..time import Time as _Time
from . import Derived as _Derived


class Speed(_Derived):
	_type = 'Speed'
	_numerator: _Length
	_denominator: _Time
