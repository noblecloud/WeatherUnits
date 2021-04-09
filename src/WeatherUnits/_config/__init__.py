import logging
import os.path
from configparser import ConfigParser
import importlib.resources
from pytz import timezone


class Config(ConfigParser):

	def __init__(self, *args, **kwargs):
		# TODO: Add SI or US selection to parameters
		super(Config, self).__init__(*args, **kwargs)
		with importlib.resources.path(__package__, 'us.ini') as path:
			self.path = path
		self.read()

	def read(self, *args, **kwargs):
		if args or kwargs:
			for arg in args:
				if os.path.isfile(arg):
					self.path = arg
			super().read(*args, **kwargs)
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


config = Config()
