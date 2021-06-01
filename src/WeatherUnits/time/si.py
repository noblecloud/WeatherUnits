from .time import Time


class Millisecond(Time):
	_unit = 'ms'
	_format = '{:4.0f}'


class Second(Time):
	_unit = 's'
	_format = '{:2.1f}'


class Minute(Time):
	_unit = 'min'
	_format = '{:2.1f}'


class Hour(Time):
	_unit = 'hr'


class Day(Time):
	_unit = 'd'


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


class Decade(Time):
	_unit = 'dec'


class Century(Time):
	_unit = 'cen'


class Millennia(Time):
	_unit = 'mel'
