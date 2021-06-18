from .. import Integer
from .. import Measurement as _Measurement, NamedType


@NamedType
class Humidity(_Measurement):
	_unit = ''
	_decorator = '%'
