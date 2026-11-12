"""The formatting playground writes a format spec and a config line for what its controls say.

`docs/playground/playground.py` is the Python half of the page. These tests hold the claim most likely to
rot: the spec it writes and the `[UnitProperties]` line it writes both give back the string the page shows,
when they are fed through the library again.

The page renders against the package's own `template.toml`, and a config is read once, at import, so each
check runs in a fresh interpreter: one to produce what the page would show, then one per config line with the
line written into a copy of the template and pointed at by `UNITCORN_CONFIG_PATH`.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PLAYGROUND = ROOT / 'docs' / 'playground'
TEMPLATE = ROOT / 'src' / 'unitcorn' / 'config' / 'template.toml'

sys.path.insert(0, str(PLAYGROUND))
import playground as pg  # noqa: E402  (stdlib only; the library is imported lazily, in the subprocesses)


def run(script: str, payload, config: Path | None = None):
	"""Run `script` in a fresh interpreter with `payload` on stdin and a JSON answer on stdout."""
	env = {k: v for k, v in os.environ.items() if k not in ('UNITCORN_CONFIG_PATH', 'WU_CONFIG_PATH')}
	env['PYTHONPATH'] = os.pathsep.join([str(ROOT / 'src'), str(PLAYGROUND)])
	env['PYTHONIOENCODING'] = 'utf-8'
	if config is not None:
		env['UNITCORN_CONFIG_PATH'] = str(config)
	done = subprocess.run([sys.executable, '-c', script], input=json.dumps(payload), capture_output=True,
		text=True, encoding='utf-8', env=env, check=True)
	return json.loads(done.stdout)


#: What the page shows for a list of requests.
PAGE = '''
import json, sys
import playground as pg
print(json.dumps([pg.render_request(r) for r in json.loads(sys.stdin.read())], ensure_ascii=False))
'''

#: What a measurement shows with no spec at all, so only the class defaults (and any config line loaded) apply.
BARE = '''
import json, sys
import playground as pg
r = json.loads(sys.stdin.read())
print(json.dumps(format(pg.build(r['measurement'], r['unit'], pg.parse_value(r['value'])), ''), ensure_ascii=False))
'''

#: What a measurement shows for a spec, in a fresh interpreter: the claim that a pasted spec gives the same string.
PLAIN = '''
import json, sys
import playground as pg
r = json.loads(sys.stdin.read())
print(json.dumps(format(pg.build(r['measurement'], r['unit'], pg.parse_value(r['value'])), r['spec']), ensure_ascii=False))
'''


def req(measurement, unit, value, **params):
	return {'measurement': measurement, 'unit': unit, 'value': str(value), 'params': params}


#: (value, controls) combinations, each from a different corner of the page.
COMBOS = [
	req('temperature', 'f', 72.456, precision=2, show_unit=True),
	req('temperature', 'c', 22.5, digit_budget=4, unit_spacer='_', show_unit=True),
	req('temperature', 'f', 90, show_unit=True, unit_spacer='-'),
	req('length', 'in', 0.01, precision=2, digit_budget=2),
	req('length', 'in', 0.5, leading_zero='False'),
	req('length', 'in', 0.5, leading_zero='True', digit_budget=2),
	req('length', 'ft', 5120, shorten=True),
	req('length', 'm', 1234.5, shorten=True, precision=2, digit_budget=4),
	req('length', 'km', 3.14159, precision=3, digit_budget=5, show_unit=False),
	req('wind', 'mph', 4.1, unit_spacer='False'),
	req('wind', 'mps', 12.75, precision=2, digit_budget=5, trailing_zeros='fill'),
	req('pressure', 'inhg', 30.0, precision=2, digit_budget=5, trailing_zeros='precision'),
	req('pressure', 'inhg', 30.0, precision=2, digit_budget=5),
	req('pressure', 'mmhg', 760.0, precision=1, digit_budget=4, trailing_zeros='precision'),
	req('pressure', 'hpa', 1013.25, precision=2, digit_budget=6, show_unit=False),
	req('light', 'lux', 1054, shorten=True),
	req('light', 'lux', 1054, shorten=True, digit_budget=2, unit_spacer='_'),
	req('direction', 'deg', 22.5, shorten=False),
	req('direction', 'deg', 183, cardinal=False),
	req('direction', 'deg', 183, cardinal=False, precision=1, show_unit=False),
	req('rain', 'inhr', 0.01, precision=2, digit_budget=2),
	req('rain', 'mmhr', 2.5, trailing_zeros=2),
	req('rain', 'inhr', 0, precision=2, digit_budget=4, trailing_zeros='precision', true_zero=False),
	req('rain', 'inhr', 0, precision=2, digit_budget=4, trailing_zeros='precision', true_zero=True),
	req('wind', 'mph', 4.1),
	req('time', 'hr', 33, style='human'),
	req('time', 'hr', -3, style='ago'),
	req('time', 'mth', 18, style='timestamp'),
]


@pytest.fixture(scope='module')
def page():
	"""The page's answer to every combination and every case, in one interpreter on the template baseline."""
	requests = COMBOS + [dict(req(c['measurement'], c['unit'], c['value']), params=c['params']) for c in pg.CASES]
	answers = run(PAGE, requests)
	return dict(combos=answers[:len(COMBOS)], cases=answers[len(COMBOS):])


