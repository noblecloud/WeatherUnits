import re
from datetime import timedelta, datetime
from uuid import uuid4

from math import inf

__all__ = ['Time']

from typing import Mapping

from ..base.Decorators import UnitType
from ..base import Dimension, both
from ..base import ScalingMeasurement, Scale, FormatSpec


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


	common = {'Decade', 'Year', 'Day', 'Hour', 'Minute', 'Second', 'Millisecond'}

	# Which unit is sensible at which magnitude. Each rung reads "below
	# <amount> <unit>, show <unit>"; the first rung that fits wins and anything
	# past the last rung is shown in `ladder_top`. Used by the `human` and `ago`
	# specs and by `Time.humanized`. This is a meaning-of-the-number table, not
	# a width constraint: `digit_budget` is unrelated and stays one.
	#
	#   under 90 s -> seconds      (a minute and a half is still "90 s" to a person)
	#   under 90 min -> minutes
	#   under 30 h -> hours        (33 hrs is not a useful reading, 1.4 days is; the
	#                               first draft said 36 h, which would have left 33 hrs alone)
	#   under 14 d -> days
	#   under 8 wk -> weeks
	#   under 18 mth -> months
	#   else -> years
	ladder = (
		(90, 'Second', 'Second'),
		(90, 'Minute', 'Minute'),
		(30, 'Hour', 'Hour'),
		(14, 'Day', 'Day'),
		(8, 'Week', 'Week'),
		(18, 'Month', 'Month'),
	)
	ladder_top = 'Year'

	def __new__(cls, value: float | datetime | timedelta, scale: Scale = None):
		match value:
			case float(value) | int(value):
				pass
			case datetime():
				value = datetime.now().timestamp() - value.timestamp()
				value = Second(value)
				if cls is type(value):
					return value
			case timedelta():
				value = value.total_seconds()
				value = Second(value)
				if cls is type(value):
					return value
		return super().__new__(cls, value, scale)

	def __format__(self, format_spec: str, **extras) -> str:

		original_spec = format_spec

		if precisionSpec := FormatSpec.precision.search(format_spec):
			format_spec = format_spec[:precisionSpec.start()-1] if format_spec.endswith(precisionSpec.group()) else format_spec[precisionSpec.end()+1:]
			precisionSpec = precisionSpec.groupdict()
		else:
			precisionSpec = {'format_spec': ''}

		if format_spec == 'timestamp':
			return self._formatTimestamp()
		elif format_spec.startswith('human'):
			if format_spec[-1] == '+':
				extras['unit_type'] = 'name'
			# The sign is put on by hand: the base formatter sends any value
			# that is not above 1 down its sub-1 branch, so -1.375 days comes
			# out as '-1 days' where 1.375 days comes out as '1.4 days'.
			humanized = self.humanized
			sign = '-' if humanized < 0 else ''
			return sign + abs(humanized).__format__('simple', **extras)
		elif format_spec.startswith('simple'):
			extras['unit_spacer'] = ' '
			if format_spec[-1] == '+':
				extras['unit_type'] = 'name'
			if format_spec := precisionSpec['format_spec']:
				format_spec += ':'
			format_spec = "shorten=True, plural=True"
			return super().__format__(format_spec, **extras)
		elif format_spec.startswith('ago'):
			if format_spec[-1] == '+':
				extras['unit_type'] = 'name'
			if self < 0:
				return f'in {abs(self).__format__("human", **extras)}'
			return f'{self.__format__("human", **extras)} ago'


		units = 'ymwdHMS'
		matches = list(i.groupdict() for i in re.finditer(rf'%(?P<full>(?P<leading>[-#])?(?P<char>[{units}])(?P=char)*)', format_spec))
		params = {}
		trailingID = str(uuid4())
		for group in sorted(matches, key=lambda x: format_spec.index(x['full'])):
			padding = len(group['full'].strip('-#')) if not group['leading'] else 0
			match group['char']:
				case 'y':
					paramID = f'year_{trailingID}'
					newValue = f'{{{paramID}:0{padding}}}'
					params[paramID] = (self.year if not params else abs(self.year)).onlyInt
				case 'm':
					paramID = f'month_{trailingID}'
					newValue = f'{{{paramID}:0{padding}}}'
					params[paramID] = (self.month if not params else abs(self.month)).onlyInt
				case 'w':
					paramID = f'week_{trailingID}'
					newValue = f'{{{paramID}:0{padding}}}'
					params[paramID] = (self.week if not params else abs(self.week)).onlyInt
				case 'd':
					paramID = f'day_{trailingID}'
					newValue = f'{{{paramID}:0{padding}}}'
					params[paramID] = (self.day if not params else abs(self.day)).onlyInt
				case 'H':
					paramID = f'hour_{trailingID}'
					newValue = f'{{{paramID}:0{padding}}}'
					params[paramID] = (self.hour if not params else abs(self.hour)).onlyInt
				case 'M':
					paramID = f'minute_{trailingID}'
					newValue = f'{{{paramID}:0{padding}}}'
					params[paramID] = (self.minute if not params else abs(self.minute)).onlyInt
				case 'S':
					paramID = f'second_{trailingID}'
					newValue = f'{{{paramID}:0{padding}}}'
					params[paramID] = (self.second if not params else abs(self.second)).onlyInt
				case _:
					newValue = f'%{group["full"]}'
			format_spec = format_spec.replace(f'%{group["full"]}', newValue)
		if matches:
			format_spec = {'format': format_spec, **params}
		return super().__format__(format_spec)

	def _formatTimestamp(self) -> str:
		"""
		Clock form, escalating with magnitude.

		=====================  ==================
		under an hour          ``MM:SS``
		an hour up to 100 h    ``H:MM:SS``
		over 100 h             ``Dd H:MM:SS``
		a year or more         ``Yy Dd H:MM:SS``
		=====================  ==================

		Seconds are rounded to the nearest whole second, a negative value keeps
		its sign in front, and a year is 365 days. The year prefix only appears
		once there is a whole year to show, so 101 days reads ``101d 0:00:00``
		and 400 days reads ``1y 35d 0:00:00``.

		This does the arithmetic itself rather than going through ``onlyInt``:
		``Time.common`` holds ``Scale`` members, which ``splitInto`` then tries to
		call as types.
		"""
		total = float(self.second)
		sign = '-' if total < 0 else ''
		total = round(abs(total))
		days, rest = divmod(total, 86400)
		hours, rest = divmod(rest, 3600)
		minutes, seconds = divmod(rest, 60)
		if total < 3600:
			return f'{sign}{minutes:02}:{seconds:02}'
		if total <= 100*3600:
			return f'{sign}{total//3600}:{minutes:02}:{seconds:02}'
		clock = f'{hours}:{minutes:02}:{seconds:02}'
		if days >= 365:
			years, days = divmod(days, 365)
			return f'{sign}{years}y {days}d {clock}'
		return f'{sign}{days}d {clock}'

	@property
	def humanized(self) -> 'Time':
		"""
		This duration in the unit :attr:`ladder` says is sensible for its
		magnitude (``Hour(33).humanized`` is ``Day(1.375)``). The sign is kept;
		the choice is made on the magnitude.
		"""
		seconds = abs(float(self.second))
		for amount, thresholdUnit, unit in self.ladder:
			if seconds < amount*getattr(Time, thresholdUnit).scale.absoluteValue:
				return getattr(Time, unit)(self)
		return getattr(Time, self.ladder_top)(self)

	def __format_value__(self, params: Mapping) -> str:

		return super().__format_value__(params)

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

	@property
	def timedelta(self) -> timedelta:
		return timedelta(seconds=self.second)

	def _millennia(self):
		return self.changeScale(self.scale.Millennia)

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


class Day(Time, plural_name='Days', plural_unit='days'):
	_unit = 'd'
	_digit_budget = 2


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

Time.aMillisecond = Time.oneMillisecond = Millisecond.one = Millisecond(1)
Time.aSecond = Time.oneSecond = Second.one = Second(1)
Time.aMinute = Time.oneMinute = Minute.one = Minute(1)
Time.anHour = Time.oneHour = Hour.one = Hour(1)
Time.aDay = Time.oneDay = Day.one = Day(1)
Time.aWeek = Time.oneWeek = Week.one = Week(1)
Time.aMonth = Time.oneMonth = Month.one = Month(1)
Time.aYear = Time.oneYear = Year.one = Year(1)
Time.aDecade = Time.oneDecade = Decade.one = Decade(1)
Time.aCentury = Time.oneCentury = Century.one = Century(1)
Time.aMillennia = Time.oneMillennia = Millennia.one = Millennia(1)
