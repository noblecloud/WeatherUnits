from .._unit import AbnormalScale


class _Time(AbnormalScale):
	_format = '{:2.2f}'
	# milliseconds, second, minute, hour, day
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
	def ms(self):
		from ..time import Millisecond
		return Millisecond(self._milliseconds())

	@property
	def s(self):
		from ..time import Second
		return Second(self._seconds())

	@property
	def min(self):
		from ..time import Minute
		return Minute(self._minutes())

	@property
	def hr(self):
		from ..time import Hour
		return Hour(self._hours())

	@property
	def day(self):
		from ..time import Day
		return Day(self._days())
