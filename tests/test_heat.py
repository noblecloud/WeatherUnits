from unittest import TestCase
from src.WeatherUnits import *


class TestHeat(TestCase):
	cLow = temperature.Celsius(0)
	fLow = temperature.Fahrenheit(32)
	kLow = temperature.Kelvin(273.15)
	cHigh = temperature.Celsius(100)
	fHigh = temperature.Fahrenheit(212)
	kHigh = temperature.Kelvin(373.15)

	cRoom: temperature.Celsius = temperature.Celsius(20.0)
	fRoom = temperature.Fahrenheit(68.0)
	cDewpoint = temperature.Celsius(13.2)
	fDewpoint = temperature.Fahrenheit(55.76)


	def test_celsius(self):
		low: temperature.Celsius = self.cLow
		self.assertEqual(self.fLow, low.f)
		self.assertEqual(self.kLow, low.kel)
		self.assertEqual(self.cLow, low.c)

		high = self.cHigh
		self.assertEqual(self.fHigh, high.f)
		self.assertEqual(self.kHigh, high.kel)
		self.assertEqual(self.cHigh, high.c)

		delta = temperature.Celsius(10)
		self.assertEqual(temperature.Fahrenheit(18), delta.fDelta)

		self.assertEqual('0ºc', low.withUnit)
		self.assertEqual('0º', str(low))

	def test_fahrenheit(self):
		low: temperature.Fahrenheit = self.fLow
		self.assertEqual(self.cLow, low.c)
		self.assertEqual(self.kLow, low.kel)
		self.assertEqual(self.fLow, low.f)

		high: temperature.Fahrenheit = self.fHigh
		self.assertEqual(self.cHigh, high.c)
		self.assertEqual(self.kHigh, high.kel)
		self.assertEqual(self.fHigh, high.f)

		delta = temperature.Fahrenheit(18)
		self.assertEqual(temperature.Celsius(10), delta.cDelta)

		self.assertEqual('32ºf', low.withUnit)
		self.assertEqual('32º', str(low))

	def test_kelvin(self):
		low: temperature.Kelvin = self.kLow
		self.assertEqual(self.fLow, low.f)
		self.assertEqual(self.cLow, low.c)
		self.assertEqual(self.kLow, low.kel)

		high: temperature.Kelvin = self.kHigh
		self.assertEqual(self.cHigh, high.c)
		self.assertEqual(self.kHigh, high.kel)
		self.assertEqual(self.fHigh, high.f)

		self.assertEqual('273k', low.withUnit)
		self.assertEqual('273', str(low))

	def test_dewpoint(self):
		self.assertEqual(self.cDewpoint, self.cRoom.dewpoint(65))
		self.assertEqual(self.fDewpoint, self.fRoom.dewpoint(65))
