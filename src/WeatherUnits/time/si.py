from .time import Time


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


# class Week(_Time):
# 	_unit = 'wk'
# 	_scale = 4
# 	_multiplier = 7
#
#
# class Month(_Time):
# 	_unit = 'mnt'
# 	_scale = 4
# 	_multiplier = 30


class Year(Time):
	_unit = 'yr'
	_scale = 5


class Decade(Time):
	_unit = 'dec'
	_scale = 6


class Century(Time):
	_unit = 'cen'
	_scale = 7


class Millennia(Time):
	_unit = 'mel'
	_scale = 8
