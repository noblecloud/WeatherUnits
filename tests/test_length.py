from unittest import TestCase
from src.WeatherUnits import *


class TestLength(TestCase):
	line = length.Line(1)
	inch = length.Inch(1)
	foot = length.Foot(1)
	yard = length.Yard(1)
	mile = length.Mile(1)
	millimeter = length.Millimeter(1)
	centimeter = length.Centimeter(1)
	meter = length.Meter(1)
	kilometer = length.Kilometer(1)

	def test_line(self):
		self.assertEqual(self.line * 12, self.inch.line)

	def test_inch(self):
		self.assertEqual((self.inch * 12).foot, self.foot)

	def test_foot(self):
		self.assertEqual(self.foot * 3, self.yard.foot)

	def test_yard(self):
		self.assertEqual(self.yard, self.foot * 3)

	def test_mile(self):
		self.assertEqual(length.Foot(5280).mile, self.mile)
