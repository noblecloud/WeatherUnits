from unittest import TestCase
from src.WeatherUnits import *


class TestHeat(TestCase):
	cLow = temperature.Celsius(0)
	fLow = temperature.Fahrenheit(32)
	kLow = temperature.Kelvin(273.15)
	cHigh = temperature.Celsius(100)
	fHigh = temperature.Fahrenheit(212)
	kHigh = temperature.Kelvin(373.15)

	def test__celsius(self):
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

	def test__fahrenheit(self):
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

	def test__kelvin(self):
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
