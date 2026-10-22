"""Config files are TOML; an INI config still loads, and converts."""
import subprocess
import sys
import tomllib
from configparser import ConfigParser
from pathlib import Path

import pytest

from WeatherUnits.config import Config, config

CONFIG = Path(__file__).resolve().parents[1] / 'src' / 'WeatherUnits' / 'config'


def test_unit_properties_tables_become_property_lines():
	sections = Config.fromToml({'UnitProperties': {'mmHg': {'precision': 2, 'trailing_zeros': 'precision', 'shorten': False}}})
	assert sections['UnitProperties']['mmHg'] == 'precision=2, trailing_zeros=precision, shorten=False'


def test_values_read_back_as_they_do_from_ini():
	sections = Config.fromToml({'UnitDefaults': {'precision': 1, 'unit_spacer': True, 'unit': ''}})
	assert sections['UnitDefaults'] == {'precision': '1', 'unit_spacer': 'True', 'unit': ''}


def test_a_separator_in_a_property_value_is_refused():
	with pytest.raises(ValueError, match='can not hold'):
		Config.fromToml({'UnitProperties': {'humidity': {'missing': 'a, b'}}})


def test_a_top_level_value_is_refused():
	with pytest.raises(ValueError, match='must be a \\[section\\]'):
		Config.fromToml({'precision': 1})


def test_the_template_parses():
	with open(CONFIG / 'template.toml', 'rb') as file:
		Config.fromToml(tomllib.load(file))


def test_an_ini_config_converts_to_the_same_settings(tmp_path):
	ini = tmp_path / 'units.ini'
	ini.write_text('[UnitDefaults]\nprecision = 2\nunit_spacer = False\nkey\n\n[UnitProperties]\nmmHg = precision=2, digit_budget=5\n', encoding='utf-8')
	converted = Config.fromToml(tomllib.loads(Config.toToml(ini)))
	parser = ConfigParser(allow_no_value=True)
	parser.optionxform = str
	parser.read(ini)
	assert converted == {s: {k: v for k, v in parser[s].items() if v is not None} for s in parser.sections()}


def test_the_converter_runs_as_a_module(tmp_path):
	ini = tmp_path / 'units.ini'
	ini.write_text('[LocalUnits]\ntemperature = f\n', encoding='utf-8')
	out = subprocess.run([sys.executable, '-m', 'WeatherUnits.config', str(ini)], capture_output=True, text=True, encoding='utf-8', check=True)
	assert tomllib.loads(out.stdout) == {'LocalUnits': {'temperature': 'f'}}


@pytest.mark.parametrize('suffix', ['.toml', '.ini'])
def test_reading_either_format_localizes(tmp_path, suffix):
	import WeatherUnits as wu
	path = tmp_path / f'units{suffix}'
	path.write_text('[Units]\nlength = "mi"\n' if suffix == '.toml' else '[Units]\nlength = mi\n', encoding='utf-8')
	original = config.path
	try:
		config.read(str(path))
		assert wu.Length.localizedUnit is wu.Length.Mile
	finally:
		config.read(str(original))
