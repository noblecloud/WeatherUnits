"""A reading is not a change; see docs/tasks/derived-units-and-algebra.md."""
from math import isclose

import pytest

from WeatherUnits import Length
from WeatherUnits.temperature import Celsius, CelsiusChange, Fahrenheit, FahrenheitChange, Kelvin, summingReadings


def test_reading_minus_reading_is_a_change_in_the_left_degrees():
	r = Celsius(30) - Celsius(20)
	assert isinstance(r, CelsiusChange) and float(r) == 10


def test_a_change_converts_by_factor_only():
	assert isclose(float(CelsiusChange(10).fahrenheit), 18)
	assert isclose(float(FahrenheitChange(18)['c']), 10)
	assert FahrenheitChange(18) == CelsiusChange(10)


def test_across_scales_the_change_is_the_same_change():
	assert isclose(float(Fahrenheit(86) - Celsius(20)), 18)
	assert isclose(float(Celsius(30) - Fahrenheit(50)), 20)


def test_reading_plus_change_is_a_reading_in_every_scale():
	assert isclose(float(Fahrenheit(68) + CelsiusChange(10)), 86)
	assert isclose(float(CelsiusChange(10) + Fahrenheit(68)), 86)
	assert isclose(float(Fahrenheit(68) - CelsiusChange(10)), 50)
	assert isinstance(Celsius(20) + FahrenheitChange(18), Celsius)


def test_two_readings_do_not_add_by_default():
	with pytest.raises(TypeError, match='summingReadings'):
		Celsius(20) + Celsius(10)


def test_opt_in_adds_in_the_left_unit():
	with summingReadings():
		assert float(Celsius(20) + Celsius(10)) == 30
		assert float(Fahrenheit(68) + Fahrenheit(50)) == 118
	with pytest.raises(TypeError):
		Celsius(20) + Celsius(10)


def test_a_bare_number_still_means_the_same_unit():
	assert float(Celsius(30) - 3) == 27
	assert float(Celsius(30) + 3) == 33


def test_change_arithmetic():
	assert float(CelsiusChange(10) * 2) == 20 and isinstance(2 * CelsiusChange(10), CelsiusChange)
	assert float(-CelsiusChange(4)) == -4
	assert float(CelsiusChange(10) + FahrenheitChange(18)) == 20
	assert isclose(FahrenheitChange(18) / CelsiusChange(10), 1.0)
	assert CelsiusChange(5) < FahrenheitChange(18)


def test_a_change_takes_part_in_the_algebra():
	r = CelsiusChange(10) * Length.Meter(2)
	assert r.unit == 'm·K' and isclose(float(r), 20)
	assert isclose(float(FahrenheitChange(18) * Length.Meter(1)), 10)


def test_kelvin_readings_subtract_to_a_change():
	assert isinstance(Kelvin(300) - Kelvin(290), type(Kelvin.change(0)))
