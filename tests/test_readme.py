"""The README's code examples must actually run.

Every example in the README was originally written by hand and never
executed. When they were finally run, all four "define your own unit"
examples failed on their first import line (`NamedType` had been renamed
to `UnitType` at some point), and four of the rendered-output tables in the
parameter reference disagreed with the library.

This test keeps that from happening again: it extracts the ```python fences
from README.md and executes each one. A fence is skipped only if it is
explicitly marked illustrative or is a `>>>` transcript (those are checked
by TestReadmeTranscript below instead).
"""
import re
from pathlib import Path
from unittest import TestCase

README = Path(__file__).parent.parent / 'README.md'

# Fences that are prose-adjacent rather than runnable programs.
SKIP_MARKERS = ('Illustrative sketch', 'wu.config.read(')


def _code_blocks():
	source = README.read_text()
	for index, block in enumerate(re.findall(r'```python\n(.*?)```', source, re.S)):
		if '>>>' in block:
			continue
		if any(marker in block for marker in SKIP_MARKERS):
			continue
		yield index, block


class TestReadmeExamples(TestCase):

	def test_readme_has_examples_to_check(self):
		# Guards against the extraction silently matching nothing, which
		# would make every other assertion here vacuously true.
		self.assertGreaterEqual(len(list(_code_blocks())), 4)

	def test_every_example_executes(self):
		for index, block in _code_blocks():
			with self.subTest(block=index, first_line=block.strip().split('\n')[0]):
				# A fresh namespace per block: the examples redefine names
				# like Length and Pressure that also exist in the library,
				# and must not leak into each other.
				exec(compile(block, f'README.md[block {index}]', 'exec'), {})


class TestReadmeTranscript(TestCase):
	"""The `>>>` block at the top is the first thing anyone reads."""

	def test_conversion_transcript(self):
		from WeatherUnits.temperature import Fahrenheit
		value = Fahrenheit(32)
		self.assertEqual('32°', str(value))
		self.assertEqual('32°f', value.withUnit)
		self.assertEqual('0°c', value['c'].withUnit)
		self.assertEqual('0°', str(value.celsius))

	def test_parameter_reference_tables(self):
		"""The rendered outputs in the '#### Properties' tables."""
		from WeatherUnits import Length, Time, Light
		from WeatherUnits.others import Direction

		# precision table (3.14159 m)
		for precision, expected in ((0, '3 m'), (1, '3.1 m'), (2, '3.14 m'), (3, '3.142 m')):
			with self.subTest(precision=precision):
				self.assertEqual(expected, format(Length.Meter(3.14159), f'precision={precision}, digit_budget=6'))

		# digit_budget table (415.25 mm) - caps without granting
		for budget, expected in ((2, '41.53 cm'), (3, '415.2 mm'), (4, '415.2 mm'), (5, '415.2 mm')):
			with self.subTest(digit_budget=budget):
				self.assertEqual(expected, format(Length.Millimeter(415.25), f'digit_budget={budget}'))

		# shorten table
		self.assertEqual('16.67min', format(Time.Second(1000), 'shorten=True'))
		self.assertEqual('1000s', format(Time.Second(1000), 'shorten=False'))
		self.assertEqual('1.00k lux', str(Light.Lux(1000)))

		# unit_spacer is a string, not a flag
		from WeatherUnits import Temperature
		self.assertEqual('90°f', format(Temperature.Fahrenheit(90), 'unit_spacer=False, show_unit=True'))
		self.assertEqual('90°Truef', format(Temperature.Fahrenheit(90), 'unit_spacer=True, show_unit=True'))

		# cardinal table
		self.assertEqual('S', format(Direction(180), 'cardinal=True'))
		self.assertEqual('180°', format(Direction(180), 'cardinal=False'))