def with_line(template: str, key: str, line: str) -> str:
	"""`template` with `line` as the `[UnitProperties]` entry for `key`: replaced if the template has one, else added."""
	assert template.index('[UnitProperties]') > template.rindex('[UnitDefaults]'), '[UnitProperties] is no longer the last section'
	pattern = re.compile(rf'^{re.escape(key)}\s*=.*$', re.MULTILINE | re.IGNORECASE)
	if pattern.search(template):
		return pattern.sub(lambda _: line, template, count=1)
	return template.rstrip('\n') + '\n' + line + '\n'


def through_config(tmp_path: Path, answer: dict, request: dict) -> str:
	"""Write the page's config line into a copy of the template, load it, and format with no spec at all."""
	text = with_line(TEMPLATE.read_text(encoding='utf-8'), answer['key'], answer['configLine'])
	path = tmp_path / 'units.toml'
	path.write_text(text, encoding='utf-8')
	return run(BARE, request, config=path)


def test_every_case_still_says_what_the_page_says_it_does(page):
	for case, answer in zip(pg.CASES, page['cases']):
		assert answer['ok'], (case['id'], answer.get('error'))
		assert answer['text'] == case['expect'], case['id']


@pytest.mark.parametrize('index', range(len(COMBOS)), ids=[f'{r["measurement"]}-{r["unit"]}-{r["value"]}-{i}' for i, r in enumerate(COMBOS)])
def test_the_spec_reproduces_the_rendering(page, index):
	"""Paste the spec into a REPL and get the same string: the spec on its own, in a fresh interpreter."""
	request, answer = COMBOS[index], page['combos'][index]
	assert answer['ok'], answer.get('error')
	assert not answer['problems']
	again = run(PLAIN, dict(request, spec=answer['spec']))
	assert again == answer['text']


@pytest.mark.parametrize('index', range(len(COMBOS)), ids=[f'{r["measurement"]}-{r["unit"]}-{r["value"]}-{i}' for i, r in enumerate(COMBOS)])
def test_the_config_line_reproduces_the_rendering(page, tmp_path, index):
	"""Write the config line into a real TOML file, load it, and get the same string with no spec."""
	request, answer = COMBOS[index], page['combos'][index]
	assert answer['ok'], answer.get('error')
	if not answer['configLine']:
		pytest.skip('nothing set, so there is no line')
	loaded = through_config(tmp_path, answer, request)
	assert loaded == answer['asConfig'], answer['configLine']  # the page's emulation of a loaded line is faithful
	if loaded != answer['text']:
		assert answer['notes'], 'the page must say when a config line renders differently from the spec'
	else:
		assert not answer['notes']


def test_known_spec_and_config_differences_are_flagged(page):
	flagged = {(c['measurement'], c['value']): a['notes'] for c, a in zip(COMBOS, page['combos'])}
	assert flagged[('pressure', '30.0')]  # precision=2 on a whole number
	assert flagged[('direction', '183')]


def test_the_generated_line_is_valid_toml(page):
	import tomllib
	for answer in page['combos']:
		if answer['configLine']:
			parsed = tomllib.loads(answer['config'])
			assert answer['key'] in parsed['UnitProperties']


