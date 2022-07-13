from datetime import timedelta, datetime

from math import inf

__all__ = ['Time']

from ..base.Decorators import UnitType
from ..base import Dimension, both
from ..base import ScalingMeasurement, Scale


@UnitType
class Time(ScalingMeasurement, metaclass=Dimension, system=both, symbol='T', baseUnit='Second'):
	_limits = -inf, inf
	Millisecond: type
	Second: type
	Minute: type
	Hour: type
	Day: type
	Week: type
	Month: type
	Year: type
	Decade: type
	Century: type
	Millennia: type

	_acceptedTypes = (timedelta,)

	class _Scale(Scale):
		Millisecond = 1/1000
		Second = 1
		Minute = 60
		Hour = 60
		Day = 24
		Year = 365
		Decade = 10
		Century = 10
		Millennia = 10
		Base = 'Second'
		Week = 7.0*float(Day*Hour*Minute*Second)
		Month = 30.436875*float(Day*Hour*Minute*Second)

	def _convert(self, other):
		if isinstance(other, datetime):
			other = Second(other.timestamp() - datetime.now().timestamp())
		if isinstance(other, timedelta):
			other = Second(other.total_seconds())
		return super()._convert(other)

	def _millisecond(self):
		return self.changeScale(self.scale.Millisecond)

	def _second(self):
		return self.changeScale(self.scale.Second)

	def _minute(self):
		return self.changeScale(self.scale.Minute)

	def _hour(self):
		return self.changeScale(self.scale.Hour)

	def _day(self):
		return self.changeScale(self.scale.Day)

	def _year(self):
		return self.changeScale(self.scale.Year)

	def _month(self):
		return float(Month(self))

	def _decade(self):
		return self.changeScale(self.scale.Decade)

	def _century(self):
		return self.changeScale(self.scale.Century)

	def _millennia(self):
		return self.changeScale(self.scale.Millennia)

	@property
	def auto(self):
		if self._second() < 60 and self.scale <= self._Scale.Second:
			return self.s
		elif self._minute() < 60 and self.scale <= self._Scale.Minute:
			return self.min
		elif self._hour() < 24 and self.scale <= self._Scale.Hour:
			return self.hour
		elif self._day() < 7 and self.scale <= self._Scale.Year:
			return self.week
		elif self._day() < 30 and self.scale <= self._Scale.Year:
			return self.month
		return self

	@property
	def autoAny(self):
		if abs(self._second()) < 60:
			return self.s
		elif abs(self._minute()) < 60:
			return self.min
		elif abs(self._hour()) < 24:
			return self.hour
		elif abs(self._day()) < 2:
			return self.day
		elif abs(self._day()) < 7:
			return self.week
		elif abs(self._day()) < 30:
			return self.month
		elif abs(self._year()) > 1:
			return self.year
		return self

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

	@property
	def week(self):
		return Week(self)

	@property
	def month(self):
		return Month(self)

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


class Second(Time, alias='sec'):
	_unit = 's'


class Minute(Time):
	_precision = 1
	_unit = 'min'


class Hour(Time):
	_unit = 'hr'


class Day(Time):
	_unit = 'd'


class Week(Time):
	_unit = 'wk'


class Month(Time):
	_unit = 'mth'


class Year(Time):
	_unit = 'yr'


class Decade(Time):
	_unit = 'dec'


class Century(Time):
	_unit = 'cen'


class Millennia(Time):
	_unit = 'mel'


Time.Millisecond = Millisecond
Time.Second = Second
Time.Minute = Minute
Time.Hour = Hour
Time.Day = Day
Time.Week = Week
Time.Month = Month
Time.Year = Year
Time.Decade = Decade
Time.Century = Century
Time.Millennia = Millennia
