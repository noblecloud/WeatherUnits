"""Dimension algebra: `*` and `/` across dimensions; see docs/tasks/derived-units-and-algebra.md."""
from math import isclose

import pytest

from WeatherUnits import Length, Mass, Pressure, Temperature, Time
from WeatherUnits.base import Compound
from WeatherUnits.derived.rate import MilesPerHour

Meter, Foot, Mile, Millimeter = Length.Meter, Length.Foot, Length.Mile, Length.Millimeter
Second, Hour = Time.Second, Time.Hour
Kilogram = Mass.Kilogram


class TestDivision:
	def test_same_dimension_is_a_plain_float(self):
		r = Meter(10) / Meter(2)
		assert r == 5.0 and type(r) is float

	def test_same_dimension_across_systems(self):
		r = Mile(1) / Meter(1609.344)
		assert type(r) is float and isclose(r, 1.0)

	def test_amount_over_interval_keeps_its_units(self):
		r = Millimeter(6) / Hour(3)
		assert float(r) == 2 and r.unit == 'mm/hr' and r.withUnit == '2 mm/hr'

	def test_registered_rate_class_still_wins(self):
		assert (Mile(10) / Hour(1)).unit == 'mph'

	def test_rate_times_its_interval_is_the_amount(self):
		r = (Millimeter(6) / Hour(3)) * Hour(3)
		assert isclose(float(r), 6) and isinstance(r, Length)

	def test_rate_over_a_rate_is_a_float(self):
		assert isclose(MilesPerHour(60) / MilesPerHour(30), 2.0)

	def test_rate_over_time_is_an_acceleration(self):
		r = (Meter(10) / Second(2)) / Second(5)
		assert isinstance(r, Compound) and r.unit == 'm·s⁻²' and isclose(float(r), 1.0)


class TestMultiplication:
	def test_length_squared(self):
		r = Meter(5) * Meter(5)
		assert isinstance(r, Compound) and r.unit == 'm²' and float(r) == 25

	def test_across_systems_lands_in_si(self):
		r = Foot(3) * Meter(1)
		assert r.unit == 'm²' and isclose(float(r), 0.9144)

	def test_unit_free_scalars_still_scale(self):
		assert isinstance(2 * Meter(10), Length) and float(2 * Meter(10)) == 20
		assert float(Meter(10) * 2) == 20

	def test_back_to_a_named_dimension(self):
		force = Kilogram(2) * ((Meter(10) / Second(2)) / Second(5))
		pressure = force / (Meter(1) * Meter(1))
		assert isinstance(pressure, Pressure.Pascal) and isclose(float(pressure), 2.0)

	def test_density_has_a_symbol(self):
		r = Kilogram(2) / (Meter(2) * Meter(2) * Meter(2))
		assert r.unit == 'kg·m⁻³' and isclose(float(r), 0.25)

	def test_exponent_beyond_three_is_an_error(self):
		area = Meter(2) * Meter(2)
		with pytest.raises(ValueError):
			area * area

	def test_temperature_reading_does_not_multiply(self):
		with pytest.raises(TypeError, match='reading'):
			Temperature.Celsius(5) * Meter(2)

	def test_kelvin_does_multiply(self):
		r = Temperature.Kelvin(300) * Meter(2)
		assert isclose(float(r), 600) and r.unit == 'm·K'

	def test_compound_keeps_working_as_a_number(self):
		area = Meter(2) * Meter(3)
		assert float(area + area) == 12 and float(-area) == -6 and float(area * 2) == 12
		assert float(area ** 1) == 6
		with pytest.raises(Exception):
			area + Meter(1)


class TestTypePreservingOperators:
	def test_unary(self):
		assert isinstance(-Temperature.Celsius(5), Temperature.Celsius)
		assert float(-Temperature.Celsius(5)) == -5
		assert isinstance(+Meter(3), Length)
		assert float(-MilesPerHour(20)) == -20 and isinstance(-MilesPerHour(20), MilesPerHour)

	def test_scalar_on_either_side(self):
		assert isinstance(2 * Meter(10), Meter)
		assert isinstance(2 * MilesPerHour(20), MilesPerHour)
		assert isinstance(Meter(10) / 2, Meter)

	def test_modulo_and_floor_division(self):
		assert isinstance(Meter(3) % 2, Meter) and float(Meter(3) % 2) == 1
		assert isinstance(MilesPerHour(20) % 7, MilesPerHour)
		assert isinstance(Meter(7) // 2, Meter)

	def test_metadata_survives(self):
		from datetime import timedelta
		m = Meter(3, title='Wall', key='wall')
		m.period = timedelta(hours=1)
		neg = -m
		assert neg.period == timedelta(hours=1) and neg._title == 'Wall'


def test_same_unit_temperatures_divide_to_a_ratio():
	r = Temperature.Fahrenheit(10) / Temperature.Fahrenheit(40)
	assert type(r) is float and r == 0.25
