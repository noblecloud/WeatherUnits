"""Regression tests for docs/tasks/small-fixes.md."""
from pathlib import Path

import pytest

import WeatherUnits as wu
from WeatherUnits import Temperature
from WeatherUnits.temperature import Celsius, Fahrenheit, Kelvin


class TestKelvinSymbol:

	def test_symbol_is_capital_k(self):
		assert Kelvin(300).unit == 'K'
		assert str(Kelvin(300)).endswith('K')

	@pytest.mark.parametrize('spelling', ['k', 'K', 'kelvin', 'Kelvin'])
	def test_lookup_still_resolves(self, spelling):
		assert Temperature.__findUnitClass__(spelling) is Kelvin
		assert wu.Measurement.__findUnitClass__(spelling) is Kelvin

	@pytest.mark.parametrize('spelling', ['k', 'K', 'kelvin'])
	def test_subscript_conversion(self, spelling):
		assert float(Celsius(0)[spelling]) == pytest.approx(273.15)
		assert type(Celsius(0)[spelling]) is Kelvin

	def test_config_key_binds_by_name_and_symbol(self):
		from WeatherUnits.config import config
		assert config.unitPropertiesKeyFor('Kelvin', 'K') == 'kelvin'
		assert config.unitPropertiesKeyFor('Kelvin', 'k') == 'kelvin'


class TestHeatIndex:

	def test_nws_reference_value(self):
		assert float(Fahrenheit(90).heatIndex(50)) == pytest.approx(95, abs=1)

	def test_hot_day_in_celsius_and_kelvin(self):
		f = float(Fahrenheit(90).heatIndex(50))
		assert float(Celsius(Fahrenheit(90).c).heatIndex(50).f) == pytest.approx(f, abs=0.5)
		assert float(Kelvin(Fahrenheit(90).kelvin).heatIndex(50).f) == pytest.approx(f, abs=0.5)

	def test_very_hot_does_not_return_early(self):
		assert float(Celsius(46).heatIndex(50)) > 46

	def test_cool_day_is_unchanged(self):
		t = Fahrenheit(60)
		assert t.heatIndex(50) is t or float(t.heatIndex(50)) == 60

	def test_threshold_is_300_kelvin(self):
		assert float(Kelvin(299.9).heatIndex(50)) == 299.9
		assert float(Kelvin(305).heatIndex(50)) != 305

	def test_dry_air_is_unchanged(self):
		assert float(Fahrenheit(90).heatIndex(10)) == 90


class TestAuto:

	def test_value_and_unit(self):
		m = wu.auto(5, 'm')
		# by name: test_readme registers its own Meter, which shadows the unit lookup
		assert type(m).__name__ == 'Meter'
		assert float(m) == 5
		assert m.unit == 'm'

	def test_string_value(self):
		assert type(wu.auto('5', 'km')).__name__ == 'Kilometer'

	def test_unit_only_still_works(self):
		assert wu.auto('m').__name__ == 'Meter'


class TestPyTyped:

	def test_marker_in_package(self):
		assert (Path(wu.__file__).parent / 'py.typed').is_file()
