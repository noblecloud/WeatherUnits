from unittest import TestCase
from src.WeatherUnits import *


class TestHeat(TestCase):
	cLow = heat.Celsius(0)
	fLow = heat.Fahrenheit(32)
	kLow = heat.Kelvin(273.15)
	cHigh = heat.Celsius(100)
	fHigh = heat.Fahrenheit(212)
	kHigh = heat.Kelvin(373.15)

	def test__celsius(self):
		low: heat.Celsius = self.cLow
		self.assertEqual(self.fLow, low.f)
		self.assertEqual(self.kLow, low.kel)
		self.assertEqual(self.cLow, low.c)

		high = self.cHigh
		self.assertEqual(self.fHigh, high.f)
		self.assertEqual(self.kHigh, high.kel)
		self.assertEqual(self.cHigh, high.c)

		delta = heat.Celsius(10)
		self.assertEqual(heat.Fahrenheit(18), delta.fDelta)

		self.assertEqual('0ºc', low.withUnit)
		self.assertEqual('0º', str(low))

	def test__fahrenheit(self):
		low: heat.Fahrenheit = self.fLow
		self.assertEqual(self.cLow, low.c)
		self.assertEqual(self.kLow, low.kel)
		self.assertEqual(self.fLow, low.f)

		high: heat.Fahrenheit = self.fHigh
		self.assertEqual(self.cHigh, high.c)
		self.assertEqual(self.kHigh, high.kel)
		self.assertEqual(self.fHigh, high.f)

		delta = heat.Fahrenheit(18)
		self.assertEqual(heat.Celsius(10), delta.cDelta)

		self.assertEqual('32ºf', low.withUnit)
		self.assertEqual('32º', str(low))

	def test__kelvin(self):
		low: heat.Kelvin = self.kLow
		self.assertEqual(self.fLow, low.f)
		self.assertEqual(self.cLow, low.c)
		self.assertEqual(self.kLow, low.kel)

		high: heat.Kelvin = self.kHigh
		self.assertEqual(self.cHigh, high.c)
		self.assertEqual(self.kHigh, high.kel)
		self.assertEqual(self.fHigh, high.f)

		self.assertEqual('273.1k', low.withUnit)
		self.assertEqual('273.1', str(low))
