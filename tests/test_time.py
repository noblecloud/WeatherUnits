from datetime import timedelta
from unittest import TestCase
from WeatherUnits import Time


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
		self.assertEqual(self.second * self.hour, self.hour)

	def test_timedelta_math(self):
		self.assertEqual(self.second + timedelta(seconds=59), self.minute)
