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
		self.assertEqual(low.f, self.fLow)
		self.assertEqual(low.kel, self.kLow)
		self.assertEqual(low.c, self.cLow)

		high = self.cHigh
		self.assertEqual(high.f, self.fHigh)
		self.assertEqual(high.kel, self.kHigh)
		self.assertEqual(high.c, self.cHigh)

		delta = heat.Celsius(10)
		self.assertEqual(delta.fDelta, heat.Fahrenheit(18))

		self.assertEqual(low.withUnit, '0ºc')
		self.assertEqual(str(low), '0º')

	def test__fahrenheit(self):
		low: heat.Fahrenheit = self.fLow
		self.assertEqual(low.c, self.cLow)
		self.assertEqual(low.kel, self.kLow)
		self.assertEqual(low.f, self.fLow)

		high: heat.Fahrenheit = self.fHigh
		self.assertEqual(high.c, self.cHigh)
		self.assertEqual(high.kel, self.kHigh)
		self.assertEqual(high.f, self.fHigh)

		delta = heat.Fahrenheit(18)
		self.assertEqual(delta.cDelta, heat.Celsius(10))

		self.assertEqual(low.withUnit, '32ºf')
		self.assertEqual(str(low), '32º')

	def test__kelvin(self):
		low: heat.Kelvin = self.kLow
		self.assertEqual(low.f, self.fLow)
		self.assertEqual(low.c, self.cLow)
		self.assertEqual(low.kel, self.kLow)

		high: heat.Kelvin = self.kHigh
		self.assertEqual(high.c, self.cHigh)
		self.assertEqual(high.kel, self.kHigh)
		self.assertEqual(high.f, self.fHigh)

		self.assertEqual(low.withUnit, '273.15k')
		self.assertEqual(str(low), '273.15k')
