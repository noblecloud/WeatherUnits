"""The Python half of the formatting playground.

The page (`index.html`) loads this file into Pyodide, next to the real unitcorn
wheel, and talks to it with JSON strings. Nothing about *how* a value renders is
decided here or in the page: `render()` builds a measurement, writes the format
spec, and calls `format(value, spec)`. This module only decides how to *write
down* what the controls say, as a spec and as a `[UnitProperties]` config line.

Standard library only, so `tests/test_playground.py` imports it as well and
checks the claim most likely to rot: the spec and the config line it writes
render the same string when fed back through the library.

Baseline. The page renders against the library's own `template.toml`, not a
shipped `us.toml` / `si.toml`, so what a control does is not coloured by a
unit-system preset. Those files differ from the template in a few
`[UnitProperties]` lines, which is why a generated config line is *merged* with
the line the baseline already has for that key (a TOML table cannot repeat a key).
"""
import json
import math
import os
import re
import sys

#: A parameter the controls can set. `kind` is the control: `int` a slider, `bool` default/on/off,
#: `choice` a segmented control over `options`, `text` a text field.
PARAMS = (
	{'name': 'precision', 'kind': 'int', 'lo': 0, 'hi': 6,
		'doc': 'Decimal places, capped by digit_budget and by what the value itself needs.'},
	{'name': 'digit_budget', 'kind': 'int', 'lo': 1, 'hi': 8,
		'doc': 'Total digits that may be shown. Together with shorten it decides when a value is rescaled.'},
	{'name': 'leading_zero', 'kind': 'choice', 'options': ['True', 'False', 'auto'],
		'doc': 'The 0 before the point on values under 1. auto drops it only when that saves a digit of the value.'},
	{'name': 'trailing_zeros', 'kind': 'choice', 'options': ['off', 'precision', 'fill', '1', '2', '3'],
		'doc': 'Pad decimals to a stable width instead of the value own decimals. Capped by digit_budget.'},
	{'name': 'true_zero', 'kind': 'bool',
		'doc': 'Keep an exact zero bare while trailing_zeros pads the rest. No effect without trailing_zeros.'},
	{'name': 'shorten', 'kind': 'bool',
		'doc': 'Rescale to fit digit_budget. May change the unit (feet to miles) or add a k / m suffix.'},
	{'name': 'show_unit', 'kind': 'bool', 'doc': 'Show the unit at all.'},
	{'name': 'unit_spacer', 'kind': 'text',
		'doc': 'A string, not a flag: the text between the value and the unit. False means none; True is the literal word.'},
	{'name': 'cardinal', 'kind': 'bool', 'only': ['direction'],
		'doc': 'Show a compass heading (NNE) instead of degrees. shorten picks letters or words.'},
)
PARAM = {p['name']: p for p in PARAMS}

#: Characters the spec parser or a config table would read as structure, not as part of a spacer.
SPACER_FORBIDDEN = ',=:{}\'"\\'

