from unittest import TestCase
from WeatherUnits import Light

Lux = Light.Lux

class TestLux(TestCase):
	zero = Lux(0)
	oneHundred = Lux(100)
	oneThousand = Lux(1054)
	oneMillion = Lux(1024581)

	def test_zero(self):
		self.assertEqual(float(self.zero), 0)
		self.assertEqual(self.zero.unit, 'lux')
		self.assertEqual(str(self.zero.withUnit), '0 lux')

	def test_oneHundred(self):
		self.assertEqual(float(self.oneHundred), 100)
		self.assertEqual(self.oneHundred.unit, 'lux')
		self.assertEqual(str(self.oneHundred.withUnit), '100 lux')

	def test_oneThousand(self):
		self.assertEqual(float(self.oneThousand), 1054)
		self.assertEqual(self.oneThousand.unit, 'lux')
		# 1054 scaled and shortened renders with three significant figures
		self.assertEqual(str(self.oneThousand.withUnit), '1.05k lux')

	def test_oneMillion(self):
		self.assertEqual(float(self.oneMillion), 1024581)
		self.assertEqual(self.oneMillion.unit, 'lux')

	def test_add(self):
		self.assertEqual(self.oneHundred + self.oneThousand, Lux(1154))
		self.assertEqual(self.oneHundred + self.oneMillion, Lux(1024681))
		self.assertEqual(self.oneThousand + self.oneMillion, Lux(1025635))
		self.assertEqual(self.oneMillion + self.oneMillion, Lux(2049162))

	def test_subtract(self):
		self.assertEqual(self.oneHundred - self.oneThousand, Lux(-954))
		self.assertEqual(self.oneThousand - self.oneHundred, Lux(954))
