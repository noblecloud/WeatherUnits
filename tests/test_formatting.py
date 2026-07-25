"""Display invariants - what a measurement actually renders as.

The rest of the suite covers conversion arithmetic; this file pins the
*rendered strings*, which is what users and downstream consumers (LevityDash
renders every dashboard value through this library) actually see. Before
this file there were 19 string assertions in the whole suite, only 5 of them
involving decimals.

See docs/formatting.md for the model these assertions encode: `max` is the
total number of *displayed digits* - a width budget that, together with
`shorten`, decides when a value is rescaled to fit (changing the unit or
adding a k/m suffix). `precision` fills whatever room `max` leaves, derived
per value from that value's own decimal content.

Assertions here reflect the **US config** (config/us.ini); `shorten` in
particular differs under si.ini.
"""
from unittest import TestCase

from WeatherUnits import Length, Light, Mass, Pressure, Temperature, Wind


class TestZeroValues(TestCase):
	"""Zero renders bare - never '0.0'."""

	def test_zero_has_no_trailing_decimal(self):
		for measurement, expected in (
			(Pressure.InchOfMercury(0), '0 inHg'),
			(Light.Lux(0), '0 lux'),
			(Length.Inch(0), '0 in'),
			(Wind.MilesPerHour(0), '0 mph'),
			(Mass.Gram(0), '0 g'),
		):
			with self.subTest(measurement=repr(measurement)):
				self.assertEqual(expected, str(measurement))

	def test_zero_temperature_keeps_its_decorator(self):
		self.assertEqual('0°', str(Temperature.Fahrenheit(0)))
		self.assertEqual('0°', str(Temperature.Celsius(0)))


class TestPrecisionAndMax(TestCase):
	"""`max` is a significant-digit budget; precision follows the value."""

	def test_decimals_are_kept_within_the_digit_budget(self):
		for measurement, expected in (
			(Pressure.InchOfMercury(29.92), '29.9 inHg'),   # 3 digits -> 1 decimal
			(Pressure.InchOfMercury(30.5), '30.5 inHg'),
			(Wind.MilesPerHour(4.1), '4.1 mph'),
			(Wind.MilesPerHour(12.75), '12.8 mph'),         # rounded to fit
			(Length.Inch(1.25), '1.2 in'),
			(Length.Inch(0.5), '0.5 in'),
			(Mass.Gram(1.5), '1.5 g'),
		):
			with self.subTest(measurement=repr(measurement)):
				self.assertEqual(expected, str(measurement))

	def test_whole_values_render_without_decimals(self):
		self.assertEqual('51 in', str(Length.Inch(51)))
		self.assertEqual('100 g', str(Mass.Gram(100)))
		self.assertEqual('100 lux', str(Light.Lux(100)))

	def test_trailing_zero_gap_is_current_behaviour_not_intent(self):
		"""KNOWN GAP, pinned deliberately - see docs/formatting.md.

		A value of exactly 30.0 renders as '30', so a live pressure readout
		drifts between '29.9', '30' and '30.1'. Raising precision/max does
		not help, because precision is capped by the value's own decimals.
		Two declared-but-unconsumed options in config/template.ini are the
		intended mechanism: `trailing_zero` ("display zero after decimal
		point to full precision staying under max") and `force_precision`
		("decimals are always displayed within the precision amount").

		When either is implemented, this test SHOULD fail - update it to the
		intended '30.00 inHg' rather than working around it.
		"""
		self.assertEqual('30 inHg', str(Pressure.InchOfMercury(30.0)))
		self.assertEqual('30.0 inHg', format(Pressure.InchOfMercury(30.0), 'precision=2, digit_budget=5'))
		# trailing_zero currently has no effect either way
		self.assertEqual(
			format(Pressure.InchOfMercury(30.0), 'trailing_zero=True'),
			format(Pressure.InchOfMercury(30.0), 'trailing_zero=False'),
		)


class TestMaxAppliesBelowOne(TestCase):
	"""`max` used to be inert for values <= 1.

	The type='g' normalization gated its clamping block behind
	`if float(value) > 1`, so the sub-1 branch passed the configured
	precision through unclamped and a 1-digit budget still rendered 3 digits.
	"""

	def test_budget_clamps_decimals_on_small_values(self):
		i = Length.Inch(0.0416)
		self.assertEqual('0', format(i, 'digit_budget=1, show_unit=False'))
		self.assertEqual('0.0', format(i, 'digit_budget=2, show_unit=False'))
		self.assertEqual('0.0', format(i, 'digit_budget=3, show_unit=False'))

	def test_default_rendering_is_unaffected(self):
		# The default budget already matched what these rendered, so nothing
		# users see at default settings changed.
		self.assertEqual('0.5 in', str(Length.Inch(0.5)))
		self.assertEqual('0 in', str(Length.Inch(0)))
		self.assertEqual('100 lux', str(Light.Lux(100)))


