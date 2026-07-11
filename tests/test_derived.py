from unittest import TestCase
from WeatherUnits import Wind, Length, Time

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
		from WeatherUnits import Direction
		mph.direction = Direction(180)
		self.assertEqual(float(mph.direction), 180)
		self.assertEqual(str(mph.direction), 'S ')

	def test_manual_derived(self):
		from WeatherUnits import DerivedMeasurement
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
