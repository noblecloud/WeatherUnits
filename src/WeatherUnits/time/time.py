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

	def _milliseconds(self):
		return self.changeScale(self._scale.Millisecond)

	def _seconds(self):
		return self.changeScale(self._scale.Second)

	def _minutes(self):
		return self.changeScale(self._scale.Minute)

	def _hours(self):
		return self.changeScale(self._scale.Hour)

	def _days(self):
		return self.changeScale(self._scale.Day)

	def _years(self):
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
		from ..time import Millisecond
		return Millisecond(self._milliseconds())

	@property
	def second(self):
		from ..time import Second
		return Second(self._seconds())

	@property
	def minute(self):
		from ..time import Minute
		minute = Minute(self._minutes())
		minute.title = self.title
		return minute

	@property
	def hour(self):
		from ..time import Hour
		hour = Hour(self._hours())
		hour.title = self.title
		return hour

	@property
	def day(self):
		from ..time import Day
		return Day(self._days())

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
		from ..time import Year
		return Year(self._years())

	@property
	def decade(self):
		from ..time import Decade
		return Decade(self._decade())


	@property
	def century(self):
		from ..time import Century
		return Century(self._century())


	@property
	def millennia(self):
		from ..time import Millennia
		return Millennia(self._millennia())


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
