import math
from unittest import TestCase

import pytest

from unitcorn import Wind, Length, Time

class TestDerived(TestCase):
	def test_wind_speed(self):
		# Wind is DistanceOverTime
		# MilesPerHour is Wind
		mph = Wind.MilesPerHour(10)
		self.assertEqual(float(mph), 10)
		self.assertEqual(mph.unit, 'mph')
		self.assertEqual(str(mph.withUnit), '10 mph')

	def test_wind_conversions(self):
		mph = Wind.MilesPerHour(2.23694)
		# 2.23694 mph is approx 1 m/s
		self.assertAlmostEqual(float(mph.ms), 1, places=3)
		
		ms = Wind.MetersPerSecond(1)
		self.assertAlmostEqual(float(ms.mph), 2.23694, places=5)

	def test_wind_direction(self):
		mph = Wind.MilesPerHour(10)
		from unitcorn import Direction
		mph.direction = Direction(180)
		self.assertEqual(float(mph.direction), 180)
		# No trailing space: Direction is dimensionless, and a unit spacer
		# before an empty unit is a separator between nothing and nothing.
		self.assertEqual(str(mph.direction), 'S')

	def test_manual_derived(self):
		from unitcorn import DerivedMeasurement
		# Length / Time should create a DistanceOverTime (or similar derived unit)
		dist = Length.Mile(10)
		time = Time.Hour(1)
		speed = dist / time
		self.assertEqual(float(speed), 10)
		# It returns the specialized MilesPerHour which has 'mph' as unit
		self.assertEqual(speed.unit, 'mph')

	def test_compound_multiply_denominator_simplifies(self):
		# (m/s) * s -> m
		speed = Length.Meter(6) / Time.Second(2)  # 3 m/s
		distance = speed * Time.Second(2)
		self.assertIsInstance(distance, Length.Meter)
		self.assertEqual(float(distance), 6)
		# unit conversion of the denominator is respected: 3 m/s * 1 min -> 180 m
		self.assertEqual(float(speed * Time.Minute(1)), 180)

	def test_compound_multiply_commutes(self):
		# s * (m/s) -> m
		speed = Length.Meter(6) / Time.Second(2)  # 3 m/s
		distance = Time.Second(2) * speed
		self.assertIsInstance(distance, Length.Meter)
		self.assertEqual(float(distance), 6)

	def test_compound_divide_by_scalar(self):
		# (6m / 2s) / 2 -> 1.5 m/s  (previously raised TypeError)
		speed = Length.Meter(6) / Time.Second(2)  # 3 m/s
		half = speed / 2
		self.assertAlmostEqual(float(half), 1.5, places=6)
		self.assertEqual(half.unit, speed.unit)

	def test_compound_multiply_by_scalar(self):
		speed = Length.Meter(6) / Time.Second(2)  # 3 m/s
		doubled = speed * 2
		self.assertAlmostEqual(float(doubled), 6, places=6)
		self.assertEqual(doubled.unit, speed.unit)


def test_rates_in_different_units_compare_by_size():
	"""1.4 in/hr is more than 1 in/hr and less than 40 mm/hr (1.575 in/hr), whichever unit each is written in."""
	import unitcorn as uc
	Hourly = uc.Precipitation.Hourly
	rate = Hourly(uc.Length.Inch(1.4), uc.Time.Hour(1))
	one = Hourly(uc.derived.DistanceOverTime.MetersPerSecond(0.0254 / 3600))
	assert rate > one and rate >= one and not rate < one
	assert not rate > Hourly(uc.derived.DistanceOverTime.MetersPerSecond(0.040 / 3600))
	assert rate < Hourly(uc.derived.DistanceOverTime.MetersPerSecond(0.040 / 3600))