def test_a_case_the_config_can_not_say_is_flagged(page, tmp_path):
	"""unit_spacer=True is the word True in a spec and a boolean in a config; the page has to say so."""
	index = next(i for i, c in enumerate(pg.CASES) if c['id'] == 'spacer-word')
	answer, case = page['cases'][index], pg.CASES[index]
	assert any('read as a number or a boolean' in note for note in answer['notes'])
	request = req(case['measurement'], case['unit'], case['value'])
	assert through_config(tmp_path, answer, request) != answer['text']


def test_direction_ignores_digit_budget_in_a_spec_but_not_in_config(page, tmp_path):
	"""The gap `IGNORED_BY_SPEC` names. When the library closes it this fails: delete the entry and the case's note."""
	index = next(i for i, c in enumerate(pg.CASES) if c['id'] == 'direction-budget')
	answer, case = page['cases'][index], pg.CASES[index]
	assert ('direction', 'digit_budget') in pg.IGNORED_BY_SPEC
	assert any('does not read digit_budget' in note for note in answer['notes'])
	assert answer['text'] == 'NNE'
	assert through_config(tmp_path, answer, req(case['measurement'], case['unit'], case['value'])) == 'N'


def test_the_baseline_line_is_kept_when_a_parameter_is_added():
	"""A TOML table can not repeat a key, so a line for a key the baseline has must carry the baseline's own settings."""
	baseline = 'precision=1, digit_budget=3, unit_spacer=False, shorten=False, k_separator=True'
	line = pg.config_line('temperature', {'precision': '2', 'show_unit': 'True'}, baseline)
	assert line == ('temperature = { precision = 2, digit_budget = 3, unit_spacer = false, shorten = false, '
		'k_separator = true, show_unit = true }')


def test_text_and_choices_are_quoted_and_numbers_and_flags_are_not():
	line = pg.config_line('wind', {'unit_spacer': '_', 'leading_zero': 'auto', 'trailing_zeros': '2', 'true_zero': 'False',
		'shorten': 'True', 'precision': '3'})
	assert line == 'wind = { unit_spacer = "_", leading_zero = "auto", trailing_zeros = 2, true_zero = false, shorten = true, precision = 3 }'


def test_leading_zero_flags_are_booleans_in_config():
	assert 'leading_zero = true' in pg.config_line('length', {'leading_zero': 'True'})
	assert 'leading_zero = false' in pg.config_line('length', {'leading_zero': 'False'})


def test_values_the_parsers_would_read_as_structure_are_refused():
	for bad in ('a,b', 'a=b', 'a:b', '{x}', 'it\'s', 'a"b', 'a\\b', ''):
		values, problems = pg.clean({'unit_spacer': bad}, 'wind')
		assert 'unit_spacer' in problems or not bad and not values, bad
		assert 'unit_spacer' not in values


def test_out_of_range_numbers_are_refused_not_written():
	values, problems = pg.clean({'precision': 9, 'digit_budget': 0}, 'length')
	assert not values and set(problems) == {'precision', 'digit_budget'}


def test_a_parameter_for_another_measurement_is_left_out():
	values, _ = pg.clean({'cardinal': False, 'precision': 1}, 'wind')
	assert values == {'precision': '1'}
	values, _ = pg.clean({'cardinal': False}, 'direction')
	assert values == {'cardinal': 'False'}


def test_the_call_falls_back_to_format_when_an_f_string_could_not_hold_the_spec():
	assert pg.python_expression('') == "f'{value}'"
	assert pg.python_expression('precision=2, digit_budget=3') == "f'{value:precision=2, digit_budget=3}'"
	assert pg.python_expression("unit_spacer=it's") == 'format(value, "unit_spacer=it\'s")'


def test_every_catalogue_entry_builds_and_formats(page):
	"""Each unit on the page constructs from its own expression, at its own default value."""
	requests = [req(m['id'], u['id'], u['value']) for m in pg.MEASUREMENTS for u in m['units']]
	answers = run(PAGE, requests)
	for request, answer in zip(requests, answers):
		assert answer['ok'], (request, answer.get('error'))
		assert answer['text']
