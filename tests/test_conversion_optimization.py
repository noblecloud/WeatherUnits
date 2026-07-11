from unittest import TestCase

from WeatherUnits import Length, Temperature
from WeatherUnits.base import _SmartFloat
from WeatherUnits.base._ScalingMeasurement import _scaleFactor

try:
	import numpy as np
except ImportError:  # pragma: no cover
	np = None


class TestCachedFactorConversion(TestCase):
	"""Task 1 - cached, factor-based multiplicative conversion."""

	def test_scale_factor_is_cached(self):
		first = _scaleFactor(Length.Yard.scale, Length.Foot.scale)
		second = _scaleFactor(Length.Yard.scale, Length.Foot.scale)
		self.assertIs(first, second)
		self.assertEqual(3.0, first)

	def test_change_scale_matches_construction(self):
		yard = Length.Yard(2)
		self.assertEqual(float(Length.Foot(yard)), yard.changeScale(Length.Foot.scale))

	def test_conversion_factor_symmetry(self):
		f = Length.Yard.getConversionFactor(Length.Yard, Length.Foot)
		r = Length.Foot.getConversionFactor(Length.Foot, Length.Yard)
		self.assertAlmostEqual(1.0, f * r)


class TestAffineConversion(TestCase):
	"""Task 2 - (factor, offset) affine conversion accessor."""

	def test_multiplicative_has_zero_offset(self):
		factor, offset = Length.Foot.get_conversion(Length.Yard)
		self.assertEqual(3.0, factor)
		self.assertEqual(0.0, offset)

	def test_temperature_is_affine(self):
		factor, offset = Temperature.Fahrenheit.get_conversion(Temperature.Celsius)
		self.assertAlmostEqual(1.8, factor)
		self.assertAlmostEqual(32.0, offset)

	def test_kelvin_offset(self):
		factor, offset = Temperature.Kelvin.get_conversion(Temperature.Celsius)
		self.assertAlmostEqual(1.0, factor)
		self.assertAlmostEqual(273.15, offset)

	def test_get_conversion_accepts_instance(self):
		fromType = Temperature.Celsius(20)
		self.assertEqual(
			Temperature.Fahrenheit.get_conversion(fromType),
			Temperature.Fahrenheit.get_conversion(Temperature.Celsius),
		)


class TestConvertArray(TestCase):
	"""Task 3 - vectorized array conversion."""

	def _assert_matches_elementwise(self, toUnit, fromUnit, values):
		if np is None:
			self.skipTest('numpy not available')
		expected = [float(toUnit(fromUnit(v))) for v in values]
		result = toUnit.convert_array(np.array(values, dtype='float64'), fromUnit)
		for e, r in zip(expected, result):
			self.assertAlmostEqual(e, r)

	def test_multiplicative_array(self):
		self._assert_matches_elementwise(Length.Foot, Length.Yard, [0.0, 1.0, 2.5, 10.0])

	def test_affine_array(self):
		self._assert_matches_elementwise(Temperature.Fahrenheit, Temperature.Celsius, [-40.0, 0.0, 37.0, 100.0])

	def test_affine_array_kelvin(self):
		self._assert_matches_elementwise(Temperature.Kelvin, Temperature.Celsius, [-273.15, 0.0, 100.0])

	def test_default_from_unit_is_identity(self):
		if np is None:
			self.skipTest('numpy not available')
		values = np.array([1.0, 2.0, 3.0])
		result = Length.Foot.convert_array(values)
		for v, r in zip(values, result):
			self.assertAlmostEqual(float(v), r)


class TestLazyFormattingGuard(TestCase):
	"""Task 5 - bulk conversion must never trigger presentation cost."""

	def test_convert_array_does_not_format(self):
		if np is None:
			self.skipTest('numpy not available')
		calls = {'count': 0}
		original = _SmartFloat.SmartFloat._string

		def counting_string(self, *args, **kwargs):
			calls['count'] += 1
			return original(self, *args, **kwargs)

		_SmartFloat.SmartFloat._string = counting_string
		try:
			Temperature.Fahrenheit.convert_array(np.arange(1000, dtype='float64'), Temperature.Celsius)
		finally:
			_SmartFloat.SmartFloat._string = original
		self.assertEqual(0, calls['count'])
