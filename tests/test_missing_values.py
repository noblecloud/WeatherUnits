"""A gap in the data stays a gap.

APIs send NaN and None for readings they don't have. Clamping used to sort NaN
into the limits, so a missing humidity showed as saturated (`100%`) and a
missing temperature as `inf°`.
"""
from math import isnan, nan
from unittest import TestCase

from WeatherUnits import Length, Pressure, Temperature
from WeatherUnits.others import Humidity, Percentage


class TestNaNPassesThrough(TestCase):

	def test_it_is_not_clamped_to_the_upper_limit(self):
		for cls in (Humidity, Percentage, Temperature.Celsius, Temperature.Fahrenheit, Length.Meter, Pressure.Hectopascal):
			with self.subTest(cls=cls.__name__):
				self.assertTrue(isnan(float(cls(nan))))

	def test_none_becomes_nan(self):
		for cls in (Humidity, Percentage, Temperature.Celsius, Length.Meter, Pressure.Hectopascal):
			with self.subTest(cls=cls.__name__):
				self.assertTrue(isnan(float(cls(None))))

	def test_real_values_are_still_clamped(self):
		self.assertEqual(1.0, float(Humidity(5.0, isPercentage=False)))
		self.assertEqual(0.0, float(Humidity(-1.0)))

	def test_nan_survives_a_conversion(self):
		self.assertTrue(isnan(float(Temperature.Fahrenheit(Temperature.Celsius(nan)))))

	def test_it_is_falsy(self):
		for cls in (Humidity, Temperature.Celsius, Length.Meter):
			with self.subTest(cls=cls.__name__):
				self.assertFalse(cls(nan))
				self.assertFalse(cls(None))

	def test_zero_is_still_truthy_with_its_unit(self):
		self.assertTrue(Length.Meter(0))

	def test_value_unset_sees_it(self):
		self.assertTrue(Humidity(nan).valueUnset)
		self.assertFalse(Humidity(0).valueUnset)


class TestPlaceholder(TestCase):

	def test_it_formats_as_an_em_dash(self):
		for cls in (Humidity, Temperature.Celsius, Length.Meter, Pressure.Hectopascal):
			with self.subTest(cls=cls.__name__):
				self.assertEqual('—', str(cls(nan)))
				self.assertEqual('—', str(cls(None)))

	def test_a_format_spec_does_not_change_it(self):
		self.assertEqual('—', f'{Length.Meter(nan):precision=2}')
		self.assertEqual('—', f'{Temperature.Celsius(nan):convert=f}')

	def test_it_does_not_look_like_a_saturated_reading(self):
		self.assertNotIn('100', repr(Humidity(nan)))
		self.assertNotIn('inf', repr(Temperature.Celsius(nan)))

	def test_the_placeholder_can_be_configured(self):
		from WeatherUnits.base import Measurement
		original = Measurement._missing
		try:
			Measurement._missing = '⋯'
			self.assertEqual('⋯', str(Humidity(nan)))
		finally:
			Measurement._missing = original

	def test_the_config_names_it(self):
		from WeatherUnits.config import config
		self.assertEqual('—', config['UnitDefaults']['missing'])
