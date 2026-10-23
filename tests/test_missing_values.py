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

	def test_it_formats_as_an_ellipsis(self):
		for cls in (Humidity, Temperature.Celsius, Length.Meter, Pressure.Hectopascal):
			with self.subTest(cls=cls.__name__):
				self.assertEqual('⋯', str(cls(nan)))
				self.assertEqual('⋯', str(cls(None)))

	def test_a_format_spec_does_not_change_it(self):
		self.assertEqual('⋯', f'{Length.Meter(nan):precision=2}')
		self.assertEqual('⋯', f'{Temperature.Celsius(nan):convert=f}')

	def test_it_does_not_look_like_a_saturated_reading(self):
		self.assertNotIn('100', repr(Humidity(nan)))
		self.assertNotIn('inf', repr(Temperature.Celsius(nan)))

	def test_the_config_names_it(self):
		from WeatherUnits.config import config
		self.assertEqual('⋯', config['UnitDefaults']['missing'])


class TestPlaceholderLevels(TestCase):
	"""`missing` resolves like every other parameter: format spec, instance, unit config, defaults."""

	def test_a_format_spec_overrides_it(self):
		self.assertEqual('n/a', f'{Length.Meter(nan):missing=n/a}')
		self.assertEqual('--', format(Length.Meter(nan), 'precision=2, missing=--'))
		self.assertEqual('?', Length.Meter(nan).__format__('', missing='?'))

	def test_an_instance_overrides_it(self):
		value = Length.Meter(nan)
		value.missing = 'no reading'
		self.assertEqual('no reading', str(value))
		self.assertEqual('⋯', str(Length.Meter(nan)))

	def test_a_class_overrides_it(self):
		original = Humidity.__dict__.get('_missing')
		try:
			Humidity._missing = '--'
			self.assertEqual('--', str(Humidity(nan)))
			self.assertEqual('⋯', str(Temperature.Celsius(nan)))
		finally:
			if original is None:
				del Humidity._missing
			else:
				Humidity._missing = original

	def test_it_is_a_default_format_param(self):
		self.assertEqual('⋯', Length.Meter(1).defaultFormatParams['missing'])

	def test_the_config_file_sets_both_levels(self):
		# The config binds at import, so a fresh interpreter reads a file with a default and a per-unit override.
		import subprocess, sys, textwrap
		from pathlib import Path
		from tempfile import TemporaryDirectory
		si = Path(__file__).resolve().parents[1] / 'src' / 'WeatherUnits' / 'config' / 'si.ini'
		text = si.read_text(encoding='utf-8').replace('missing = ⋯', 'missing = n/a').replace('kelvin = unit_symbol=', 'kelvin = unit_symbol=, missing=no data')
		with TemporaryDirectory() as folder:
			path = Path(folder) / 'units.ini'
			path.write_text(text, encoding='utf-8')
			script = textwrap.dedent('''
				from WeatherUnits.length import Meter
				from WeatherUnits.temperature import Kelvin
				print(f'{Meter(None)}|{Kelvin(None)}')
			''')
			out = subprocess.run([sys.executable, '-c', script], env={**__import__('os').environ, 'WU_CONFIG_PATH': str(path)}, capture_output=True, text=True, encoding='utf-8')
		self.assertEqual('n/a|no data', out.stdout.strip(), out.stderr)
