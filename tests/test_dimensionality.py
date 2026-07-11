from unittest import TestCase

from WeatherUnits import Length, Temperature, Time
from WeatherUnits import errors


class TestDimensionality(TestCase):
	def test_incompatible_addition_raises(self):
		with self.assertRaises(errors.BadConversion):
			Length.Meter(1) + Temperature.Celsius(1)

	def test_incompatible_subtraction_raises(self):
		with self.assertRaises(errors.BadConversion):
			Length.Meter(1) - Time.Second(1)

	def test_compatible_addition_still_works(self):
		self.assertEqual(float(Length.Meter(1) + Length.Meter(2)), 3)

	def test_scalar_addition_still_works(self):
		self.assertEqual(float(Length.Meter(1) + 2), 3)

	def test_incompatible_comparison_returns_false(self):
		self.assertFalse(Length.Meter(1) == Temperature.Celsius(1))
		self.assertFalse(Length.Meter(1) < Temperature.Celsius(5))
