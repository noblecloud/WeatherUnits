"""Strict unit lookup: `lookup`, `parse`, `suggest`, `UnknownUnit`, `AmbiguousUnit`.

The point of the strict front door is that a unit string either names exactly
one unit or raises. The tables here list one outcome per row, and no row may
fall back: a class, `UnknownUnit` or `AmbiguousUnit`.
"""
from pathlib import Path
from unittest import TestCase

import unitcorn as uc
from unitcorn import AmbiguousUnit, UnknownUnit

Celsius = uc.Temperature.Celsius
Fahrenheit = uc.Temperature.Fahrenheit
Kelvin = uc.Temperature.Kelvin

UNKNOWN = UnknownUnit
AMBIGUOUS = AmbiguousUnit

# (text, dimension, outcome)
LOOKUPS = [
	# Temperature. The brief's "problems": degC was Decade, °C was CelsiusChange
	('degC', None, Celsius),
	('°C', None, Celsius),
	('° C', None, Celsius),
	('deg C', None, Celsius),
	('℃', None, Celsius),
	('celsius', None, Celsius),
	('Celsius', None, Celsius),
	('°F', None, Fahrenheit),
	('degF', None, Fahrenheit),
	('K', None, Kelvin),
	('kelvin', None, Kelvin),
	('k', None, UNKNOWN),             # not Kelvin: k is kilo
	('C', None, UNKNOWN),             # coulomb, not Celsius
	('F', None, UNKNOWN),             # farad
	('c', None, UNKNOWN),
	('C', uc.Temperature, Celsius),
	('c', uc.Temperature, Celsius),
	('F', uc.Temperature, Fahrenheit),
	('Δ°C', None, uc.Temperature.CelsiusChange),
	# Percent
	('%', None, uc.Percentage),
	('percent', None, uc.Percentage),
	('%', uc.Percentage, uc.Percentage),
	('%', uc.PartsPer, uc.derived.partsPer.Hundred),
	('ppm', None, uc.derived.partsPer.Million),
	('‰', None, uc.derived.partsPer.Thousand),
	# Time. `ms` was Meter's plural, `m` was always Meter
	('ms', None, uc.Time.Millisecond),
	('ms', uc.Time, uc.Time.Millisecond),
	('ms', uc.Length, UNKNOWN),
	('m', None, AMBIGUOUS),
	('m', uc.Time, AMBIGUOUS),        # Minute or Month: Home Assistant writes months as m
	('mo', uc.Time, uc.Time.Month),
	('mth', None, uc.Time.Month),
	('mins', None, uc.Time.Minute),
	('m', uc.Length, uc.Length.Meter),
	('min', None, uc.Time.Minute),
	('h', None, uc.Time.Hour),
	('hr', None, uc.Time.Hour),
	('hours', None, uc.Time.Hour),
	('d', None, uc.Time.Day),
	('s', None, uc.Time.Second),
	('sec', None, uc.Time.Second),
	('w', None, uc.Time.Week),
	('y', None, uc.Time.Year),
	('ts', None, UNKNOWN),            # was Ton's generated plural
	('cs', None, UNKNOWN),            # was Celsius's generated plural
	# Power, energy
	('W', None, uc.Power.Watt),
	('kW', None, uc.Power.Kilowatt),
	('kWh', None, uc.Energy.KilowattHour),
	('kW·h', None, uc.Energy.KilowattHour),
	('kW*h', None, uc.Energy.KilowattHour),
	('kW h', None, UNKNOWN),
	('J', None, uc.Energy.Joule),
	# Angle
	('°', None, uc.Angle),
	('deg', None, uc.Angle),
	('degrees', None, uc.Angle),
	# Speed units that are not in the library yet
	('kn', None, uc.Wind.Knot),
	('kt', None, uc.Wind.Knot),
	('knot', None, uc.Wind.Knot),
	('knots', None, uc.Wind.Knot),
	('nmi', None, uc.Length.NauticalMile),
	('Beaufort', None, uc.Beaufort),
	('Bft', None, uc.Beaufort),
	('PPFD', None, uc.PPFD),
	('DLI', None, uc.DLI),
	('knotz', None, UNKNOWN),
	# Case: exact first, then case-insensitive only if one unit matches
	('km', None, uc.Length.Kilometer),
	('KM', None, uc.Length.Kilometer),
	('Km', None, uc.Length.Kilometer),
	('mm', None, uc.Length.Millimeter),
	('MM', None, uc.Length.Millimeter),
	('Mm', None, UNKNOWN),            # megameter, which the library does not have
	('mW', None, UNKNOWN),            # milliwatt, not Megawatt
	('mw', None, UNKNOWN),
	('MW', None, uc.Power.Megawatt),
	('Mw', None, uc.Power.Megawatt),
	('hpa', None, uc.Pressure.Hectopascal),
	('HPA', None, uc.Pressure.Hectopascal),
	('MPa', None, uc.pressure.pressure.Megapascal),
	('mpa', None, UNKNOWN),           # millipascal, not MPa
	('w', None, uc.Time.Week),        # exact, so it does not fold to Watt
	('V', None, uc.Others.Voltage if hasattr(uc, 'Others') else uc.Voltage),
	# Unicode and punctuation
	('μg', None, uc.Mass.Microgram),   # Greek mu
	('µg', None, uc.Mass.Microgram),   # micro sign
	('ug', None, uc.Mass.Microgram),
	('m²', None, uc.Area.SquareMeter),
	('m^2', None, uc.Area.SquareMeter),
	('m2', None, uc.Area.SquareMeter),
	('m**2', None, uc.Area.SquareMeter),
	('  hPa ', None, uc.Pressure.Hectopascal),
	# Names, plural names
	('meter', None, uc.Length.Meter),
	('Meters', None, uc.Length.Meter),
	('square meter', None, uc.Area.SquareMeter),
	('Square-Meter', None, uc.Area.SquareMeter),
	('pascal', None, uc.Pressure.Pascal),
	# Unknown for good
	('', None, UNKNOWN),
	('   ', None, UNKNOWN),
	('xyz', None, UNKNOWN),
	('L', None, UNKNOWN),
	('m³', None, UNKNOWN),
	('fl. oz.', None, UNKNOWN),
	# A dimension narrows
	('mi', uc.Length, uc.Length.Mile),
	('mi', uc.Time, UNKNOWN),
	('hPa', uc.Pressure, uc.Pressure.Hectopascal),
	('hPa', uc.Length, UNKNOWN),
]

