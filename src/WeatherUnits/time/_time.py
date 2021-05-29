from .._unit import AbnormalScale


class _Time(AbnormalScale):
	_type = 'time'
	_format = '{:2.2f}'
	_factors = [1, 1000, 60, 60, 12, 365, 10, 10, 10]

	def _milliseconds(self):
		return self.changeScale(0)

	def _seconds(self):
		return self.changeScale(1)

	def _minutes(self):
		return self.changeScale(2)

	def _hours(self):
		return self.changeScale(3)

	def _days(self):
		return self.changeScale(4)

	def _years(self):
		return self.changeScale(5)

	def _decade(self):
		return self.changeScale(6)

	def _century(self):
		return self.changeScale(7)

	def _millennia(self):
		return self.changeScale(8)

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
		return Minute(self._minutes())

	@property
	def hour(self):
		from ..time import Hour
		return Hour(self._hours())

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
