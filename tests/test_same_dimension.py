"""Metric and imperial units of one dimension compare and combine.

`.type` is a scaling unit's *system* family (`Meter.type` is MetricLength,
`Foot.type` is ImperialLength), so tests that used it as the dimension treated a
foot as unrelated to a metre. See docs/tasks/same-dimension-regressions.md.
"""
import pytest

from WeatherUnits import errors
from WeatherUnits.derived.rate import MetersPerSecond, MilesPerHour
from WeatherUnits.length import Centimeter, Foot, Kilometer, Meter, Mile, Millimeter
from WeatherUnits.temperature import Celsius, Fahrenheit, Kelvin
from WeatherUnits.time_ import Time


def test_add_across_systems():
	total = Meter(1) + Foot(1)
	assert type(total) is Meter
	assert float(total) == pytest.approx(1.3048)


def test_subtract_across_systems():
	assert float(Foot(10) - Meter(1)) == pytest.approx(10 - 3.280839895)


def test_equal_across_systems():
	assert Meter(1) == Foot(3.280839895)
	assert Foot(3.280839895) == Meter(1)


def test_equal_temperatures_across_scales():
	assert Celsius(0) == Fahrenheit(32)
	assert Fahrenheit(32) == Celsius(0)
	assert Kelvin(273.15) == Celsius(0)
	assert Celsius(0) == Kelvin(273.15)


@pytest.mark.parametrize('smaller, larger', [
	(Fahrenheit(70), Celsius(25)),
	(Kilometer(1), Mile(1)),
	(Meter(1), Foot(4)),
	(MilesPerHour(20), MetersPerSecond(10)),
])
def test_order_across_units(smaller, larger):
	assert smaller < larger
	assert larger > smaller
	assert smaller <= larger
	assert larger >= smaller
	assert not larger < smaller
	assert not smaller > larger


def test_mixed_temperatures_sort_by_temperature():
	ordered = sorted([Fahrenheit(40), Celsius(1), Kelvin(270)])
	assert [type(t) for t in ordered] == [Kelvin, Celsius, Fahrenheit]


def test_a_round_trip_is_still_equal_and_ordered_both_ways():
	there_and_back = Meter(Foot(Meter(1)))
	assert there_and_back == Meter(1)
	assert there_and_back <= Meter(1) and there_and_back >= Meter(1)


def test_same_dimension_division_is_a_ratio():
	ratio = Meter(10) / Meter(2)
	assert type(ratio) is float and ratio == 5.0


def test_equality_compares_the_value_not_the_display():
	assert Celsius(20) != Celsius(20.09)
	assert Celsius(20) != Celsius(20.05)
	assert Celsius(20).displays_same(Celsius(20.05))
	assert not Celsius(20).displays_same(Celsius(21))


def test_displays_same_converts_into_this_unit():
	assert Celsius(0).displays_same(Fahrenheit(32.01))


def test_equal_values_hash_alike():
	assert len({Meter(1), Centimeter(100), Millimeter(1000)}) == 1
	assert hash(Meter(1)) == hash(Foot(3.280839895))
	assert hash(Celsius(0)) == hash(Fahrenheit(32)) == hash(Kelvin(273.15))
	assert hash(Time.Week(1)) == hash(Time.Day(7))


def test_unequal_values_are_unequal():
	assert hash(Celsius(20)) != hash(Celsius(20.05))
	assert Time.Week(1) != Time.Month(1)


def test_different_dimensions_are_not_equal():
	assert Meter(1) != Celsius(1)
	assert not Meter(1) == Celsius(1)


def test_different_dimensions_do_not_order():
	with pytest.raises(TypeError):
		Meter(1) < Celsius(1)
	with pytest.raises(TypeError):
		sorted([Meter(1), Celsius(1)])


def test_different_dimensions_do_not_add():
	with pytest.raises(errors.BadConversion):
		Meter(1) + Celsius(1)


def test_plain_numbers_compare_in_this_unit():
	assert Meter(1) == 1
	assert Meter(1) < 2
	assert Celsius(20) != 20.05