# (text, outcome class name) for compounds; the result is whatever the algebra returns
COMPOUNDS = [
	'km/h', 'mm/h', 'in/h', 'ft/s', 'm/min', 'mm/s', 'in/d', 'mm/d', 'km / h',
]
NOT_COMPOUNDS = [
	'g/m',            # the algebra answers with a catch-all Compound
	'm/m',            # a ratio of like units is a number
	'µg/m³',          # no cubic meter
	'mi/kWh',
	'km/',
	'/h',
	'km/h/s',
	'BTU/(h⋅ft²)',
	'x/y',
]


class TestLookupTable(TestCase):

	def test_every_row_is_exactly_one_outcome(self):
		for text, dimension, outcome in LOOKUPS:
			with self.subTest(text=text, dimension=getattr(dimension, '__name__', None)):
				if outcome in (UNKNOWN, AMBIGUOUS):
					with self.assertRaises(outcome) as raised:
						uc.lookup(text, dimension)
					self.assertEqual(text, raised.exception.unit)
					self.assertIsInstance(raised.exception.candidates, list)
				else:
					self.assertIs(outcome, uc.lookup(text, dimension))

	def test_parse_agrees_with_lookup_on_every_row(self):
		for text, dimension, outcome in LOOKUPS:
			with self.subTest(text=text, dimension=getattr(dimension, '__name__', None)):
				if outcome in (UNKNOWN, AMBIGUOUS):
					with self.assertRaises(outcome):
						uc.parse(1, text, dimension)
				else:
					self.assertIsInstance(uc.parse(1, text, dimension), outcome)

	def test_table_is_not_trivially_one_sided(self):
		outcomes = [outcome for _, _, outcome in LOOKUPS]
		self.assertGreater(outcomes.count(UNKNOWN), 10)
		self.assertGreater(len([o for o in outcomes if o not in (UNKNOWN, AMBIGUOUS)]), 50)
		self.assertGreaterEqual(outcomes.count(AMBIGUOUS), 1)


