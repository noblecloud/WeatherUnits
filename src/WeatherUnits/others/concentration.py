from .._unit import Measurement as _Measurement


class Humidity(_Measurement):
	_type = 'concentration'
	_format = "{:2d}"
	_unit = ''
	_decorator = '%'
