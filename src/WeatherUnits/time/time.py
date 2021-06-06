from .._unit import MeasurementSystem as _MS
from ..utils import ScaleMeta as _ScaleMeta


class Scale(_ScaleMeta):
	Millisecond = 1
	Second = 1000
	Minute = 60
	Hour = 60
	Day = 24
	Year = 365
	Decade = 10
	Century = 10
	Millennia = 10


class Time(_MS):
	_type = 'time'
	_format = '{:2.2f}'
	_Scale = Scale
	_baseUnit = 'second'

	def _millisecond(self):
		return self.changeScale(self._scale.Millisecond)

	def _second(self):
		return self.changeScale(self._scale.Second)

	def _minute(self):
		return self.changeScale(self._scale.Minute)

	def _hour(self):
		return self.changeScale(self._scale.Hour)

	def _day(self):
		return self.changeScale(self._scale.Day)

	def _year(self):
		return self.changeScale(self._scale.Year)

	def _decade(self):
		return self.changeScale(self._scale.Decade)

	def _century(self):
		return self.changeScale(self._scale.Century)

	def _millennia(self):
		return self.changeScale(self._scale.Millennia)

	@property
	def auto(self):
		if self._seconds() < 60:
			return self.s
		elif self._minutes() < 60:
			return self.min
		elif self._hours() < 24:
			return self.hour
		return

	@property
	def millisecond(self):
		return Millisecond(self)

	@property
	def second(self):
		return Second(self)

	@property
	def minute(self):
		return Minute(self)

	@property
	def hour(self):
		return Hour(self)

	@property
	def day(self):
		return Day(self)

	# @property
	# def week(self):
	# 	from ..time import Week
	# 	return Week(self._days() / 7)
	#
	# @property
	# def month(self):
	# 	from ..time import Month
	# 	return Month(self._days() / 30)

	@property
	def year(self):
		return Year(self)

	@property
	def decade(self):
		return Decade(self)

	@property
	def century(self):
		return Century(self)

	@property
	def millennia(self):
		return Millennia(self)


	## abbreviations
	y = year
	d = day
	min = minute
	m = minute
	hr = hour
	h = hour
	s = second
	sec = second
	ms = millisecond


class Millisecond(Time):
	_unit = 'ms'
	_format = '{:4.0f}'


@BaseUnit
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
