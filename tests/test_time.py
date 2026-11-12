from datetime import timedelta
from unittest import TestCase
from unitcorn import Time


class TestTime(TestCase):
	second = Time.Second(1)
	minuteAsSeconds = Time.Second(60)
	minute = Time.Minute(1)
	hourAsMinutes = Time.Minute(60)
	hour = Time.Hour(1)
	dayAsHours = Time.Hour(24)
	day = Time.Day(1)
	weekAsDays = Time.Day(7)
	week = Time.Week(1)
	month = Time.Month(1)
	yearAsDays = Time.Day(365)
	year = Time.Year(1)

	def test_conversion(self):
		self.assertEqual(self.minute, self.minuteAsSeconds.minute)
		self.assertEqual(self.hour, self.hourAsMinutes.hour)
		self.assertEqual(self.day, self.dayAsHours.day)
		# self.assertEqual(self.week, self.weekAsDays.week)
		assert (self.week == self.weekAsDays.week)
		self.assertEqual(self.month, self.month.month)
		self.assertEqual(self.year, self.yearAsDays.year)

	def test_multiplication(self):
		self.assertEqual(self.second * 60, self.minute)
		# Seconds times hours is a time squared, not a time: see test_algebra.py
		self.assertAlmostEqual(float(self.second * self.hour), 3600)

	def test_timedelta_math(self):
		self.assertEqual(self.second + timedelta(seconds=59), self.minute)


class TestTimeLadder(TestCase):
	"""`Time.ladder` picks the unit; `human`, `human+` and `ago` use it."""

	def test_ladder_boundaries(self):
		# (just below the threshold, at the threshold) -> (unit below, unit at/above)
		cases = (
			(Time.Second(89.9), Time.Second(90), 'Second', 'Minute'),
			(Time.Minute(89.9), Time.Minute(90), 'Minute', 'Hour'),
			(Time.Hour(29.9), Time.Hour(30), 'Hour', 'Day'),
			(Time.Day(13.9), Time.Day(14), 'Day', 'Week'),
			(Time.Week(7.9), Time.Week(8), 'Week', 'Month'),
			(Time.Month(17.9), Time.Month(18), 'Month', 'Year'),
		)
		for below, at, lowerUnit, upperUnit in cases:
			with self.subTest(at=repr(at)):
				self.assertEqual(type(below.humanized).__name__, lowerUnit)
				self.assertEqual(type(at.humanized).__name__, upperUnit)

	def test_ladder_is_data_on_the_class(self):
		self.assertEqual([unit for _, _, unit in Time.ladder], ['Second', 'Minute', 'Hour', 'Day', 'Week', 'Month'])
		self.assertEqual(Time.ladder_top, 'Year')

	def test_big_values_stay_years(self):
		self.assertEqual(format(Time.Year(40), 'human'), '40 yrs')
		self.assertEqual(format(Time.Century(1), 'human'), '100 yrs')

	def test_humanized_keeps_value(self):
		self.assertEqual(type(Time.Hour(33).humanized), Time.Day)
		self.assertAlmostEqual(float(Time.Hour(33).humanized), 1.375)
		self.assertEqual(Time.Hour(33).humanized, Time.Hour(33))

	def test_humanized_is_chosen_on_magnitude(self):
		self.assertEqual(type(Time.Hour(-33).humanized), Time.Day)
		self.assertLess(float(Time.Hour(-33).humanized), 0)

	def test_human_rescales(self):
		self.assertEqual(format(Time.Hour(33), 'human'), '1.4 days')
		self.assertEqual(format(Time.Second(45), 'human'), '45 s')
		self.assertEqual(format(Time.Second(0), 'human'), '0 s')
		self.assertEqual(format(Time.Second(90), 'human'), '1.5 mins')
		self.assertEqual(format(Time.Minute(90), 'human'), '1.5 hrs')
		self.assertEqual(format(Time.Day(14), 'human'), '2 wks')
		self.assertEqual(format(Time.Month(18), 'human'), '1.5 yrs')

	def test_human_whole_numbers_stay_whole(self):
		self.assertEqual(format(Time.Hour(48), 'human'), '2 days')
		self.assertEqual(format(Time.Hour(3), 'human'), '3 hrs')
		self.assertEqual(format(Time.Second(120), 'human'), '2 mins')

	def test_human_across_input_units(self):
		# the same duration reads the same whatever it was built in
		self.assertEqual(format(Time.Minute(1980), 'human'), format(Time.Hour(33), 'human'))
		self.assertEqual(format(Time.Second(118800), 'human'), format(Time.Hour(33), 'human'))

	def test_human_negative_keeps_sign(self):
		self.assertEqual(format(Time.Hour(-3), 'human'), '-3 hrs')
		self.assertEqual(format(Time.Hour(-33), 'human'), '-1.4 days')
		self.assertEqual(format(Time.Second(-45), 'human'), '-45 s')

	def test_human_plus_names(self):
		self.assertEqual(format(Time.Second(45), 'human+'), '45 Seconds')
		self.assertEqual(format(Time.Second(90), 'human+'), '1.5 Minutes')
		self.assertEqual(format(Time.Hour(3), 'human+'), '3 Hours')
		self.assertEqual(format(Time.Hour(33), 'human+'), '1.4 Days')
		self.assertEqual(format(Time.Day(14), 'human+'), '2 Weeks')
		self.assertEqual(format(Time.Month(3), 'human+'), '3 Months')
		self.assertEqual(format(Time.Month(18), 'human+'), '1.5 Years')
		self.assertEqual(format(Time.Hour(-33), 'human+'), '-1.4 Days')

	def test_human_in_fstring(self):
		self.assertEqual(f'{Time.Hour(33):human}', '1.4 days')

	def test_ago_past(self):
		self.assertEqual(format(Time.Hour(3), 'ago'), '3 hrs ago')
		self.assertEqual(format(Time.Second(45), 'ago'), '45 s ago')
		self.assertEqual(format(Time.Hour(33), 'ago'), '1.4 days ago')
		self.assertEqual(format(Time.Hour(33), 'ago+'), '1.4 Days ago')

	def test_ago_future(self):
		self.assertEqual(format(Time.Hour(-3), 'ago'), 'in 3 hrs')
		self.assertEqual(format(Time.Hour(-33), 'ago'), 'in 1.4 days')
		self.assertEqual(format(Time.Hour(-33), 'ago+'), 'in 1.4 Days')

	def test_simple_is_unchanged(self):
		# `simple` keeps the unit it was given
		self.assertEqual(format(Time.Hour(33), 'simple'), '33 hrs')
		self.assertEqual(format(Time.Hour(33), 'simple+'), '33 Hours')
		self.assertEqual(format(Time.Hour(-3), 'simple'), '-3 hrs')


