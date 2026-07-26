"""`SmartFloat._string` — the keyword-argument formatting path.

Deliberately kept as an alternative to `__format__`: that one takes a spec
*string* which must be parsed and validated, while this takes the same knobs
as plain keywords, which is cheaper when a caller already holds them as
values (a plugin schema carrying its own formatting settings, say).

It has no production caller, which is exactly why it needs tests. The
snake_case rename renamed this method's local `decorator` to `unit_symbol`
inside the f-string but not in the signature, so every call raised
`NameError: name 'unit_symbol' is not defined` - undetected, because nothing
called it. These assertions are cheap insurance against the next such edit.
"""
from unittest import TestCase

from WeatherUnits import Length, Temperature
from WeatherUnits.others import Angle, Direction


class TestStringRenders(TestCase):
	"""The bar is low and deliberate: it must not raise, and must be a str."""

	def test_it_runs_for_every_shape_of_unit(self):
		for measurement in (
			Temperature.Fahrenheit(72.5),   # unit symbol, no unit string
			Length.Inch(51),                # unit string, no symbol
			Length.Meter(1234.5),           # scaling unit
			Angle(45),                      # dimensionless
			Direction(180),                 # dimensionless + cardinal
		):
			with self.subTest(measurement=repr(measurement)):
				result = measurement._string()
				self.assertIsInstance(result, str)
				self.assertTrue(result)

	def test_defaults_match_the_unit(self):
		self.assertEqual('72°', Temperature.Fahrenheit(72.5)._string())
		self.assertEqual('51 in', Length.Inch(51)._string())


class TestStringKeywords(TestCase):
	"""Each keyword must actually reach the output."""

	def test_unit_toggles_the_unit_string(self):
		self.assertEqual('51 in', Length.Inch(51)._string(unit=True))
		self.assertEqual('51', Length.Inch(51)._string(unit=False))

	def test_unit_symbol_is_overridable(self):
		# The parameter the rename broke. Named to match the library-wide
		# `decorator` -> `unit_symbol` rename.
		self.assertEqual('180DEG', Direction(180)._string(unit_symbol='DEG'))

	def test_prefix_and_suffix(self):
		self.assertEqual('~51 in', Length.Inch(51)._string(prefix='~'))
		self.assertEqual('51* in', Length.Inch(51)._string(suffix='*'))

	def test_format_spec_controls_the_number(self):
		self.assertEqual('180°', Direction(180.4)._string(unit=False, formatSpec='.0f'))


class TestStringSpacing(TestCase):

	def test_no_spacer_before_an_empty_unit(self):
		# Same rule as __format_template__: nothing to separate means no
		# separator. These rendered '180° ' and '45° ' with a trailing space.
		self.assertEqual('180°', Direction(180)._string())
		self.assertEqual('45°', Angle(45)._string())

	def test_a_real_unit_keeps_its_spacer(self):
		self.assertEqual('51 in', Length.Inch(51)._string())


class TestDecoratedInt(TestCase):
	"""`Direction.decoratedInt` - _string's only in-tree caller."""

	def test_it_renders_an_integer_with_its_symbol(self):
		# It passed `forceUnit=`/`asInt=`, neither of which is a parameter,
		# so it raised TypeError for anyone who called it.
		self.assertEqual('180°', Direction(180.4).decoratedInt)
		self.assertEqual('46°', Direction(45.6).decoratedInt)


class TestSeparatorOverrides(TestCase):
	"""`grouping_character` / `radix_character` come from the config, once.

	They are a property of the locale - they change when someone moves
	country, not between values - so they are resolved at config load rather
	than consulted while rendering. The old `Config.groupingCharacter`
	property was the per-render form of this and was never read by anything;
	it is gone.
	"""

	def test_defaults_come_from_the_locale(self):
		from WeatherUnits.config import GROUPING_CHAR, RADIX_CHAR
		# Whatever the locale says, both must be single non-empty characters -
		# they are interpolated into FormatSpec.number's character classes,
		# where an empty value would silently change what that regex matches.
		self.assertEqual(1, len(GROUPING_CHAR))
		self.assertEqual(1, len(RADIX_CHAR))
		self.assertNotEqual(GROUPING_CHAR, RADIX_CHAR)

	def test_the_removed_property_is_really_gone(self):
		from WeatherUnits.config import config
		self.assertFalse(hasattr(type(config), 'groupingCharacter'))
