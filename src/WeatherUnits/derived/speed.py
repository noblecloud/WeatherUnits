from ..length import Length
from ..time import Time
from . import Derived


class Speed(Derived):
	_type = 'Speed'
	_numerator: Length
	_denominator: Time
