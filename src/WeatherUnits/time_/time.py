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

	def __format__(self, format_spec: str) -> str:

		original_spec = format_spec

		if precisionSpec := FormatSpec.precision.search(format_spec):
			format_spec = format_spec[:precisionSpec.start()-1] if format_spec.endswith(precisionSpec.group()) else format_spec[precisionSpec.end()+1:]
			precisionSpec = precisionSpec.groupdict()
		else:
			precisionSpec = {'format_spec': ''}

		if format_spec == 'timestamp':
			if type(self) < Time.Minute:
				if self < Time.anHour:
					format_spec = '%MM:%SS'
				else:
					format_spec = '%H:%MM:%SS'
			else:
				format_spec = '%H:%MM'
			if self.hour > 100:
				format_spec = f'{{day}} {format_spec}'
			if self.day > 100:
				format_spec = f'{{year}} {format_spec}'
		elif format_spec == 'simple':
			if (auto_value := self.auto).unit != self.unit:
				return auto_value.__format__(original_spec)
			if float(self) != 1:
				format_spec = f"{precisionSpec['format_spec']}:plural=True"
			else:
				format_spec = precisionSpec['format_spec']
			return super().__format__(format_spec)
		elif format_spec == 'ago':
			if self < 0:
				return f'in {abs(self).__format__("simple")}'
			return f'{self.__format__("simple")} ago'


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

Time.common = Time.Decade, Time.Year, Time.Day, Time.Hour, Time.Minute, Time.Second, Time.Millisecond
