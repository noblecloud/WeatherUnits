from unittest import TestCase
from WeatherUnits.digital import RSSI

class TestDigital(TestCase):
	def test_rssi(self):
		rssi = RSSI(-50)
		self.assertEqual(float(rssi), -50)
		self.assertEqual(rssi.unit, 'dBm')
		self.assertEqual(rssi.string, 'Great')
		
		rssi = RSSI(-30)
		self.assertEqual(rssi.string, 'Perfect')
		
		rssi = RSSI(-95)
		self.assertEqual(rssi.string, 'None')