class TestLeadingZero(TestCase):
	"""`leading_zero` was declared, documented, and never consumed.

	Three-state, defaulting to 'auto': keep the zero unless keeping it would
	cost a decimal place.
	"""

	def test_auto_keeps_the_zero_when_it_fits(self):
		# 0.5 needs two digits with the zero and the budget allows two, so
		# there is nothing to gain by dropping it.
		self.assertEqual('0.5', format(Length.Inch(0.5), 'digit_budget=2, show_unit=False'))
		self.assertEqual('0.5', format(Length.Inch(0.5), 'precision=2, digit_budget=2, show_unit=False'))

	def test_auto_drops_the_zero_only_when_the_budget_is_short(self):
		# precision=2 asks for hundredths; with the zero that needs three
		# digits, so a 2-digit budget reclaims it. At digit_budget=3 it fits and the
		# zero stays. This is the shape of the shipped precipitationRate
		# config.
		i = Length.Inch(0.04)
		self.assertEqual('.04', format(i, 'precision=2, digit_budget=2, show_unit=False'))
		self.assertEqual('0.04', format(i, 'precision=2, digit_budget=3, show_unit=False'))

	def test_explicit_true_keeps_it_even_when_that_costs_precision(self):
		i = Length.Inch(0.04)
		self.assertEqual('0.0', format(i, 'precision=2, digit_budget=2, leading_zero=True, show_unit=False'))

	def test_explicit_false_drops_it_even_when_it_would_have_fit(self):
		self.assertEqual('.5', format(Length.Inch(0.5), 'digit_budget=2, leading_zero=False, show_unit=False'))

	def test_zero_is_not_spent_when_dropping_it_rescues_nothing(self):
		"""Second clause of the auto rule - the easy one to lose.

		At a 1-digit budget, 0.0416 renders '0' with the zero and '.0'
		without: equally empty. Dropping buys nothing, so the zero stays.
		An implementation that only asks "would keeping it show zero?"
		returns '.0' here.
		"""
		self.assertEqual('0', format(Length.Inch(0.0416), 'digit_budget=1, show_unit=False'))

	def test_zero_is_not_spent_to_buy_a_trailing_digit(self):
		"""First clause of the auto rule - guards a plausible wrong version.

		Keying off the *configured* precision rather than what the value
		needs drops the zero whenever `max - intLength < precision`. That
		spends it on a trailing zero carrying no information: 0.5 renders
		'.50' and 0.9697 renders '.970' - same digit count, strictly worse
		to read. Both must keep their leading zero.
		"""
		self.assertEqual('0.5', format(Length.Inch(0.5), 'precision=2, digit_budget=2, show_unit=False'))
		self.assertEqual('0.97 mi', str(Length.Foot(5120)))

	def test_negative_sub_one_values_keep_their_sign(self):
		self.assertEqual('-.5 in', format(Length.Inch(-0.5), 'leading_zero=False'))

	def test_values_at_or_above_one_are_untouched(self):
		for value in (1.0, 1.25, 12.75):
			with self.subTest(value=value):
				self.assertEqual(
					format(Length.Inch(value), 'leading_zero=True'),
					format(Length.Inch(value), 'leading_zero=False'),
				)

	def test_zero_is_untouched(self):
		# Exactly zero has no fractional part to expose; stripping would
		# leave a bare '.'.
		self.assertEqual('0 in', format(Length.Inch(0), 'leading_zero=False'))


class TestDegreeSign(TestCase):
	"""The degree unit_symbol must be U+00B0, not the ordinal indicator.

	The codebase previously used '°' MASCULINE ORDINAL INDICATOR - a
	Spanish/Portuguese ordinal marker (1° = "primero") that many fonts draw
	with an underline, which is how it was noticed. It looks close enough to
	a degree sign to survive years unremarked, but it is a different
	character: screen readers announce it as an ordinal rather than
	"degrees", and it renders inconsistently across fonts.

	The two were also mixed - Temperature and Angle carried U+00BA while
	Direction's _id already used U+00B0. Pinned here because the difference
	is invisible in a diff.
	"""

	# Escapes, not literals: the two glyphs are visually near-identical, so
	# spelling out the codepoints is the only way this test states its own
	# intent legibly - and it keeps the file safe to bulk-normalize.
	DEGREE = '\u00b0'   # DEGREE SIGN
	ORDINAL = '\u00ba'  # MASCULINE ORDINAL INDICATOR

	def test_temperature_decorator_is_the_degree_sign(self):
		for cls in (Temperature.Celsius, Temperature.Fahrenheit):
			with self.subTest(cls=cls.__name__):
				self.assertEqual(self.DEGREE, cls(0).unit_symbol)

	def test_rendered_temperature_uses_the_degree_sign(self):
		rendered = str(Temperature.Celsius(0))
		self.assertIn(self.DEGREE, rendered)
		self.assertNotIn(self.ORDINAL, rendered)

	def test_angle_and_direction_use_the_degree_sign(self):
		from WeatherUnits.others import Angle, Direction
		for cls in (Angle, Direction):
			with self.subTest(cls=cls.__name__):
				self.assertEqual(self.DEGREE, cls(0).unit_symbol)

	def test_no_ordinal_indicator_survives_anywhere_in_the_package(self):
		# Cheap guard against it creeping back in via a copy-paste.
		import pathlib
		import WeatherUnits
		root = pathlib.Path(WeatherUnits.__file__).parent
		offenders = []
		for path in list(root.rglob('*.py')) + list(root.rglob('*.ini')):
			if '__pycache__' in str(path):
				continue
			try:
				if self.ORDINAL in path.read_text():
					offenders.append(str(path.relative_to(root)))
			except (UnicodeDecodeError, OSError):
				continue
		self.assertEqual([], offenders, f'U+00BA found in: {offenders}')


