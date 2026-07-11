from unittest import TestCase
from WeatherUnits import Length


class TestLength(TestCase):
	line = Length.Line(1)
	inch = Length.Inch(1)
	foot = Length.Foot(1)
	yard = Length.Yard(1)
	mile = Length.Mile(1)
	millimeter = Length.Millimeter(1)
	centimeter = Length.Centimeter(1)
	meter = Length.Meter(1)
	kilometer = Length.Kilometer(1)

	def test_line(self):
		self.assertEqual(self.line * 12, self.inch.line)

	def test_inch(self):
		self.assertEqual((self.inch * 12).foot, self.foot)

	def test_foot(self):
		self.assertEqual(self.foot * 3, self.yard.foot)

	def test_yard(self):
		self.assertEqual(self.yard, self.foot * 3)

	def test_mile(self):
		self.assertEqual(Length.Foot(5280).mile, self.mile)