#: The measurements the page offers. `key` is the `[UnitProperties]` key that reaches the whole family, and a unit's
#: own `key` replaces it where the family's does not reach: `length = {...}` binds nothing (a foot is an
#: ImperialLength, not a Length), and Kelvin sets some of its own defaults. A unit builds from
#: `ctor`, an expression over unitcorn's names with `{v}` for the value; `lo` / `hi` / `step` / `value` drive the slider.
MEASUREMENTS = (
	{'id': 'temperature', 'label': 'Temperature', 'key': 'temperature', 'units': (
		{'id': 'f', 'label': 'Fahrenheit', 'ctor': 'Temperature.Fahrenheit({v})', 'lo': -20, 'hi': 120, 'step': 0.5, 'value': 72.456},
		{'id': 'c', 'label': 'Celsius', 'ctor': 'Temperature.Celsius({v})', 'lo': -30, 'hi': 50, 'step': 0.5, 'value': 22.5},
		{'id': 'k', 'label': 'Kelvin', 'key': 'K', 'ctor': 'Temperature.Kelvin({v})', 'lo': 240, 'hi': 320, 'step': 0.5, 'value': 273.15},
	)},
	{'id': 'length', 'label': 'Length', 'key': None, 'units': (
		{'id': 'mm', 'label': 'Millimeter', 'key': 'mm', 'ctor': 'Length.Millimeter({v})', 'lo': 0, 'hi': 2000, 'step': 0.25, 'value': 415.25},
		{'id': 'm', 'label': 'Meter', 'key': 'm', 'ctor': 'Length.Meter({v})', 'lo': 0, 'hi': 5000, 'step': 0.5, 'value': 1234.5},
		{'id': 'km', 'label': 'Kilometer', 'key': 'km', 'ctor': 'Length.Kilometer({v})', 'lo': 0, 'hi': 100, 'step': 0.05, 'value': 3.14159},
		{'id': 'in', 'label': 'Inch', 'key': 'in', 'ctor': 'Length.Inch({v})', 'lo': 0, 'hi': 120, 'step': 0.01, 'value': 0.04},
		{'id': 'ft', 'label': 'Foot', 'key': 'ft', 'ctor': 'Length.Foot({v})', 'lo': 0, 'hi': 10000, 'step': 10, 'value': 5120},
		{'id': 'mi', 'label': 'Mile', 'key': 'mi', 'ctor': 'Length.Mile({v})', 'lo': 0, 'hi': 100, 'step': 0.05, 'value': 0.9697},
	)},
	{'id': 'wind', 'label': 'Wind', 'key': 'wind', 'units': (
		{'id': 'mph', 'label': 'Miles per hour', 'ctor': 'Wind.MilesPerHour({v})', 'lo': 0, 'hi': 100, 'step': 0.05, 'value': 4.1},
		{'id': 'mps', 'label': 'Meters per second', 'ctor': 'Wind.MetersPerSecond({v})', 'lo': 0, 'hi': 50, 'step': 0.05, 'value': 12.75},
	)},
	{'id': 'pressure', 'label': 'Pressure', 'key': 'pressure', 'units': (
		{'id': 'inhg', 'label': 'Inches of mercury', 'ctor': 'Pressure.InchOfMercury({v})', 'lo': 28, 'hi': 32, 'step': 0.01, 'value': 30.0},
		{'id': 'mmhg', 'label': 'Millimeters of mercury', 'ctor': 'Pressure.MillimeterOfMercury({v})', 'lo': 700, 'hi': 800, 'step': 0.1, 'value': 760.0},
		{'id': 'hpa', 'label': 'Hectopascal', 'ctor': 'Pressure.Hectopascal({v})', 'lo': 950, 'hi': 1050, 'step': 0.05, 'value': 1013.25},
		{'id': 'kpa', 'label': 'Kilopascal', 'ctor': 'Pressure.Kilopascal({v})', 'lo': 95, 'hi': 105, 'step': 0.01, 'value': 101.325},
		{'id': 'psi', 'label': 'Pounds per square inch', 'ctor': 'Pressure.PoundsPerSquareInch({v})', 'lo': 13, 'hi': 16, 'step': 0.01, 'value': 14.7},
	)},
	{'id': 'light', 'label': 'Light', 'key': 'illuminance', 'units': (
		{'id': 'lux', 'label': 'Lux', 'ctor': 'Light.Lux({v})', 'lo': 0, 'hi': 5000, 'step': 1, 'value': 1054},
	)},
	{'id': 'direction', 'label': 'Direction', 'key': 'direction', 'units': (
		{'id': 'deg', 'label': 'Degrees', 'ctor': 'Direction({v})', 'lo': 0, 'hi': 360, 'step': 0.5, 'value': 22.5},
	)},
	{'id': 'rain', 'label': 'Precipitation rate', 'key': 'precipitationRate', 'units': (
		{'id': 'inhr', 'label': 'Inches per hour', 'ctor': 'Precipitation.Hourly(Length.Inch({v}), Time.Hour(1))', 'lo': 0, 'hi': 4, 'step': 0.01, 'value': 0.01},
		{'id': 'mmhr', 'label': 'Millimeters per hour', 'ctor': 'Precipitation.Hourly(Length.Millimeter({v}), Time.Hour(1))', 'lo': 0, 'hi': 100, 'step': 0.25, 'value': 2.5},
	)},
)
MEASUREMENT = {m['id']: m for m in MEASUREMENTS}

#: A setting a config line reaches and a spec does not. The page says so when it matters, and `tests/test_playground.py`
#: checks the gap is still there, so fixing it in the library fails the test and sends you here to delete the entry.
IGNORED_BY_SPEC = {
	('direction', 'digit_budget'): (
		'Direction does not read digit_budget from a format spec today, so the slider changes nothing here. '
		'A config line does reach it: set it there and the compass resolution follows.'
	),
}

