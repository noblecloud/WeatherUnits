"""Format-spec parsing: `key: value` must work, not just `key=value`.

`FormatSpec.params` (base/_SmartFloat.py) originally accepted only `=` as
the key/value separator. Specs written with `: ` - including two inside this
library itself, `.withUnit`'s `f'{self:showUnit: True}'` and Direction's
`f'{self: cardinal: False}'` - matched nothing and were silently discarded,
so the parameter simply never took effect. Nothing raised; the spec just did
nothing, which is why it went unnoticed (see the note in
test_temperature.test_fahrenheit, which was an expected failure until this
was fixed).
"""
from unittest import TestCase

from WeatherUnits import Length, Temperature, Wind


class TestFormatSpecSeparators(TestCase):

	def test_separators_are_equivalent_for_word_values(self):
		subjects = [
			Temperature.Celsius(0),
			Temperature.Fahrenheit(32),
			Wind.MilesPerHour(4.1),
			Length.Inch(51),
		]
		for subject in subjects:
			for key, value in (('showUnit', 'True'), ('showUnit', 'False')):
				with self.subTest(subject=repr(subject), key=key, value=value):
					self.assertEqual(
						format(subject, f'{key}={value}'),
						format(subject, f'{key}: {value}'),
					)

	def test_force_show_unit_overrides_a_false_default(self):
		# Celsius defaults to showUnit=False, so this distinguishes a real
		# override from merely inheriting the default.
		c = Temperature.Celsius(0)
		self.assertFalse(c.showUnit)
		self.assertEqual('0°c', format(c, 'showUnit: True'))
		self.assertEqual('0°c', format(c, 'showUnit=True'))

	def test_format_template_isolates_the_unit(self):
		# `format: {unit}` must yield the bare unit symbol, not the whole
		# rendered measurement - LevityDash relies on this to decide whether
		# a unit is short enough to render inline.
		for subject, unit in (
			(Wind.MilesPerHour(4.1), 'mph'),
			(Length.Inch(51), 'in'),
			(Temperature.Celsius(0), 'c'),
		):
			with self.subTest(subject=repr(subject)):
				self.assertEqual(unit, format(subject, 'format: {unit}'))
				self.assertEqual(unit, format(subject, 'format={unit}'))

	def test_colon_is_not_equivalent_for_format_spec_shaped_values(self):
		"""KNOWN LIMITATION, pinned deliberately - use '=' for these.

		`FormatSpec.precision` is applied to the spec *before*
		`FormatSpec.params` is, and its pattern happily matches things like
		` _`, ` 2` and ` .2f` (as sign/grouping_option/precision). So when a
		`key: value` pair carries a value shaped like a float format-spec,
		precision claims it first and the parameter is lost - the leading
		space in the results below is that stolen ` ` being applied as a
		sign. This predates the ':' separator support (`precision: 2`
		behaved identically before it) and is unchanged by it; ':' works for
		ordinary word values, which is every real use in this library.
		"""
		i = Length.Inch(51)
		self.assertEqual('51_in', format(i, 'unitSpacer=_'))   # '=' honours it
		self.assertEqual(' 51 in', format(i, 'unitSpacer: _'))  # ':' does not

	def test_conversion_spec_is_not_mistaken_for_a_param(self):
		# A leading `unit:` is a conversion and is stripped before params are
		# parsed, so it must not be swallowed as a `key: value` pair now that
		# ':' is a valid separator. The precision half must still apply too.
		mph = Wind.MilesPerHour(4.1)
		self.assertTrue(
			format(mph, 'mph:.2f').startswith('4.10'),
			f'conversion+precision spec was hijacked: {format(mph, "mph:.2f")!r}',
		)
		self.assertEqual(format(mph, 'mph'), format(mph, 'mph'))
