import unittest
from unittest import TestCase
from WeatherUnits import Temperature


class TestTemperature(TestCase):
	cLow = Temperature.Celsius(0)
	fLow = Temperature.Fahrenheit(32)
	kLow = Temperature.Kelvin(273.15)
	cHigh = Temperature.Celsius(100)
	fHigh = Temperature.Fahrenheit(212)
	kHigh = Temperature.Kelvin(373.15)

	cRoom: Temperature.Celsius = Temperature.Celsius(20.0)
	fRoom = Temperature.Fahrenheit(68.0)
	cDewpoint = Temperature.Celsius(13.2)
	fDewpoint = Temperature.Fahrenheit(55.76)

	def test_celsius(self):
		low: Temperature.Celsius = self.cLow
		self.assertEqual(self.fLow, low.f)
		self.assertEqual(self.kLow, low.kel)
		self.assertEqual(self.cLow, low.c)

		high = self.cHigh
		self.assertEqual(self.fHigh, high.f)
		self.assertEqual(self.kHigh, high.kel)
		self.assertEqual(self.cHigh, high.c)

		delta = Temperature.Celsius(10)
		self.assertEqual(Temperature.Fahrenheit(18), delta.fDelta)

		self.assertEqual('0º', str(low))

	def test_fahrenheit(self):
		# The withUnit assertion below (`'32ºf'`) was an expected failure
		# until FormatSpec.params learned ':' as a key/value separator.
		# `.withUnit` is `f'{self:showUnit: True}'`, but the params regex
		# only ever matched `key=value`, so `showUnit: True` was silently
		# dropped and the force-show did nothing at all.
		#
		# It looked like it worked wherever the class default for showUnit
		# was already True (Kelvin, and Fahrenheit back when _showUnit was
		# incorrectly hardcoded True in fahrenheit.py) - "forced" and
		# "default" were indistinguishable there. Celsius, whose default is
		# False, is the honest test: see test_celsius_force_show_unit.
		low: Temperature.Fahrenheit = self.fLow
		self.assertEqual(self.cLow, low.c)
		self.assertEqual(self.kLow, low.kel)
		self.assertEqual(self.fLow, low.f)

		high: Temperature.Fahrenheit = self.fHigh
		self.assertEqual(self.cHigh, high.c)
		self.assertEqual(self.kHigh, high.kel)
		self.assertEqual(self.fHigh, high.f)

		delta = Temperature.Fahrenheit(18)
		self.assertEqual(Temperature.Celsius(10), delta.cDelta)

		self.assertEqual('32ºf', str(low.withUnit))

	def test_kelvin(self):
		low: Temperature.Kelvin = self.kLow
		self.assertEqual(self.fLow, low.f)
		self.assertEqual(self.cLow, low.c)
		self.assertEqual(self.kLow, low.kel)

		high: Temperature.Kelvin = self.kHigh
		self.assertEqual(self.cHigh, high.c)
		self.assertEqual(self.kHigh, high.kel)
		self.assertEqual(self.fHigh, high.f)
		low.precision = 1
		low.max = 4
		self.assertEqual('273.1k', low.withUnit)

	def test_celsius_force_show_unit(self):
		# Celsius defaults to showUnit=False (the º decorator already conveys
		# it), so this is the one temperature where forcing the unit on is
		# actually distinguishable from the class default - the regression
		# guard for the ':' separator fix.
		low = Temperature.Celsius(0)
		self.assertFalse(low.showUnit)
		self.assertEqual('0º', str(low))
		self.assertEqual('0ºc', str(low.withUnit))

	def test_dewpoint(self):
		self.assertEqual(self.cDewpoint, self.cRoom.dewpoint(65))
		self.assertEqual(self.fDewpoint, self.fRoom.dewpoint(65))
