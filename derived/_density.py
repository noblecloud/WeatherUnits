from units.mass import Mass
from . import _Derived
from ._volume import Volume


class Density(_Derived):
	_type = 'density'
	_numerator: Mass
	_denominator: Volume