class TestDecoratorAndSpacer(TestCase):
	"""Two shapes: unit_symbol-no-spacer, and spacer-no-unit_symbol."""

	def test_temperature_uses_a_decorator_and_no_spacer(self):
		f = Temperature.Fahrenheit(32)
		self.assertEqual('°', f.unit_symbol)
		self.assertEqual('', f.unit_spacer)
		self.assertEqual('32°', str(f))

	def test_wind_uses_a_spacer_and_no_decorator(self):
		w = Wind.MilesPerHour(4.1)
		self.assertEqual('', w.unit_symbol)
		self.assertEqual(' ', w.unit_spacer)
		self.assertEqual('4.1 mph', str(w))

	def test_unit_spacer_is_a_string_not_a_flag(self):
		# `unit_spacer=True` renders the literal word - documented gotcha.
		k = Temperature.Kelvin(273.15)
		self.assertEqual('273_k', format(k, 'unit_spacer=_'))
		self.assertEqual('273Truek', format(k, 'unit_spacer=True'))


class TestShowUnit(TestCase):

	def test_with_and_without_unit(self):
		c = Temperature.Celsius(0)
		self.assertEqual('0°', str(c))
		self.assertEqual('0°c', str(c.withUnit))
		self.assertEqual('0°', str(c.withoutUnit))

	def test_show_unit_parameter_both_separators(self):
		c = Temperature.Celsius(0)
		self.assertEqual('0°c', format(c, 'show_unit=True'))
		self.assertEqual('0°c', format(c, 'show_unit: True'))


class TestFloatTypeCodes(TestCase):
	"""`type`/`fill`/`align` are exempt from boolean coercion."""

	def test_single_letter_type_codes_are_not_coerced_to_bool(self):
		# 'f' and 'n' are members of FormatSpec.falsy_values; before they
		# were exempted they became False and reached the float format spec
		# as '.2False' -> ValueError.
		p = Pressure.InchOfMercury(29.92)
		self.assertEqual('29.9 inHg', format(p, 'type=f'))
		self.assertEqual('3e+01 inHg', format(p, 'type=n'))
		self.assertEqual('29.9 inHg', format(p, 'type=g'))

	def test_keys_that_are_not_exempt_still_take_false(self):
		# False must keep meaning "disable this" for these.
		self.assertEqual('4.1mph', format(Wind.MilesPerHour(4.1), 'unit_spacer=False'))
		self.assertEqual('4.1', format(Wind.MilesPerHour(4.1), 'show_unit=False'))


class TestShortenAndBestFit(TestCase):

	def test_shorten_can_change_the_unit_entirely(self):
		# Not just the magnitude - the rendered unit changes too.
		self.assertEqual('497.66 psi', str(Pressure.InchOfMercury(1013.25)))
		self.assertEqual('1.234 km', str(Length.Meter(1234.5)))

	def test_scale_factor_suffixes(self):
		self.assertEqual('1.05k lux', str(Light.Lux(1054)))
		self.assertEqual('1.0246m lux', str(Light.Lux(1024581)))

	def test_values_are_rescaled_to_fit_the_max_digit_budget(self):
		# `max` is a display-width budget: when a value needs more digits
		# than it allows, `shorten` rescales to fit - either by suffix or by
		# refitting to a larger unit.
		self.assertEqual('1.00k lux', str(Light.Lux(1000)))       # suffix
		# 5120 ft best-fits to 0.9697 mi, which is sub-1 - the branch that
		# used to ignore `max`. It rendered '0.970 mi': four digit characters
		# on Length's 3-digit budget, the last carrying no information.
		self.assertEqual('0.97 mi', str(Length.Foot(5120)))       # unit refit
