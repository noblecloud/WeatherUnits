import os.path
from importlib import resources

import locale
import logging
from configparser import ConfigParser, SectionProxy
from pathlib import Path

from ..utils import convertString, setPropertiesFromConfig

log = logging.getLogger('WeatherUnitsConfig')


class Config(ConfigParser):
	configuredUnits: dict[str, list[type]] = {}
	locale = locale.getlocale()[0]
	__localUnits: SectionProxy

	def __init__(self, *args, path: str = None, locale: str = None, **kwargs):
		self.optionxform = str
		self.__localUnits = None
		path = path or os.environ.get('WU_CONFIG_PATH')
		super(Config, self).__init__(allow_no_value=True)

		if locale is not None:
			self.locale = locale
		if path is None:
			path = 'us.ini' if self.locale.lower().endswith('us') else 'si.ini'
			with resources.path(__package__, path) as path:
				self.path = path
		else:
			if isinstance(path, str):
				path = Path(path)
			self.path = path

		self.read(path, reloadModules=False)
		log.info(f'Loaded {path}')

	def __hash__(self):
		return hash(self.path)

	@property
	def customConfig(self):
		return self._customConfig

	def read(self, *args, reloadModules: bool = True, **kwargs):
		if args or kwargs:
			for arg in args:
				if os.path.isfile(arg):
					self.path = arg
					log.info(f'Loaded {arg}')
					super().read(arg, **kwargs)
					break
				else:
					log.error(f'{os.path.abspath(os.getcwd())}/{arg} is not a file')
			else:
				log.error(f'Unable to find config file')
		else:
			log.info(f'Loaded {self.path}')
		for k, v in self.configuredUnits.copy().items():
			setPropertiesFromConfig(v, self)

	def __getattr__(self, item):
		return self[item]

	@property
	def loc(self):
		return float(self['Location']['lat']), float(self['Location']['lon'])

	@property
	def lat(self):
		return float(self['Location']['lat'])

	@property
	def lon(self):
		return float(self['Location']['lon'])

	@property
	def unitProperties(self):
		return self['UnitProperties']

	@property
	def unitDefaults(self):
		return {f'_{prop}': convertString(value) for prop, value in config['UnitDefaults'].items()}

	@property
	def localUnits(self) -> SectionProxy:
		if self.__localUnits is None:
			if 'LocalUnits' in self:
				self.__localUnits = self['LocalUnits']
			elif 'Units' in self:
				self.__localUnits = self['Units']
			else:
				raise AttributeError(f'No local units defined in the config {self.path}')
		return self.__localUnits


config = Config()
