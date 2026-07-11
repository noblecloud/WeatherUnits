from unittest import TestCase
from WeatherUnits import Light

class TestLight(TestCase):
	def test_uvi(self):
		uvi = Light.UVI(5)
		self.assertEqual(float(uvi), 5)
		# Index units currently don't show unit string by default
		self.assertEqual(str(uvi.withUnit), '5 ')

	def test_illuminance_irradiance_conversion(self):
		# Based on the code: Irradiance = Illuminance / 120
		lux = Light.Lux(120)
		self.assertEqual(float(lux.wpm2), 1)
		
		irr = Light.Irradiance(1)
		self.assertEqual(float(irr.lux), 120)

	def test_string_representation(self):
		self.assertEqual(str(Light.Lux(100).withUnit), '100 lux')
		self.assertEqual(str(Light.Irradiance(500).withUnit), '500 W/m²')