class TestKnots:
	"""1 kn = 1852 m / 3600 s exactly."""
	MS_PER_KNOT = 1852 / 3600

	def test_knot_in_metres_per_second(self):
		import unitcorn as uc
		assert math.isclose(float(uc.Wind.Knot(1).ms), self.MS_PER_KNOT, rel_tol=1e-9)
		assert math.isclose(float(uc.Wind.Knot(10).ms), 10 * self.MS_PER_KNOT, rel_tol=1e-9)

	def test_knot_in_other_speeds(self):
		import unitcorn as uc
		assert math.isclose(float(uc.Wind.Knot(1).kmh), 1.852, rel_tol=1e-9)
		assert math.isclose(float(uc.Wind.Knot(1).mph), 1852 / 1609.344, rel_tol=1e-9)

	@pytest.mark.parametrize('value', [0.0, 1.0, 12.5, 40.0, 1234.5])
	def test_round_trips_to_1e_9(self, value):
		import unitcorn as uc
		W = uc.Wind
		for other in (W.MetersPerSecond, W.PerHour, W.MilesPerHour):
			there = other(W.Knot(value))
			assert math.isclose(float(W.Knot(there)), value, rel_tol=1e-9, abs_tol=1e-12), (value, other)
		assert math.isclose(float(W.Knot(W.Knot(value).kmh)), value, rel_tol=1e-9, abs_tol=1e-12)
		assert math.isclose(float(W.Knot(W.Knot(value).mph)), value, rel_tol=1e-9, abs_tol=1e-12)
		assert math.isclose(float(W.Knot(W.Knot(value).ms)), value, rel_tol=1e-9, abs_tol=1e-12)

	def test_from_the_other_speeds(self):
		import unitcorn as uc
		W = uc.Wind
		assert math.isclose(float(W.Knot(W.MetersPerSecond(self.MS_PER_KNOT))), 1.0, rel_tol=1e-9)
		assert math.isclose(float(W.Knot(W.MilesPerHour(1852 / 1609.344))), 1.0, rel_tol=1e-9)
		assert math.isclose(float(W.Knot(W.PerHour(uc.Length.Kilometer(1.852)))), 1.0, rel_tol=1e-9)

	def test_the_same_speed_is_equal_and_ordered(self):
		import unitcorn as uc
		W = uc.Wind
		assert W.Knot(1) == W.MetersPerSecond(self.MS_PER_KNOT)
		assert W.Knot(2) > W.MetersPerSecond(1) > W.Knot(1)
		assert hash(W.Knot(1)) == hash(W.MetersPerSecond(self.MS_PER_KNOT))

	def test_spelling(self):
		import unitcorn as uc
		assert str(uc.Wind.Knot(10)) == '10 kn'
		assert uc.Wind.Knot(10).withUnit == '10 kn'
		assert uc.Wind.Knot(10).unit == 'kn'
		assert str(uc.Wind.MetersPerSecond(10).kn) == '19.4 kn'
		assert str(uc.Wind.MetersPerSecond(10)['kt']) == '19.4 kn'

	@pytest.mark.parametrize('name', ['kn', 'kt', 'knot', 'knots', 'KN', 'Knots'])
	def test_every_name_finds_it(self, name):
		import unitcorn as uc
		assert isinstance(uc.auto(5, name), uc.Wind.Knot), name
		assert float(uc.auto(5, name)) == 5

	def test_it_is_a_wind_and_a_rate(self):
		import unitcorn as uc
		assert isinstance(uc.Wind.Knot(3), uc.Wind)
		assert isinstance(uc.Rate.Knot(3), uc.Rate)
		assert uc.Rate.Knot(3).unit == 'kn'

	def test_a_nautical_mile_over_an_hour_is_a_knot(self):
		import unitcorn as uc
		speed = uc.Length.NauticalMile(10) / uc.Time.Hour(1)
		assert isinstance(speed, uc.Rate.Knot) and speed.unit == 'kn' and float(speed) == 10

	def test_nautical_mile_is_1852_metres(self):
		import unitcorn as uc
		assert math.isclose(float(uc.Length.Meter(uc.Length.NauticalMile(1))), 1852, rel_tol=1e-12)
		assert math.isclose(float(uc.Length.NauticalMile(uc.Length.Kilometer(1.852))), 1, rel_tol=1e-12)
		assert math.isclose(float(uc.Length.Mile(uc.Length.NauticalMile(1))), 1852 / 1609.344, rel_tol=1e-9)
		assert str(uc.Length.NauticalMile(2)) == '2 nmi'

	def test_nautical_mile_is_not_somewhere_to_autoscale_to(self):
		import unitcorn as uc
		assert str(uc.Length.Kilometer(5000).bestFit()) == '5000 km'
		assert str(uc.Length.Meter(1e6).bestFit()) == '1000 km'


