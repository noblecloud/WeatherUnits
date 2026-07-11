from unittest import TestCase
from WeatherUnits import Pressure

class TestPressure(TestCase):
	def test_pascal_conversions(self):
		pa = Pressure.Pascal(1000)
		self.assertEqual(pa.hectopascal, 10)
		self.assertEqual(pa.kilopascal, 1)
		
		hpa = Pressure.Hectopascal(1013.25)
		self.assertAlmostEqual(float(hpa.pascal), 101325, places=1)

	def test_aliases(self):
		hpa = Pressure.Hectopascal(1013.25)
		self.assertEqual(float(hpa.mbar), 1013.25)
		self.assertEqual(float(hpa.millibar), 1013.25)

	def test_other_units(self):
		# 1 atm = 101325 Pa

		# hPa to inHg
		hpa = Pressure.Hectopascal(1013.25)
		# 1013.25 hPa is approx 29.92 inHg
		self.assertAlmostEqual(float(hpa.inHg), 29.92, places=2)

	def test_string_representation(self):
		# The default configuration (si.ini) localizes pressure to mmHg,
		# so a Hectopascal value is displayed converted to mmHg.
		self.assertEqual(str(Pressure.Hectopascal(1013.25).withUnit), '760.00 mmHg')
		self.assertEqual(str(Pressure.InchOfMercury(29.92).withUnit), '29.9 inHg')
