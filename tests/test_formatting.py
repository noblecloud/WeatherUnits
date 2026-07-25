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

	def test_the_derived_width_is_still_the_default(self):
		"""The gap this used to pin is now closed - see TestTrailingZeros.

		This test previously documented a KNOWN GAP: 30.0 rendered '30', so a
		live pressure readout drifted between '29.9', '30' and '30.1', and
		the two declared-but-unconsumed options meant to fix it
		(`trailing_zero`, `force_precision`) did nothing. Both have since
		been replaced by a single `trailing_zeros` option.

		What remains true - and is what this test now guards - is that the
		*default* is still the value-derived width. Opting into a stable
		width is deliberate, so nobody's existing output changed underneath
		them.
		"""
		self.assertEqual('30 inHg', str(Pressure.InchOfMercury(30.0)))
		self.assertEqual('30.0 inHg', format(Pressure.InchOfMercury(30.0), 'precision=2, digit_budget=5'))
		# ...and the fix is one parameter away.
		self.assertEqual(
			'30.00 inHg',
			format(Pressure.InchOfMercury(30.0), 'precision=2, digit_budget=5, trailing_zeros=precision'),
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


class TestDimensionlessSpacing(TestCase):
	"""A unit spacer before an empty unit is a separator between nothing.

	`__format_template__` gated the spacer on `unit is not False`, which an
	empty string passes, so every dimensionless value carried a trailing
	space: 'S ', '5 ', '180° '. Invisible in a terminal, visible the moment
	the string is centred in a dashboard panel or compared for equality.
	"""

	def test_dimensionless_values_have_no_trailing_space(self):
		from WeatherUnits import Light
		from WeatherUnits.others import Angle, Direction
		for measurement, expected in (
			(Direction(180), 'S'),
			(Angle(45), '45°'),
			(Light.UVI(5), '5'),
		):
			with self.subTest(measurement=repr(measurement)):
				self.assertEqual(expected, str(measurement))

	def test_units_that_do_exist_keep_their_spacer(self):
		self.assertEqual('4.1 mph', str(Wind.MilesPerHour(4.1)))
		self.assertEqual('100 lux', str(Light.Lux(100)))


class TestDirectionCardinal(TestCase):
	"""`cardinal` and `shorten` were both inert on Direction.

	Two independent causes, both worth pinning:

	1. `getFrom` used the caller's `default` as the per-object miss
	   sentinel, so the *first* mapping searched returned it and every
	   later mapping was unreachable. `cardinal=False` in a spec could
	   never beat the class's own `show_cardinal`.
	2. `Cardinal.__format_value__` read `self.shorten` and ignored the
	   params entirely, so a spec could not ask for the full name.
	"""

	def test_cardinal_false_renders_degrees(self):
		from WeatherUnits.others import Direction
		d = Direction(180)
		self.assertEqual('S', format(d, 'cardinal=True'))
		self.assertEqual('180°', format(d, 'cardinal=False'))
		self.assertEqual('180°', format(d, 'cardinal: False'))

	def test_shorten_selects_letters_vs_words(self):
		from WeatherUnits.others import Direction
		self.assertEqual('S', format(Direction(180), 'shorten=True'))
		self.assertEqual('South', format(Direction(180), 'shorten=False'))

	def test_the_character_budget_picks_the_compass_resolution(self):
		"""Two independent axes: `shorten` picks the form, the budget the detail.

		Formatting used to call `abbrivated`/`full` directly, jumping to the
		ends of the ladder and leaving every rung between them unreachable -
		budgets 5 through 8 could never produce the word forms.
		"""
		from WeatherUnits.others import Direction
		expected = {
			1: ['N', 'N',   'N',  'E', 'S',  'S', 'S',  'W',   'N'],
			2: ['N', 'N',   'NE', 'E', 'SE', 'S', 'SW', 'W',   'NW'],
			3: ['N', 'NNE', 'NE', 'E', 'SE', 'S', 'SW', 'WSW', 'NW'],
		}
		degrees = (0, 22.5, 45, 90, 135, 180, 225, 247.5, 315)
		for budget, wanted in expected.items():
			for deg, want in zip(degrees, wanted):
				with self.subTest(budget=budget, degrees=deg):
					d = Direction(deg)
					d._digit_budget = budget
					self.assertEqual(want, format(d, 'shorten=True'))

	def test_a_one_character_budget_never_emits_two_characters(self):
		"""The 4-point rung was missing entirely.

		Below a 3-char budget everything fell to the 8-point `twoLetter`
		set, so a 1-character budget still returned 'NE'.
		"""
		from WeatherUnits.others import Direction
		for deg in (0, 45, 90, 135, 180, 225, 270, 315):
			with self.subTest(degrees=deg):
				d = Direction(deg)
				d._digit_budget = 1
				self.assertEqual(1, len(format(d, 'shorten=True')))

	def test_a_word_counts_as_a_digit(self):
		"""The budget counts compass *components*, whatever the atom.

		A letter when abbreviated, a word when spelled out - so the same
		budget carries the same amount of information in either form.
		The old parallel word list broke this: it spelled the 2-component
		'NE' as the single word 'Northeast' and the 3-component 'SSW' as
		the 2-word 'South Southwest'.
		"""
		from WeatherUnits.others import Direction
		# 238 deg is the useful probe: it resolves to a different heading at
		# every rung, so all three budgets are genuinely exercised.
		expected = {
			1: ('W',   'West'),
			2: ('SW',  'South West'),
			3: ('WSW', 'West South West'),
		}
		for budget, (letters, words) in expected.items():
			d = Direction(238)
			d._digit_budget = budget
			with self.subTest(budget=budget):
				self.assertEqual(letters, format(d, 'shorten=True'))
				self.assertEqual(words, format(d, 'shorten=False'))
				self.assertEqual(budget, len(words.split()))

	def test_the_budget_is_a_cap_not_a_quota(self):
		"""A heading that lands on a cardinal doesn't pad to fill the budget.

		202.5 deg is SSW, but at a 2-component budget the nearest 8-point
		heading is plain 'S' - one letter against a budget of two. Nothing
		should stretch it to two.
		"""
		from WeatherUnits.others import Direction
		d = Direction(202.5)
		d._digit_budget = 2
		self.assertEqual('S', format(d, 'shorten=True'))
		self.assertEqual('South', format(d, 'shorten=False'))

		for deg in range(0, 360, 15):
			for budget in (1, 2, 3):
				d = Direction(deg)
				d._digit_budget = budget
				with self.subTest(degrees=deg, budget=budget):
					self.assertLessEqual(len(format(d, 'shorten=True')), budget)
					self.assertLessEqual(len(format(d, 'shorten=False').split()), budget)

	def test_both_forms_name_the_same_heading(self):
		"""Letters and words must never disagree about which way the wind blows."""
		from WeatherUnits.others import Direction
		initial = {'N': 'North', 'E': 'East', 'S': 'South', 'W': 'West'}
		for deg in range(0, 360, 15):
			for budget in (1, 2, 3):
				d = Direction(deg)
				d._digit_budget = budget
				with self.subTest(degrees=deg, budget=budget):
					letters = format(d, 'shorten=True')
					words = format(d, 'shorten=False')
					self.assertEqual(
						[initial[c] for c in letters], words.split(),
						f'{letters!r} and {words!r} disagree',
					)

	def test_default_is_abbreviated_cardinal(self):
		from WeatherUnits.others import Direction
		self.assertEqual('S', str(Direction(180)))


class TestTrailingZeros(TestCase):
	"""`trailing_zeros` overrides the value-derived precision with a stable width.

	`precision` is normally derived per value from that value's own decimal
	content, so 29.92 renders '29.9' but 30.0 renders '30'. For a readout
	glanced at rather than read, that instability is the defect: the panel
	width jumps as the value crosses a whole number.

	This replaces the two declared-but-never-consumed booleans that used to
	sit here, `trailing_zero` and `force_precision`, which overlapped and
	neither of which did anything.
	"""

	def test_off_is_the_default_and_changes_nothing(self):
		self.assertEqual('30 inHg', str(Pressure.InchOfMercury(30.0)))
		self.assertEqual('29.9 inHg', str(Pressure.InchOfMercury(29.92)))
		self.assertEqual(
			format(Pressure.InchOfMercury(30.0), 'precision=2, digit_budget=5'),
			format(Pressure.InchOfMercury(30.0), 'precision=2, digit_budget=5, trailing_zeros=off'),
		)

	def test_precision_pads_to_the_configured_precision(self):
		v = Pressure.InchOfMercury(30.0)
		self.assertEqual('30.00 inHg', format(v, 'precision=2, digit_budget=5, trailing_zeros=precision'))
		self.assertEqual('30.000 inHg', format(v, 'precision=3, digit_budget=6, trailing_zeros=precision'))

	def test_fill_pads_to_whatever_the_budget_allows(self):
		v = Pressure.InchOfMercury(30.0)
		self.assertEqual('30.000 inHg', format(v, 'precision=2, digit_budget=5, trailing_zeros=fill'))
		self.assertEqual('30.0 inHg', format(v, 'precision=2, digit_budget=3, trailing_zeros=fill'))

	def test_an_integer_asks_for_exactly_that_many_places(self):
		v = Pressure.InchOfMercury(30.0)
		self.assertEqual('30.0 inHg', format(v, 'digit_budget=6, trailing_zeros=1'))
		self.assertEqual('30.0000 inHg', format(v, 'digit_budget=6, trailing_zeros=4'))

	def test_the_digit_budget_still_wins(self):
		"""Padding must never push a value over its budget."""
		v = Pressure.InchOfMercury(30.0)
		for mode in ('precision', 'fill', '9'):
			with self.subTest(trailing_zeros=mode):
				# 2 integer digits against a 3-digit budget leaves room for 1.
				self.assertEqual('30.0 inHg', format(v, f'precision=4, digit_budget=3, trailing_zeros={mode}'))

	def test_width_is_stable_across_a_whole_number_crossing(self):
		"""The actual complaint: a live readout must not change width."""
		spec = 'precision=2, digit_budget=5, trailing_zeros=precision, show_unit=False'
		widths = {len(format(Pressure.InchOfMercury(x), spec)) for x in (29.9, 29.95, 30.0, 30.05, 30.1)}
		self.assertEqual(1, len(widths), f'widths varied: {widths}')

	def test_it_composes_with_a_dropped_leading_zero(self):
		# The zero is dropped for budget, which frees a digit - and `fill`
		# must spend the freed digit rather than the one already spent.
		self.assertEqual(
			'.04',
			format(Length.Inch(0.04), 'precision=2, digit_budget=2, trailing_zeros=fill, show_unit=False'),
		)

	def test_true_is_an_alias_for_precision(self):
		v = Pressure.InchOfMercury(30.0)
		self.assertEqual(
			format(v, 'precision=2, digit_budget=5, trailing_zeros=precision'),
			format(v, 'precision=2, digit_budget=5, trailing_zeros=True'),
		)


class TestUnitPropertiesBinding(TestCase):
	"""`[UnitProperties]` keys must bind by unit symbol, not just class name.

	The metaclass gated config lookup on `name.lower() in unitPropertiesKeys`
	where `name` is the CLASS name, so `MillimeterOfMercury` never matched the
	key `mmHg` and that whole config line was silently ignored. Keys that
	happen to coincide with a class name (`temperature`, `direction`) bound
	fine, which is what made the section look like it worked.

	It then re-resolved the key with get_close_matches(cutoff=0.3) and took
	the first hit, so it could apply a *different* unit's settings than the
	one that passed the check.
	"""

	def test_a_symbol_keyed_unit_gets_its_config(self):
		# si.ini: mmHg = precision=2, digit_budget=5, trailing_zeros=precision
		m = Pressure.MillimeterOfMercury(760.0)
		self.assertEqual(2, m._precision)
		self.assertEqual(5, m._digit_budget)
		self.assertEqual('760.00 mmHg', str(m))

	def test_lookup_is_exact_not_fuzzy(self):
		from WeatherUnits.config import config
		self.assertEqual('mmHg', config.unitPropertiesKeyFor('MillimeterOfMercury', 'mmHg'))
		self.assertEqual('mmHg', config.unitPropertiesKeyFor('mmhg'))          # case-insensitive
		self.assertIsNone(config.unitPropertiesKeyFor('MillimeterOfMercury'))  # class name alone: no key
		self.assertIsNone(config.unitPropertiesKeyFor('mmH'))                  # near miss must NOT match
		self.assertIsNone(config.unitPropertiesKeyFor(None))

	def test_class_name_keys_still_bind(self):
		# `direction` and `temperature` matched by class name before and must
		# keep matching - this is the half that always worked.
		from WeatherUnits.others import Direction
		self.assertEqual(3, Direction(180)._digit_budget)


class TestRefitCarriesTheTargetUnitsConfig(TestCase):
	"""A refit changes the unit, so it must change the settings too.

	`params.default` is captured from the original measurement before
	`shorten`/`bestFit` swaps in a different unit. Without refreshing it, a
	Hectopascal displayed as mmHg was formatted with Hectopascal's precision
	and trailing_zeros while wearing mmHg's label - the same value rendered
	differently depending on which unit you happened to start from.
	"""

	def test_both_routes_to_the_same_reading_agree(self):
		converted = str(Pressure.Hectopascal(1013.25).withUnit)
		direct = str(Pressure.MillimeterOfMercury(760.0))
		self.assertEqual('760.00 mmHg', converted)
		self.assertEqual(converted, direct)
