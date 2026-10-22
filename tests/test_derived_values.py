"""A derived value is one number in its unit; see docs/tasks/derived-units-and-algebra.md."""
from datetime import timedelta

import pytest

from WeatherUnits import Length, Time, Wind, Precipitation
from WeatherUnits.derived.rate import MilesPerHour, MetersPerSecond
from WeatherUnits.derived.precipitation import Hourly

Mile, Meter, Millimeter = Length.Mile, Length.Meter, Length.Millimeter
Hour, Minute = Time.Hour, Time.Minute


class TestDenominatorIsImplied:
	def test_bare_number(self):
		v = MilesPerHour(20)
		assert (float(v.numerator), float(v.denominator)) == (20, 1)

	def test_window_is_spent_on_the_rate(self):
		v = MilesPerHour(Mile(40), Hour(2))
		assert v == MilesPerHour(20)
		assert (float(v.numerator), float(v.denominator)) == (20, 1)

	def test_conversion_keeps_one_per_unit(self):
		v = MilesPerHour(Mile(40), Hour(2))['m/s']
		assert float(v) == pytest.approx(8.9408, rel=1e-3)
		assert float(v.denominator) == 1
		assert float(v.numerator) == pytest.approx(float(v))

	def test_from_other_rate(self):
		v = MilesPerHour(MetersPerSecond(10))
		assert float(v) == pytest.approx(22.369, rel=1e-3)
		assert float(v.numerator) == pytest.approx(float(v))
		assert float(v.denominator) == 1

	def test_scalar_multiply(self):
		v = MilesPerHour(Mile(40), Hour(2)) * 2
		assert float(v) == 40
		assert float(v.denominator) == 1

	def test_pow_does_not_divide_twice(self):
		assert float(MilesPerHour(Mile(40), Hour(2)) ** 1) == 20

	def test_hourly_keeps_the_rate_not_the_window(self):
		v = Hourly(Millimeter(6), Hour(3))
		assert float(v) == 2
		assert (float(v.numerator), float(v.denominator)) == (2, 1)
		assert float(v.daily) == 48

	def test_amount_over_interval_stays_an_input_form(self):
		assert float(Hourly(Millimeter(1), Minute(5))) == pytest.approx(12)

	def test_concrete_class_from_bare_number(self):
		assert float(type(Hourly(Millimeter(6), Hour(3)))(6)) == 6

	def test_generic_class_wants_a_unit(self):
		with pytest.raises(TypeError, match='unit'):
			Hourly(6)
		with pytest.raises(TypeError, match='unit'):
			Wind(5)


class TestPeriod:
	def test_defaults_to_none(self):
		assert Millimeter(6).period is None

	def test_carried_beside_the_value(self):
		v = Hourly(Millimeter(6), Hour(3), period=timedelta(hours=24))
		assert v.period == timedelta(hours=24)

	def test_conversion_keeps_it(self):
		v = Hourly(Millimeter(6), Hour(3), period=timedelta(hours=24))
		assert v['in/hr'].period == timedelta(hours=24)


def test_scale_lookup_survives_another_family_with_the_same_member_names():
	# `_scaleFactor` is cached on scale members; converting a rate first used to
	# make a later Pressure.Kilopascal lookup compare two families' `Base`.
	from WeatherUnits import Pressure
	Hourly(Millimeter(6), Hour(3))['in/hr']
	assert float(Pressure.Pascal(1000).kilopascal) == 1


def test_a_rate_of_zero_is_less_than_a_rate_of_a_tenth():
	from WeatherUnits import Length, Precipitation, Time
	none = Precipitation.Hourly(Length.Inch(0.0), Time.Hour(1))
	some = Precipitation.Hourly(Length.Inch(0.1), Time.Hour(1))
	assert none < some and some > none and not some < none
	assert max([none, some, none]) is some
