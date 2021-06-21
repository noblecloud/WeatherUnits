from ..base import Integer
from ..base import NamedType
from ..base import Measurement as _Measurement


@NamedType
class Humidity(_Measurement):
	_unit = ''
	_decorator = '%'
