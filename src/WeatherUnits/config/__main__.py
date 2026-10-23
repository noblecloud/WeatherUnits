"""`python -m WeatherUnits.config file.ini` prints that config as TOML."""
import sys

from . import Config

if len(sys.argv) != 2:
	sys.exit('usage: python -m WeatherUnits.config <file.ini>')
print(Config.toToml(sys.argv[1]), end='')
