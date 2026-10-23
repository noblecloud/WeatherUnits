"""The import must not depend on the host's locale.

Each case runs in a fresh interpreter because the config is read at import
time, in a class body.
"""
import os
import subprocess
import sys
from pathlib import Path
from unittest import TestCase

SRC = str(Path(__file__).resolve().parents[1] / 'src')


def importIn(env: dict) -> subprocess.CompletedProcess:
	base = {k: v for k, v in os.environ.items() if k not in ('LANG', 'LANGUAGE', 'LC_ALL', 'LC_CTYPE', 'WU_CONFIG_PATH')}
	return subprocess.run(
		[sys.executable, '-I', '-c', 'import sys; sys.path.insert(0, sys.argv[1]); import WeatherUnits', SRC],
		capture_output=True, text=True, env={**base, **env}, check=False,
	)


class TestImportWithoutALocale(TestCase):

	def test_an_uninstalled_locale_does_not_stop_the_import(self):
		result = importIn({'LC_ALL': 'xx_XX.UTF-8'})
		self.assertEqual(0, result.returncode, result.stderr)

	def test_an_unset_locale_does_not_stop_the_import(self):
		result = importIn({})
		self.assertEqual(0, result.returncode, result.stderr)

	def test_the_c_locale_does_not_stop_the_import(self):
		result = importIn({'LC_ALL': 'C'})
		self.assertEqual(0, result.returncode, result.stderr)


class TestDefaultConfig(TestCase):
	"""Which file loads when nothing names one."""

	def pick(self, name):
		from WeatherUnits.config import Config
		return Config.defaultFileFor(name)

	def test_us_locales_get_us_ini(self):
		self.assertEqual('us.toml', self.pick('en_US'))
		self.assertEqual('us.toml', self.pick('English_United States'))

	def test_everything_else_gets_si_ini(self):
		for name in ('de_DE', 'C', 'fr_CA', '', None):
			with self.subTest(locale=name):
				self.assertEqual('si.toml', self.pick(name))
