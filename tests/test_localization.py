"""Localizing a derived measurement must convert it, not just relabel it.

A `wind = mph` config displayed `0.5 m/s`. Three separate faults stacked, and
each one alone was enough to break it:

1. `wind.py` defined `MilesPerHour`/`MetersPerSecond` but never attached them
   to `Wind` the way `rate.py` attaches its own. `Wind.MilesPerHour` therefore
   resolved by plain inheritance to *DistanceOverTime's* class, whose unit
   type is 'Distance Over Time'. Localization looks the type up in the config
   by name, found no `wind` key, and returned None.

2. With that fixed, the concrete classes were built as
   `class MilesPerHour(Wind, DistanceOverTime.MilesPerHour)`. The metaclass
   took the numerator from the *first* base with one - the generic `<Length>`
   from Wind - rather than the concrete `Mile`, so the class no longer knew
   which length unit it represented.

3. Which made the relabel visible: `localize` builds the target as
   `unit(self.numerator, self.denominator)`, so with generic types it wrapped
   metres and seconds in a class labelled mph. 0.5 m/s displayed as '0.5 mph'
   instead of '1.1 mph' - a wrong reading, worse than the wrong unit.
"""
from unittest import TestCase

from WeatherUnits import Length, Time, Wind
import WeatherUnits.derived.rate as rate
import WeatherUnits.derived.wind as wind


class TestWindUnitResolution(TestCase):

	def test_wind_owns_its_concrete_units(self):
		# Not DistanceOverTime's - those carry the wrong unit type.
		self.assertIs(wind.MilesPerHour, Wind.MilesPerHour)
		self.assertIs(wind.MetersPerSecond, Wind.MetersPerSecond)

	def test_they_are_typed_as_wind(self):
		# This is the name localization looks up in the config.
		self.assertEqual('Wind', Wind.MilesPerHour.type.name)
		self.assertEqual('Wind', Wind.MetersPerSecond.type.name)


class TestConcreteOverGenericInheritance(TestCase):
	"""A concrete base must win over a generic one, whatever the base order."""

	def test_wind_units_keep_their_concrete_numerator(self):
		for cls, numerator, denominator in (
			(wind.MilesPerHour, 'Mile', 'Hour'),
			(wind.MetersPerSecond, 'Meter', 'Second'),
		):
			with self.subTest(cls=cls.__name__):
				self.assertEqual(numerator, cls._numerator.__name__)
				self.assertEqual(denominator, cls._denominator.__name__)
				self.assertFalse(cls._numerator.isGeneric)

	def test_the_plain_rate_classes_are_unaffected(self):
		self.assertEqual('Mile', rate.MilesPerHour._numerator.__name__)
		self.assertEqual('Meter', rate.MetersPerSecond._numerator.__name__)


class TestLocalizeConverts(TestCase):
	"""The conversion `localize` performs, tested without depending on config.

	The suite runs under si.ini, where `wind = m/s`, so localizing a m/s
	reading correctly returns it unchanged and proves nothing. These build the
	target the same way `localize` does - `unit(self.numerator,
	self.denominator)` - which is where the relabel happened.
	"""

	def _mps(self, value):
		return Wind.MetersPerSecond(Length.Meter(value), Time.Second(1))

	def test_building_the_target_converts_the_parts(self):
		# Exactly what DerivedMeasurement.localize does. With a generic
		# numerator the target wrapped metres in a class labelled mph and
		# reported 0.5; with the concrete Mile it converts.
		w = self._mps(0.5)
		built = wind.MilesPerHour(w.numerator, w.denominator)
		self.assertEqual('mph', built.unit)
		self.assertAlmostEqual(1.1185, float(built), places=3)

	def test_it_matches_the_hand_written_conversion(self):
		w = self._mps(0.5)
		self.assertAlmostEqual(float(w.mih), float(wind.MilesPerHour(w.numerator, w.denominator)), places=6)

	def test_a_range_of_readings(self):
		for mps, mph in ((0.0, 0.0), (0.5, 1.1185), (0.9, 2.0133), (10.0, 22.3694)):
			with self.subTest(mps=mps):
				w = self._mps(mps)
				self.assertAlmostEqual(mph, float(wind.MilesPerHour(w.numerator, w.denominator)), places=3)

	def test_localize_preserves_the_physical_quantity(self):
		"""Whatever unit the config picks, the speed itself must not change.

		Trivially true under si.ini (which localizes wind to m/s); the
		assertion earns its keep under any config that converts.
		"""
		w = self._mps(0.5)
		self.assertAlmostEqual(0.5, float(w.localize.ms), places=6)


def test_reading_a_new_config_drops_the_cached_unit(tmp_path):
	"""A class's localised unit follows the file read last, not whichever was current when it was first asked."""
	import WeatherUnits as wu
	from WeatherUnits.config import config
	miles, kilometres = tmp_path / 'miles.ini', tmp_path / 'km.ini'
	miles.write_text('[Units]\nlength = mi\n')
	kilometres.write_text('[Units]\nlength = km\n')
	original = config.path
	try:
		config.read(str(miles))
		assert wu.Length.localizedUnit is wu.Length.Mile
		config.read(str(kilometres))
		assert wu.Length.localizedUnit is wu.Length.Kilometer
	finally:
		config.read(str(original))
