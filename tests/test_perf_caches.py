from unittest import TestCase

from WeatherUnits import Length


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
