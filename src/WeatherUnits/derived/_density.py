from ..mass import Mass
from . import Derived
from ._volume import Volume


class Density(Derived):
	_type = 'density'
	_numerator: Mass
	_denominator: Volume