class TestTheOldSilentGuesses(TestCase):
	"""What the fuzzy matcher used to answer."""

	def test_degC_is_not_a_decade(self):
		self.assertIs(Celsius, uc.lookup('degC'))
		self.assertIsNot(uc.Time.Decade, uc.lookup('degC'))

	def test_percent_is_not_parts_per_hundred(self):
		self.assertIs(uc.Percentage, uc.lookup('%'))
		self.assertIsNot(uc.derived.partsPer.Hundred, uc.lookup('%'))

	def test_celsius_sign_is_not_a_change_in_temperature(self):
		self.assertIs(Celsius, uc.lookup('°C'))
		self.assertIs(uc.Temperature.CelsiusChange, uc.lookup('Δ°C'))

	def test_a_wrong_unit_never_comes_back_for_a_near_miss(self):
		for text in ('degX', 'Celcius', 'kmh', 'meterz', 'kilometre'):
			with self.subTest(text=text):
				with self.assertRaises(UnknownUnit):
					uc.lookup(text)

	def test_mbar_is_the_millibar_class(self):
		self.assertEqual('Millibar', uc.lookup('mbar').name)

	def test_old_lookup_is_untouched(self):
		# Phase 1 is additive: LevityDash still relies on these
		self.assertIs(uc.Length.Meter, uc.Time.Minute.__findUnitClass__('m'))
		self.assertEqual(uc.Time.Second, uc.auto(5, 's').__class__)


class TestCompounds(TestCase):

	def test_compounds_divide_with_the_algebra(self):
		cases = {
			'km/h': (uc.Length.Kilometer(10) / uc.Time.Hour(1)),
			'mm/h': (uc.Length.Millimeter(10) / uc.Time.Hour(1)),
			'ft/s': (uc.Length.Foot(10) / uc.Time.Second(1)),
			'in/d': (uc.Length.Inch(10) / uc.Time.Day(1)),
		}
		for text, expected in cases.items():
			with self.subTest(text=text):
				parsed = uc.parse(f'10 {text}')
				self.assertEqual(type(expected), type(parsed))
				self.assertEqual(float(expected), float(parsed))
				self.assertEqual(str(expected), str(parsed))
				self.assertIs(type(expected), uc.lookup(text))

	def test_a_compound_keeps_its_own_unit(self):
		self.assertAlmostEqual(2.7778, float(uc.parse('10 km/h')['m/s']), places=3)

	def test_m_per_s_is_wind_and_not_ambiguous(self):
		# `m` is Meter or Minute, but only Meter / Second is a speed
		parsed = uc.parse('10 m/s')
		self.assertIsInstance(parsed, uc.Wind)
		self.assertEqual(10, float(parsed))
		self.assertEqual('10 m/s', str(parsed))
		self.assertEqual(str(parsed), str(uc.parse(10, 'm/s')))

	def test_compound_symbols_the_library_has(self):
		self.assertIs(uc.Light.Irradiance, uc.lookup('W/m²'))
		self.assertIs(uc.Light.Irradiance, uc.lookup('W/m2'))
		self.assertIs(uc.Power.BritishThermalUnitPerHour, uc.lookup('BTU/h'))
		self.assertEqual(10, float(uc.parse('10 W/m²')))

	def test_unit_algebra_results_are_accepted_when_named(self):
		self.assertIs(uc.Power.Watt, uc.lookup('J/s'))

	def test_what_the_library_cannot_represent_raises(self):
		for text in NOT_COMPOUNDS:
			with self.subTest(text=text):
				with self.assertRaises(UnknownUnit):
					uc.lookup(text)
				with self.assertRaises(UnknownUnit):
					uc.parse(1, text)

	def test_compound_is_scoped_by_the_result(self):
		self.assertIsInstance(uc.parse('10 km/h', uc.Wind), uc.Wind)
		self.assertEqual('10 km/hr', str(uc.parse('10 km/h', uc.Wind)))
		with self.assertRaises(UnknownUnit):
			uc.parse('10 km/h', uc.Length)

	def test_a_bad_side_is_named(self):
		with self.assertRaises(UnknownUnit) as raised:
			uc.lookup('µg/m³')
		self.assertEqual('µg/m³', raised.exception.unit)
		self.assertIn("'m3'", str(raised.exception))

	def test_list_of_compounds_all_parse(self):
		for text in COMPOUNDS:
			with self.subTest(text=text):
				self.assertEqual(10, float(uc.parse(f'10 {text}')))


