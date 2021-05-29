from . import Time as _Time


class Millisecond(_Time):
	_unit = 'ms'
	_format = '{:4.0f}'
	_scale = 0


class Second(_Time):
	_unit = 's'
	_format = '{:2.1f}'
	_scale = 1


class Minute(_Time):
	_unit = 'min'
	_format = '{:2.1f}'
	_scale = 2


class Hour(_Time):
	_unit = 'hr'
	_scale = 3


class Day(_Time):
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


class Year(_Time):
	_unit = 'yr'
	_scale = 5


class Decade(_Time):
	_unit = 'dec'
	_scale = 6


class Century(_Time):
	_unit = 'cen'
	_scale = 7


class Millennia(_Time):
	_unit = 'mel'
	_scale = 8
