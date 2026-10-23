"""The WeatherUnits forwarding shim in compat/WeatherUnits.

Run in a subprocess: the shim installs an import finder, and the point is to
see what a fresh interpreter that imports the old name gets.
"""
import os
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(code: str) -> subprocess.CompletedProcess:
	env = dict(os.environ)
	env['PYTHONPATH'] = os.pathsep.join([str(ROOT / 'src'), str(ROOT / 'compat' / 'WeatherUnits' / 'src')])
	return subprocess.run(
		[sys.executable, '-W', 'error::DeprecationWarning:__main__', '-c', textwrap.dedent(code)],
		capture_output=True, text=True, env=env,
	)


def test_import_warns():
	result = run('import WeatherUnits')
	assert result.returncode != 0
	assert 'renamed to unitcorn' in result.stderr


def test_old_names_are_the_same_objects():
	result = run('''
		import warnings
		warnings.simplefilter('ignore', DeprecationWarning)
		import sys, pickle
		import WeatherUnits as old
		from WeatherUnits.length import Foot
		from WeatherUnits.derived.precipitation import PrecipitationRate
		import unitcorn
		from unitcorn.length import Foot as NewFoot
		assert Foot is NewFoot
		assert old.Length is unitcorn.Length
		assert old.auto is unitcorn.auto
		assert sys.modules['WeatherUnits.length'] is sys.modules['unitcorn.length']
		assert PrecipitationRate is unitcorn.derived.precipitation.PrecipitationRate
		# The real module keeps its own spec, so it still resolves as unitcorn.
		assert unitcorn.length.__spec__.name == 'unitcorn.length'
		assert type(pickle.loads(pickle.dumps(Foot(3)))) is NewFoot
		print('ok')
	''')
	assert result.returncode == 0, result.stderr
	assert result.stdout.strip() == 'ok'


def test_old_environment_variable_still_read():
	us = ROOT / 'src' / 'unitcorn' / 'config' / 'us.toml'
	result = run(f'''
		import os
		os.environ.pop('UNITCORN_CONFIG_PATH', None)
		os.environ['WU_CONFIG_PATH'] = {str(us)!r}
		import unitcorn
		print(os.path.basename(unitcorn.config.path))
	''')
	assert result.returncode == 0, result.stderr
	assert result.stdout.strip() == 'us.toml'
