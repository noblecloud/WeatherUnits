"""Pin the units config before WeatherUnits is first imported.

The default file follows the machine's locale (`us.toml` for en_US, `si.toml`
otherwise), and the tests assume `si.toml`. Without this pin they pass or fail
with the locale of whoever runs them.
"""
import os
from pathlib import Path

os.environ.setdefault('WU_CONFIG_PATH', str(Path(__file__).resolve().parents[1] / 'src' / 'WeatherUnits' / 'config' / 'si.toml'))
