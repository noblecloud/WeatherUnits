import logging
import os.path
from configparser import ConfigParser
import importlib.resources
from pytz import timezone
import locale


log = logging.getLogger('WeatherUnitsConfig')
l = locale.getlocale()


class Config(ConfigParser):
	locale = locale.getlocale()[0]

	def __init__(self, *args, path: str = None, locale: str = None, **kwargs):
		if locale is not None:
			self.locale = locale
		if path is None:
			path = 'us.ini' if self.locale.lower().endswith('us') else 'si.ini'
		super(Config, self).__init__(*args, **kwargs, allow_no_value=False)
		with importlib.resources.path(__package__, path) as path:
			self.path = path
		self.read(path)

	def read(self, *args, **kwargs):
		if args or kwargs:
			for arg in args:
				if os.path.isfile(arg):
					self.path = arg
					super().read(*args, **kwargs)
					break
				else:
					log.error(f'{os.path.abspath(os.getcwd())}/{arg} is not a file')
			else:
				log.error(f'Unable to find config file')
		else:
			super().read(self.path)

	def update(self):
		# TODO: Add change indicator
		self.read()

	def __getattr__(self, item):
		return self[item]

	@property
	def tz(self):
		try:
			return timezone(self['Location']['timezone'])
		except Exception as e:
			logging.error('Unable load timezone from config\n', e)

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
