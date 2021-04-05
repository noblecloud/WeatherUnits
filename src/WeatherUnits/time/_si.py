from . import Time


class Millisecond(Time):
	_unit = 'ms'
	_format = '{:4.0f}'
	_scale = 0


class Second(Time):
	_unit = 's'
	_format = '{:2.1f}'
	_scale = 1


class Minute(Time):
	_unit = 'min'
	_format = '{:2.1f}'
	_scale = 2


class Hour(Time):
	_unit = 'hr'
	_scale = 3


class Day(Time):
	_unit = 'd'
	_scale = 4
