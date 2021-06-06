from .. import Measurement as _Measurement, MeasurementGroup


@MeasurementGroup
class Humidity(_Measurement):
	_format = "{:2d}"
	_unit = ''
	_decorator = '%'
