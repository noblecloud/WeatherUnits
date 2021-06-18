from .. import SystemVariant
from .. import MeasurementSystem as _MS, NamedType, BaseUnit, UnitSystem
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
	Base = 'Second'

@UnitSystem
@NamedType
class Time(_MS):
	_format = '{:2.2f}'
	_Scale = Scale

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
		if self._second() < 60:
			return self.s
		elif self._minute() < 60:
			return self.min
		elif self._hour() < 24:
			return self.hour
		elif self._day() < 7:
			return self.week
		elif self._month() > 1:
			return self.month
		elif self._year() > 1:
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
		from ..time import Week
		return Week(self._day() / 7)

	@property
	def month(self):
		from ..time import Month
		return Month(self._day() / 30)

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


class Week(Time, SystemVariant):
	_unit = 'wk'
	_multiplier = 1/604800


class Month(Time, SystemVariant):
	_unit = 'mth'
	_multiplier = 1/2592000


class Year(Time):
	_unit = 'yr'


class Decade(Time):
	_unit = 'dec'


class Century(Time):
	_unit = 'cen'


class Millennia(Time):
	_unit = 'mel'