class TestTimeTimestamp(TestCase):

	def test_under_an_hour(self):
		self.assertEqual(format(Time.Second(0), 'timestamp'), '00:00')
		self.assertEqual(format(Time.Second(59), 'timestamp'), '00:59')
		self.assertEqual(format(Time.Second(90), 'timestamp'), '01:30')
		self.assertEqual(format(Time.Minute(59), 'timestamp'), '59:00')

	def test_hours(self):
		self.assertEqual(format(Time.Minute(61), 'timestamp'), '1:01:00')
		self.assertEqual(format(Time.Second(3725), 'timestamp'), '1:02:05')
		self.assertEqual(format(Time.Hour(33), 'timestamp'), '33:00:00')
		self.assertEqual(format(Time.Hour(100), 'timestamp'), '100:00:00')

	def test_days_past_100_hours(self):
		self.assertEqual(format(Time.Hour(101), 'timestamp'), '4d 5:00:00')
		self.assertEqual(format(Time.Day(101), 'timestamp'), '101d 0:00:00')

	def test_years_past_a_year(self):
		self.assertEqual(format(Time.Day(364), 'timestamp'), '364d 0:00:00')
		self.assertEqual(format(Time.Day(400), 'timestamp'), '1y 35d 0:00:00')
		self.assertEqual(format(Time.Year(2), 'timestamp'), '2y 0d 0:00:00')

	def test_rounds_to_whole_seconds(self):
		self.assertEqual(format(Time.Second(59.4), 'timestamp'), '00:59')
		self.assertEqual(format(Time.Second(59.6), 'timestamp'), '01:00')

	def test_negative(self):
		self.assertEqual(format(Time.Second(-45), 'timestamp'), '-00:45')
		self.assertEqual(format(Time.Hour(-2), 'timestamp'), '-2:00:00')
		self.assertEqual(format(Time.Hour(-101), 'timestamp'), '-4d 5:00:00')

	def test_same_for_any_input_unit(self):
		self.assertEqual(format(Time.Second(3660), 'timestamp'), format(Time.Minute(61), 'timestamp'))
		self.assertEqual(format(Time.Hour(1), 'timestamp'), format(Time.Second(3600), 'timestamp'))