#: One-click examples. `expect` is what the spec renders today; `tests/test_playground.py` re-runs every one,
#: so a case that stops being true fails the suite instead of quietly lying on the page.
CASES = (
	{'id': 'self-contradictory', 'title': 'A budget too small for its precision',
		'measurement': 'length', 'unit': 'in', 'value': '0.01',
		'params': {'precision': 2, 'digit_budget': 2, 'show_unit': False}, 'expect': '.01',
		'note': 'Hundredths inside a two-digit budget cannot fit with the leading zero, which would give 0.0. '
			'leading_zero=auto drops it and shows .01. Set leading_zero to True and the value disappears.'},
	{'id': 'thirty', 'title': '30.0 renders as 30',
		'measurement': 'pressure', 'unit': 'inhg', 'value': '30.0',
		'params': {}, 'expect': '30 inHg',
		'note': 'Precision follows the value\'s own decimals, so a pressure that crosses a whole number changes width '
			'(29.9, 30, 30.1). Raising precision does not help: try precision 2, digit_budget 5 for 30.0 and then '
			'trailing_zeros = precision for 30.00.'},
	{'id': 'thirty-padded', 'title': '...until trailing_zeros pads it',
		'measurement': 'pressure', 'unit': 'inhg', 'value': '30.0',
		'params': {'precision': 2, 'digit_budget': 5, 'trailing_zeros': 'precision'}, 'expect': '30.00 inHg',
		'note': 'trailing_zeros keeps the width stable. fill pads to whatever the budget allows (30.000); '
			'it can never push a value over digit_budget.'},
	{'id': 'refit', 'title': 'shorten can change the unit',
		'measurement': 'length', 'unit': 'ft', 'value': '5120',
		'params': {'shorten': True}, 'expect': '0.97 mi',
		'note': 'Five thousand feet is too wide for three digits, so shorten refits it to miles outright, '
			'not to 5.12k ft. Turn shorten off to get 5120 ft back.'},
	{'id': 'suffix', 'title': 'shorten can add a suffix instead',
		'measurement': 'light', 'unit': 'lux', 'value': '1054',
		'params': {'shorten': True}, 'expect': '1.05k lux',
		'note': 'Lux has no bigger unit to climb to, so shorten scales by a thousand and writes a k.'},
	{'id': 'spacer-word', 'title': 'unit_spacer is a string',
		'measurement': 'temperature', 'unit': 'f', 'value': '90',
		'params': {'show_unit': True, 'unit_spacer': 'True'}, 'expect': '90°Truef',
		'note': 'The spacer is pasted between value and unit as text, so True is the word True. Use False for no '
			'spacer at all. In a config file true is read as a boolean, so this one cannot be written there.'},
	{'id': 'budget-zero', 'title': 'The zero stays when dropping it would not help',
		'measurement': 'length', 'unit': 'in', 'value': '0.0416',
		'params': {'precision': 1, 'digit_budget': 1, 'show_unit': False}, 'expect': '0',
		'note': 'Keeping the zero shows 0 and dropping it shows .0, which are equally empty, so auto keeps it.'},
	{'id': 'direction-words', 'title': 'Direction: letters or words',
		'measurement': 'direction', 'unit': 'deg', 'value': '22.5',
		'params': {'shorten': False}, 'expect': 'North North East',
		'note': 'shorten picks letters (NNE) or words. Turn cardinal off for plain degrees.'},
	{'id': 'direction-budget', 'title': 'Direction: the spec ignores digit_budget',
		'measurement': 'direction', 'unit': 'deg', 'value': '22.5',
		'params': {'digit_budget': 1}, 'expect': 'NNE',
		'note': 'A one-digit budget should give N. It does from a config line (the page\'s config output shows what '
			'to write), but a format spec does not reach the compass ladder today, so this stays NNE.'},
	{'id': 'missing', 'title': 'No reading',
		'measurement': 'wind', 'unit': 'mph', 'value': 'nan',
		'params': {}, 'expect': '⋯',
		'note': 'A NaN (or a None from a source) shows the missing marker instead of a number, and no other '
			'parameter applies to it.'},
)


# --- the library --------------------------------------------------------------------------------------

_lib = None


def baseline_config_path():
	"""The `template.toml` shipped inside the installed package, found without importing it."""
	import importlib.util
	spec = importlib.util.find_spec('unitcorn')
	return os.path.join(list(spec.submodule_search_locations)[0], 'config', 'template.toml')


def load_library():
	"""Import unitcorn once. Its config is read at import, so the baseline has to be set before this runs.

	`UNITCORN_CONFIG_PATH` wins if it is already set (the tests point it at a config of their own); otherwise the
	package's own `template.toml` is the baseline.
	"""
	global _lib
	if _lib is None:
		os.environ.setdefault('UNITCORN_CONFIG_PATH', baseline_config_path())
		import unitcorn
		_lib = unitcorn
	return _lib


def _namespace():
	lib = load_library()
	namespace = {name: getattr(lib, name) for name in dir(lib) if not name.startswith('_')}
	namespace['__builtins__'] = {'float': float}
	return namespace


