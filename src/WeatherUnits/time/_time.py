from .._unit import AbnormalScale


class _Time(AbnormalScale):
	_type = 'time'
	_format = '{:2.2f}'
	_factors = [1, 1000, 60, 60, 12]

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


	## abbreviations
	d = day
	min = minute
	m = minute
	hr = hour
	h = hour
	s = second
	sec = second
	ms = millisecond
