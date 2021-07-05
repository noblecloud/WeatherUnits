import logging
import os.path
from configparser import ConfigParser
from importlib import resources

from pytz import timezone
import locale

from ..utils import convertString, PropertiesFromConfig

log = logging.getLogger('WeatherUnitsConfig')
log.setLevel(logging.DEBUG)
l = locale.getlocale()


class ConfigKey(str):
	def __new__(cls, string: str):
		return "".join(string.split())


class Config(ConfigParser):
	configuredUnits: dict[str, list[type]] = {}
	locale = locale.getlocale()[0]

	def __init__(self, *args, path: str = None, locale: str = None, **kwargs):
		self.optionxform = ConfigKey
		if locale is not None:
			self.locale = locale
		if path is None:
			path = 'us.ini' if self.locale.lower().endswith('us') else 'si.ini'
		super(Config, self).__init__(allow_no_value=True)
		with resources.path(__package__, path) as path:
			self.path = path
		self.read(path, reloadModules=False)
		log.info(f'Loaded {path}')

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
			PropertiesFromConfig(v, self)
		print(args)

	# def update(self):
	# 	# TODO: Add change indicator
	# 	self.read()

	def __getattr__(self, item):
		return self[item]

	@property
	def tz(self):
		try:
			return timezone(self['Location']['timezone'])
		except Exception as e:
			log.error('Unable load timezone from config\n', e)

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


config = Config()