# --- writing a value down -----------------------------------------------------------------------------

_NUMBER = re.compile(r'^[-+]?(\d+\.?\d*|\.\d+)$')

def parse_value(text):
	return float(str(text).strip())


def value_code(value, text=None):
	"""The value as source. Plain numbers keep the way they were typed, so 30 stays 30 and 30.0 stays 30.0."""
	if text is not None and _NUMBER.match(text.strip()):
		return text.strip().lstrip('+')
	if math.isnan(value):
		return 'float("nan")'
	if math.isinf(value):
		return 'float("inf")' if value > 0 else '-float("inf")'
	return repr(value)


def unit_entry(measurement, unit):
	for entry in MEASUREMENT[measurement]['units']:
		if entry['id'] == unit:
			return entry
	raise KeyError(f'no unit {unit!r} for {measurement!r}')


def constructor_code(measurement, unit, value, text=None):
	return unit_entry(measurement, unit)['ctor'].format(v=value_code(value, text))


def spec_value(name, raw):
	"""The text a parameter is written as in a spec, or ValueError if it can not be written."""
	param = PARAM[name]
	kind = param['kind']
	if kind == 'int':
		number = int(raw)
		if not param['lo'] <= number <= param['hi']:
			raise ValueError(f'{name} is {param["lo"]} to {param["hi"]}')
		return str(number)
	if kind == 'bool':
		if isinstance(raw, str):
			if raw not in ('True', 'False'):
				raise ValueError(f'{name} is True or False')
			return raw
		return 'True' if raw else 'False'
	if kind == 'choice':
		raw = str(raw)
		if raw not in param['options']:
			raise ValueError(f'{name} is one of {", ".join(param["options"])}')
		return raw
	text = str(raw).strip()
	if not text:
		raise ValueError(f'{name} is empty')
	if any(c in SPACER_FORBIDDEN for c in text):
		raise ValueError(f'{name} can not hold any of  {SPACER_FORBIDDEN}')
	return text


def clean(params, measurement):
	"""The parameters that are set and valid for this measurement, as {name: spec text}, in the table's order."""
	out = {}
	problems = {}
	for param in PARAMS:
		name = param['name']
		if name not in params or params[name] is None or params[name] == '':
			continue
		if 'only' in param and measurement not in param['only']:
			continue
		try:
			out[name] = spec_value(name, params[name])
		except (ValueError, TypeError) as error:
			problems[name] = str(error)
	return out, problems


def spec_string(values):
	return ', '.join(f'{name}={text}' for name, text in values.items())


def python_expression(spec):
	"""How to write the format call: an f-string when the spec is safe inside one, `format()` otherwise."""
	if not spec:
		return "f'{value}'"
	if any(c in spec for c in '\'"{}\\'):
		return f'format(value, {spec!r})'
	return f"f'{{value:{spec}}}'"


# --- writing it as config -----------------------------------------------------------------------------

def toml_literal(name, text):
	"""A parameter's value as a TOML literal, written so the config reader gives back what the spec meant."""
	param = PARAM[name]
	if param['kind'] == 'int':
		return text
	if param['kind'] == 'bool' or name == 'leading_zero' and text in ('True', 'False'):
		return text.lower()
	if name == 'trailing_zeros' and text.isdigit():
		return text
	return json.dumps(text, ensure_ascii=False)


def toml_literal_from_text(text):
	"""A value read out of an existing config line, written back as TOML."""
	if text in ('True', 'False'):
		return text.lower()
	if _NUMBER.match(text):
		return text
	return json.dumps(text, ensure_ascii=False)


def parse_line(line):
	"""`precision=2, digit_budget=5` as an ordered {name: text}."""
	out = {}
	for item in line.split(','):
		if '=' in item:
			name, text = item.split('=', 1)
			out[name.strip()] = text.strip()
	return out


def config_value(text):
	"""A parameter's text as the config reader types it: a number, else a boolean, else the text as it is."""
	load_library()
	from unitcorn.base._SmartFloat import FormatSpec
	if (number := FormatSpec.getNumber(text, strict=True)) is not None:
		return number
	if (flag := FormatSpec.getBool(text, strict=False)) is not None:
		return flag
	return text


def as_defaults(measurement, unit, value, values, text=None):
	"""What the same settings render as when they are class defaults, which is what a config line makes them.

	A config line is read once, at import, so the page can not load one and look. It sets `_name` attributes on
	the class; setting them on a fresh instance is the same layer, one step closer. `tests/test_playground.py`
	writes the line into a real file and checks this against what comes back.
	"""
	instance = build(measurement, unit, value, text)
	for name, raw in values.items():
		setattr(instance, f'_{name}', config_value(raw))
	return format(instance, '')