class TestBeaufort:
	BOUNDS = (0.5, 1.5, 3.3, 5.5, 7.9, 10.7, 13.8, 17.1, 20.7, 24.4, 28.4, 32.6)
	MIDPOINTS = (0.25, 1.0, 2.4, 4.4, 6.7, 9.3, 12.25, 15.45, 18.9, 22.55, 26.4, 30.5, 34.7)

	def test_every_band_boundary_on_both_sides(self):
		import unitcorn as uc
		for force, bound in enumerate(self.BOUNDS):
			assert int(uc.Beaufort.from_speed(bound)) == force, f'{bound} m/s belongs to force {force}'
			assert int(uc.Beaufort.from_speed(bound - 0.01)) == force, f'just under {bound}'
			assert int(uc.Beaufort.from_speed(bound + 0.01)) == force + 1, f'just over {bound}'

	def test_the_extremes(self):
		import unitcorn as uc
		assert int(uc.Beaufort.from_speed(0)) == 0
		assert int(uc.Beaufort.from_speed(100)) == 12
		assert int(uc.Beaufort.from_speed(32.61)) == 12

	def test_a_bound_given_in_another_unit_stays_in_its_band(self):
		import unitcorn as uc
		W = uc.Wind
		for force, bound in enumerate(self.BOUNDS):
			for speed in (
				W.PerHour(uc.Length.Kilometer(bound * 3.6)),
				W.Knot(bound * 3600 / 1852),
				W.MilesPerHour(bound * 3600 / 1609.344),
			):
				assert int(uc.Beaufort.from_speed(speed)) == force, (speed.withUnit, bound)

	def test_from_a_speed_measurement(self):
		import unitcorn as uc
		W = uc.Wind
		assert int(uc.Beaufort.from_speed(W.MetersPerSecond(10))) == 5
		assert int(uc.Beaufort.from_speed(W.Knot(10))) == 3
		assert int(W.MilesPerHour(10).beaufort) == 3
		assert int(uc.Rate.MetersPerSecond(10).beaufort) == 5

	def test_back_to_a_speed_is_the_midpoint_of_the_band(self):
		import unitcorn as uc
		for force, midpoint in enumerate(self.MIDPOINTS):
			speed = uc.Beaufort(force).speed
			assert math.isclose(float(speed), midpoint, rel_tol=1e-12), force
			assert isinstance(speed, uc.Wind) and speed.unit == 'm/s'
			assert int(uc.Beaufort.from_speed(speed)) == force

	def test_a_force_that_is_not_whole_uses_the_nearest(self):
		import unitcorn as uc
		assert float(uc.Beaufort(3.6).speed) == float(uc.Beaufort(4).speed)

	def test_spelling_is_the_number_then_bft(self):
		import unitcorn as uc
		assert str(uc.Beaufort(4)) == '4 Bft'
		assert uc.Beaufort(4).withUnit == '4 Bft'
		assert str(uc.Beaufort(4).speed) == '6.7 m/s'
		assert str(uc.Beaufort(12)) == '12 Bft'
		assert format(uc.Beaufort(4), 'unit_spacer=False') == '4Bft'
		assert format(uc.Beaufort(4), 'show_unit=False') == '4'

	def test_it_stays_within_0_and_12(self):
		import unitcorn as uc
		assert float(uc.Beaufort(13)) == 12 and float(uc.Beaufort(-1)) == 0

	def test_names(self):
		import unitcorn as uc
		for name in ('Bft', 'bft', 'Beaufort'):
			assert isinstance(uc.auto(4, name), uc.Beaufort), name

	def test_a_speed_is_not_silently_taken_for_a_force(self):
		import unitcorn as uc
		with pytest.raises(TypeError, match='from_speed'):
			uc.Beaufort(uc.Wind.Knot(3))

	def test_a_gap_stays_a_gap(self):
		import unitcorn as uc
		assert math.isnan(float(uc.Beaufort.from_speed(float('nan'))))
		assert math.isnan(float(uc.Beaufort(float('nan')).speed))