class TestErrors(TestCase):

	def test_unknown_is_a_value_error_and_a_lookup_error(self):
		self.assertTrue(issubclass(UnknownUnit, ValueError))
		self.assertTrue(issubclass(UnknownUnit, LookupError))
		self.assertTrue(issubclass(AmbiguousUnit, ValueError))
		self.assertTrue(issubclass(AmbiguousUnit, LookupError))

	def test_exported_from_the_package_and_from_errors(self):
		from unitcorn import errors
		self.assertIs(UnknownUnit, errors.UnknownUnit)
		self.assertIs(AmbiguousUnit, errors.AmbiguousUnit)
		self.assertIs(UnknownUnit, errors.Conversion.UnknownUnit)

	def test_unknown_carries_the_input_and_suggestions(self):
		with self.assertRaises(UnknownUnit) as raised:
			uc.lookup('Celcius')
		self.assertEqual('Celcius', raised.exception.unit)
		self.assertIn(Celsius, raised.exception.candidates)
		self.assertIn('Celcius', str(raised.exception))

	def test_unknown_candidates_are_what_suggest_returns(self):
		with self.assertRaises(UnknownUnit) as raised:
			uc.lookup('degX')
		self.assertEqual(uc.suggest('degX'), raised.exception.candidates)

	def test_ambiguous_lists_each_dimension_once(self):
		with self.assertRaises(AmbiguousUnit) as raised:
			uc.lookup('m')
		self.assertEqual('m', raised.exception.unit)
		self.assertEqual({uc.Length.Meter, uc.Time.Minute, uc.Time.Month}, set(raised.exception.candidates))
		self.assertEqual(3, len(raised.exception.candidates))
		self.assertIn('Meter', str(raised.exception))
		self.assertIn('Minute', str(raised.exception))

	def test_a_scoped_miss_says_the_scope(self):
		with self.assertRaises(UnknownUnit) as raised:
			uc.lookup('ms', uc.Length)
		self.assertIn('Length', str(raised.exception))

	def test_converting_to_an_unknown_unit_still_raises_the_same_error(self):
		# value['text'] is not changed by phase 1 except that its error now has .unit
		value = uc.Length.Meter(5)
		with self.assertRaises(UnknownUnit) as raised:
			value['nothing like a unit at all']
		self.assertEqual('nothing like a unit at all', raised.exception.unit)
		self.assertIs(value, raised.exception.measurement)
		self.assertIn('can not be converted', str(raised.exception))

	def test_the_old_two_argument_form_still_builds(self):
		error = UnknownUnit(uc.Length.Meter(5), 'zz')
		self.assertEqual('zz', error.unit)
		self.assertEqual([], error.candidates)


