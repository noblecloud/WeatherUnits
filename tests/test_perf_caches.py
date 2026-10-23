from unittest import TestCase

from unitcorn import Length


class TestUnitNamesCache(TestCase):
	def test_matches_compatible_units(self):
		self.assertEqual(Length.unitNames, frozenset(Length.compatibleUnits) | {'auto'})

	def test_new_subclass_invalidates(self):
		before = Length.unitNames
		self.assertNotIn('zzfurlong', before)

		class Zzfurlong(Length.Foot):
			_unit = 'zzfurlong'

		self.assertIn('zzfurlong', Length.unitNames)
		self.assertEqual(Length.unitNames, frozenset(Length.compatibleUnits) | {'auto'})

	def test_reassigned_unit_invalidates(self):
		meter = Length.Meter
		original = meter._unit
		try:
			meter._unit = 'zzmeter'
			self.assertIn('zzmeter', Length.unitNames)
		finally:
			meter._unit = original
		self.assertNotIn('zzmeter', Length.unitNames)


class TestSpecParseCache(TestCase):
	def test_repeat_and_interleaved_specs_are_stable(self):
		from unitcorn import Temperature
		c = Temperature.Celsius(21.345)
		specs = ['', 'precision=2', 'precision=1, show_unit=False', 'precision=0, type=f']
		first = [format(c, s) for s in specs]
		for _ in range(3):
			self.assertEqual([format(c, s) for s in reversed(specs)][::-1], first)

	def test_spec_param_values_are_not_shared_between_calls(self):
		from unitcorn.base._SmartFloat import _parseSpec
		_, a = _parseSpec('precision=2', 'C')
		self.assertEqual(a, {'precision': 2})
		_, b = _parseSpec('precision=2', 'C')
		self.assertIs(a, b)  # shared on purpose; __format__ copies before use