def differences(measurement, values, spec_text, config_text):
	"""Why a config line renders differently from the spec, as sentences for the page."""
	notes = [f'Written as a config line this renders {config_text!r}, not {spec_text!r}.']
	for name in values:
		if (measurement, name) in IGNORED_BY_SPEC:
			notes.append(IGNORED_BY_SPEC[(measurement, name)])
	if 'precision' in values:
		notes.append('A spec\'s precision is exact. A configured precision is a ceiling that follows the value\'s own '
			'decimals, so a whole number such as 30.0 stays 30. Add trailing_zeros = "precision" to pad it.')
	if 'unit_spacer' in values and config_value(values['unit_spacer']) != values['unit_spacer']:
		notes.append(f'In a config file {values["unit_spacer"]} is read as a number or a boolean, not as the text.')
	return notes


def config_line(key, values, baseline=None):
	"""One `[UnitProperties]` line: the baseline's own line for `key`, if it has one, with `values` laid over it."""
	merged = dict(parse_line(baseline)) if baseline else {}
	literals = {name: toml_literal_from_text(text) for name, text in merged.items()}
	for name, text in values.items():
		literals[name] = toml_literal(name, text)
	if not literals:
		return ''
	body = ', '.join(f'{name} = {literal}' for name, literal in literals.items())
	return f'{key} = {{ {body} }}'


def config_block(line):
	return f'[UnitProperties]\n{line}' if line else ''


def config_key(measurement, unit, instance):
	"""The key to write: the most specific one the baseline already has for this class, else the family's."""
	lib = load_library()
	entry = unit_entry(measurement, unit)
	cls = type(instance)
	own = cls.__dict__.get('_unit')
	specific = lib.config.unitPropertiesKeyFor(cls.__name__, own if isinstance(own, str) and own else None)
	return specific or entry.get('key') or MEASUREMENT[measurement]['key']


def baseline_line(key):
	lib = load_library()
	section = lib.config['UnitProperties']
	return section[key] if key in section else None


# --- the page's two calls -----------------------------------------------------------------------------

def build(measurement, unit, value, text=None):
	return eval(constructor_code(measurement, unit, value, text), _namespace())


def render_request(request):
	"""Everything the page shows for one state of the controls, as a dict."""
	measurement = request['measurement']
	unit = request['unit']
	result = {'ok': False, 'notes': [], 'problems': {}}
	try:
		value = parse_value(request['value'])
	except ValueError:
		result['error'] = f'{request["value"]!r} is not a number'
		return result
	values, result['problems'] = clean(request.get('params', {}), measurement)
	spec = spec_string(values)
	result['spec'] = spec
	result['call'] = python_expression(spec)
	result['construct'] = f'value = {constructor_code(measurement, unit, value, str(request["value"]))}'
	try:
		instance = build(measurement, unit, value, str(request['value']))
		result['text'] = format(instance, spec)
		key = config_key(measurement, unit, instance)
		line = config_line(key, values, baseline_line(key))
		result['key'] = key
		result['config'] = config_block(line)
		result['configLine'] = line
		result['asConfig'] = as_defaults(measurement, unit, value, values, str(request['value']))
		result['ok'] = True
	except Exception as error:
		result['error'] = f'{type(error).__name__}: {error}'
		return result
	if values and result['asConfig'] != result['text']:
		result['notes'] = differences(measurement, values, result['text'], result['asConfig'])
	return result


def render(request_json):
	return json.dumps(render_request(json.loads(request_json)), ensure_ascii=False)


def describe_unit(measurement, entry):
	instance = build(measurement, entry['id'], entry['value'])
	defaults = {}
	for param in PARAMS:
		name = param['name']
		if 'only' in param and measurement not in param['only']:
			continue
		defaults[name] = 'auto' if name == 'leading_zero' else getattr(instance, f'_{name}', None)
	return dict(entry, defaults=defaults, code=constructor_code(measurement, entry['id'], entry['value']))


def describe():
	"""The catalogue the page builds its controls from, as JSON."""
	try:
		from importlib.metadata import version
		library = version('unitcorn')
	except Exception:
		library = None
	return json.dumps({
		'library': library,
		'python': '.'.join(str(n) for n in sys.version_info[:3]),
		'params': list(PARAMS),
		'spacerForbidden': SPACER_FORBIDDEN,
		'measurements': [
			dict(m, units=[describe_unit(m['id'], u) for u in m['units']]) for m in MEASUREMENTS
		],
		'cases': list(CASES),
	}, ensure_ascii=False)
