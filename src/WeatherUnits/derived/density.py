from ..mass import Mass as _Mass
from .._unit import Derived as _Derived
from .volume import Volume as _Volume


class Density(_Derived):
	_type = 'density'
	_numerator: _Mass
	_denominator: _Volume