class TestParse(TestCase):

	def test_text_and_number_forms_agree(self):
		a, b = uc.parse('10 m/s'), uc.parse(10, 'm/s')
		self.assertEqual(type(a), type(b))
		self.assertEqual(float(a), float(b))

	def test_number_formats(self):
		cases = {
			'10 mm': 10, '10mm': 10, '  10   mm  ': 10, '-3.5 mm': -3.5, '+3.5 mm': 3.5,
			'.5 mm': 0.5, '5. mm': 5, '1e3 mm': 1000, '1E-2 mm': 0.01, '2.5e1mm': 25,
		}
		for text, expected in cases.items():
			with self.subTest(text=text):
				parsed = uc.parse(text)
				self.assertIs(uc.Length.Millimeter, type(parsed))
				self.assertEqual(expected, float(parsed))

	def test_value_as_text_or_int(self):
		self.assertEqual(21.5, float(uc.parse('21.5', '°C')))
		self.assertEqual(21, float(uc.parse(21, '°C')))
		self.assertIs(Celsius, type(uc.parse(21.5, 'degC')))

	def test_dimension_forms(self):
		self.assertIs(uc.Time.Minute, type(uc.parse('5 min', uc.Time)))
		self.assertIs(uc.Time.Minute, type(uc.parse('5 min', dimension=uc.Time)))
		self.assertIs(uc.Time.Minute, type(uc.parse(5, 'mins', uc.Time)))
		self.assertIs(uc.Time.Minute, type(uc.parse(5, 'min', dimension=uc.Time)))
		self.assertIs(uc.Length.Meter, type(uc.parse('5 m', uc.Length)))
		with self.assertRaises(AmbiguousUnit):
			uc.parse('5 m')
		with self.assertRaises(AmbiguousUnit) as raised:
			uc.parse('5 m', uc.Time)
		self.assertEqual({uc.Time.Minute, uc.Time.Month}, set(raised.exception.candidates))
		with self.assertRaises(TypeError):
			uc.parse('5 m', uc.Time, dimension=uc.Time)

	def test_percent_is_percent_not_a_guessed_fraction(self):
		# Percentage(1) would be read as 100 %
		self.assertAlmostEqual(0.01, float(uc.parse('1 %')))
		self.assertAlmostEqual(0.55, float(uc.parse('55 %')))
		self.assertAlmostEqual(0.005, float(uc.parse(0.5, '%')))
		self.assertEqual(1.0, float(uc.parse('100 %')))

	def test_no_number_or_no_unit_is_a_plain_value_error(self):
		for text in ('m/s', 'abc', '', '10', '  ', '- m'):
			with self.subTest(text=text):
				with self.assertRaises(ValueError) as raised:
					uc.parse(text)
				self.assertNotIsInstance(raised.exception, (UnknownUnit, AmbiguousUnit))

	def test_wrong_argument_types(self):
		with self.assertRaises(TypeError):
			uc.parse(10)
		with self.assertRaises(TypeError):
			uc.parse(True, 'm')
		with self.assertRaises(TypeError):
			uc.parse(10, 'm', 'Time')
		with self.assertRaises(TypeError):
			uc.lookup(5)
		with self.assertRaises(TypeError):
			uc.lookup('m', 'Time')

	def test_negative_zero_and_large(self):
		self.assertEqual(0, float(uc.parse('0 °C')))
		self.assertEqual(-40, float(uc.parse('-40 °F')))
		self.assertEqual(1e9, float(uc.parse('1e9 Pa')))

	def test_a_parsed_value_converts(self):
		self.assertAlmostEqual(0, float(uc.parse('32 °F')['c']), places=6)
		self.assertAlmostEqual(1000, float(uc.parse('1 km')['m']), places=6)

	def test_text_with_dimension_checks_the_scope(self):
		with self.assertRaises(UnknownUnit):
			uc.parse('5 hPa', uc.Length)


class TestSuggest(TestCase):

	def test_returns_unit_classes_best_first(self):
		suggestions = uc.suggest('degC')
		self.assertIsInstance(suggestions, list)
		self.assertIs(Celsius, suggestions[0])
		for suggestion in suggestions:
			self.assertIsInstance(suggestion, type)

	def test_never_picks_for_you_and_never_raises(self):
		for text in ('xyzzy', '', '   ', '12345', 'km/h', '???'):
			with self.subTest(text=text):
				self.assertIsInstance(uc.suggest(text), list)

	def test_no_repeats_and_n_caps(self):
		suggestions = uc.suggest('m', n=3)
		self.assertLessEqual(len(suggestions), 3)
		self.assertEqual(len(suggestions), len(set(suggestions)))
		self.assertEqual([], uc.suggest('m', n=0))

	def test_misspellings_find_the_unit(self):
		self.assertIn(Celsius, uc.suggest('Celcius'))
		self.assertIn(uc.Length.Kilometer, uc.suggest('kilometre'))
		self.assertIn(uc.Pressure.Hectopascal, uc.suggest('hectopascals'))

	def test_dimension_scopes_suggestions(self):
		for suggestion in uc.suggest('m', uc.Time):
			self.assertTrue(issubclass(suggestion, uc.Time), suggestion)
		self.assertIn(uc.Time.Minute, uc.suggest('min', uc.Time))
		self.assertNotIn(uc.Length.Meter, uc.suggest('m', uc.Time))

	def test_scoped_only_spellings_are_not_suggested_without_a_scope(self):
		self.assertNotIn(Celsius, uc.suggest('C'))
		self.assertIn(Celsius, uc.suggest('C', uc.Temperature))

	def test_suggestions_are_stable(self):
		self.assertEqual(uc.suggest('kn'), uc.suggest('kn'))


