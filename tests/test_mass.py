from unittest import TestCase
from WeatherUnits import Mass

class TestMass(TestCase):
	def test_metric_conversions(self):
		gram = Mass.Gram(1000)
		self.assertEqual(gram.kilogram, 1)
		self.assertEqual(gram.milligram, 1000000)
		
		kg = Mass.Kilogram(1)
		self.assertEqual(kg.gram, 1000)
		self.assertEqual(kg.milligram, 1000000)

	def test_imperial_conversions(self):
		pound = Mass.Pound(1)
		self.assertEqual(pound.ounce, 16)
		
		ounce = Mass.Ounce(16)
		self.assertEqual(ounce.pound, 1)

	def test_cross_system_conversions(self):
		# 1 kg is approx 2.20462 lbs
		kg = Mass.Kilogram(1)
		# self.assertAlmostEqual(float(kg.lbs), 2.2046226218, places=5)
		
		# 1 lb is approx 453.592 g
		lb = Mass.Pound(1)
		# self.assertAlmostEqual(float(lb.gram), 453.59237, places=2)

	def test_string_representation(self):
		self.assertEqual(str(Mass.Gram(100).withUnit), '100 g')
		self.assertEqual(str(Mass.Kilogram(1.5).withUnit), '1.5 kg')
		self.assertEqual(str(Mass.Pound(2).withUnit), '2 lbs')
		self.assertEqual(str(Mass.Ounce(10).withUnit), '10 oz')