class TestIndexStaysCurrent(TestCase):

	def test_a_unit_defined_later_is_found(self):
		from unitcorn import Length
		from unitcorn.base import UnitType

		class Furlong(uc.Length.Mile.__mro__[1]):
			_unit = 'frl'

		self.assertIs(Furlong, uc.lookup('frl'))
		self.assertIs(Furlong, uc.lookup('furlong', Length))

	def test_building_a_compound_does_not_change_answers(self):
		before = uc.lookup('min', uc.Time)
		uc.parse('1 furlong/fortnight') if False else uc.parse('3 cm/min')
		self.assertIs(before, uc.lookup('min', uc.Time))
		self.assertIs(uc.Length.Meter, uc.lookup('m', uc.Length))


class TestHomeAssistantUnits(TestCase):
	"""Every `UnitOf*` string in Home Assistant parses, or raises one of the two errors."""
	FIXTURE = Path(__file__).parent / 'fixtures' / 'home_assistant_units.txt'

	# which dimension each Home Assistant enum measures, where this library has one
	DIMENSIONS = {
		'UnitOfTemperature': uc.Temperature,
		'UnitOfTime': uc.Time,
		'UnitOfLength': uc.Length,
		'UnitOfPrecipitationDepth': uc.Length,
		'UnitOfPressure': uc.Pressure,
		'UnitOfMass': uc.Mass,
		'UnitOfPower': uc.Power,
		'UnitOfEnergy': uc.Energy,
		'UnitOfArea': uc.Area,
		'UnitOfIrradiance': uc.Light,
		'UnitOfSpeed': uc.Rate,
		'UnitOfVolumetricFlux': uc.Rate,
		'UnitOfRatio': uc.Dimensionless if hasattr(uc, 'Dimensionless') else uc.Measurement,
	}

	@classmethod
	def rows(cls):
		rows = []
		for line in cls.FIXTURE.read_text(encoding='utf-8').splitlines():
			if line and not line.startswith('#'):
				enum, member, value = line.split('\t')
				rows.append((enum, member, value))
		return rows

	def outcome(self, text, dimension=None):
		try:
			return uc.parse(1, text, dimension)
		except (UnknownUnit, AmbiguousUnit) as error:
			return error

	def test_fixture_was_fetched_not_invented(self):
		header = self.FIXTURE.read_text(encoding='utf-8').splitlines()[:4]
		self.assertTrue(any('raw.githubusercontent.com/home-assistant/core' in line for line in header))
		self.assertTrue(any('Fetched:' in line for line in header))
		self.assertGreater(len(self.rows()), 150)
		self.assertIn(('UnitOfTemperature', 'CELSIUS', '°C'), self.rows())

	def test_each_one_parses_or_raises_one_of_the_two_errors(self):
		parsed = unknown = ambiguous = 0
		for enum, member, value in self.rows():
			with self.subTest(enum=enum, member=member, value=value):
				result = self.outcome(value)
				self.assertIsInstance(result, (uc.Measurement, UnknownUnit, AmbiguousUnit))
				if isinstance(result, UnknownUnit):
					unknown += 1
					self.assertEqual(value, result.unit)
				elif isinstance(result, AmbiguousUnit):
					ambiguous += 1
					self.assertGreater(len(result.candidates), 1)
				else:
					parsed += 1
		self.assertEqual(len(self.rows()), parsed + unknown + ambiguous)
		# Not everything may raise, and not everything can parse
		self.assertGreater(parsed, 50)
		self.assertGreater(unknown, 50)

	def test_nothing_parses_into_the_wrong_dimension(self):
		for enum, member, value in self.rows():
			expected = self.DIMENSIONS.get(enum)
			if expected is None:
				continue
			for scope in (None, expected):
				with self.subTest(enum=enum, value=value, scope=getattr(scope, '__name__', None)):
					result = self.outcome(value, scope)
					if isinstance(result, uc.Measurement):
						if value == 'Beaufort':
							# a wind-force scale, not a speed: the right thing, as an Index
							self.assertIsInstance(result, uc.Beaufort)
						elif enum == 'UnitOfRatio':
							self.assertIsInstance(result, (uc.Percentage, uc.derived.PartsPer))
						else:
							self.assertIsInstance(result, expected)

	def test_the_ones_that_should_parse(self):
		expected = {
			'°C': Celsius, '°F': Fahrenheit, 'K': Kelvin,
			'ms': uc.Time.Millisecond, 's': uc.Time.Second, 'min': uc.Time.Minute, 'h': uc.Time.Hour,
			'd': uc.Time.Day, 'w': uc.Time.Week, 'y': uc.Time.Year,
			'mm': uc.Length.Millimeter, 'cm': uc.Length.Centimeter, 'km': uc.Length.Kilometer,
			'in': uc.Length.Inch, 'ft': uc.Length.Foot, 'yd': uc.Length.Yard, 'mi': uc.Length.Mile,
			'Pa': uc.Pressure.Pascal, 'hPa': uc.Pressure.Hectopascal, 'kPa': uc.Pressure.Kilopascal,
			'bar': uc.Pressure.Bar, 'mmHg': uc.Pressure.MillimeterOfMercury,
			'inHg': uc.Pressure.InchOfMercury, 'psi': uc.Pressure.PoundsPerSquareInch, 'atm': uc.Pressure.Atmosphere,
			'W': uc.Power.Watt, 'kW': uc.Power.Kilowatt, 'MW': uc.Power.Megawatt, 'GW': uc.Power.Gigawatt,
			'J': uc.Energy.Joule, 'kWh': uc.Energy.KilowattHour, 'Wh': uc.Energy.WattHour,
			'g': uc.Mass.Gram, 'kg': uc.Mass.Kilogram, 'mg': uc.Mass.Milligram, 'μg': uc.Mass.Microgram,
			'oz': uc.Mass.Ounce, 'lb': uc.Mass.Pound,
			'm²': uc.Area.SquareMeter, 'km²': uc.Area.SquareKilometer, 'ac': uc.Area.Acre, 'ha': uc.Area.Hectare,
			'W/m²': uc.Light.Irradiance, '%': uc.Percentage,
			'ppm': uc.derived.partsPer.Million, 'ppb': uc.derived.partsPer.Billion,
			'V': uc.Voltage,
			'kn': uc.Wind.Knot, 'nmi': uc.Length.NauticalMile, 'Beaufort': uc.Beaufort,
		}
		values = {value for _, _, value in self.rows()}
		for text, unit in expected.items():
			with self.subTest(text=text):
				self.assertIn(text, values)
				self.assertIs(unit, type(uc.parse(1, text)))

	def test_the_ones_that_must_raise(self):
		# not in the library, or too ambiguous to answer unscoped
		must = ['m', 'mW', 'kcal', 'L', 'm³', 'μs', 'B', 'dB', 'cbar', 'BTU/(h⋅ft²)', 'μg/m³', 'kWh/100km']
		values = {value for _, _, value in self.rows()}
		for text in must:
			with self.subTest(text=text):
				self.assertIn(text, values)
				self.assertIsInstance(self.outcome(text), (UnknownUnit, AmbiguousUnit))

	def test_home_assistant_m_in_time_is_months_so_it_is_ambiguous_even_in_time(self):
		"""HA's `UnitOfTime.MONTHS` is `m`. Scoped to Time it must not become minutes."""
		self.assertIn(('UnitOfTime', 'MONTHS', 'm'), self.rows())
		self.assertIsInstance(self.outcome('m'), AmbiguousUnit)
		self.assertIsInstance(self.outcome('m', uc.Time), AmbiguousUnit)
		self.assertIs(uc.Time.Minute, uc.lookup('min', uc.Time))
		self.assertIs(uc.Time.Month, uc.lookup('month', uc.Time))
