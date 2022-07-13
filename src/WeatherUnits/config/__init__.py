import os.path
from functools import cached_property
from importlib import resources

import locale

from logging import getLogger
from configparser import ConfigParser, SectionProxy
from pathlib import Path
from typing import Any, Optional, Callable, Set, Iterable, Mapping

from ..utils import convertString, setPropertiesFromConfig, scored_get_close_matches, best_match, CaseInsensitiveKey

log = getLogger('WeatherUnitsConfig')


class Config(ConfigParser):
	configuredUnits: dict[str, list[type]] = {}
	locale = locale.getlocale()[0]
	__localUnits: SectionProxy

	def __init__(self, *args, path: str = None, locale: str = None, **kwargs):
		self.optionxform = CaseInsensitiveKey
		self.__localUnits = None
		path = path or os.environ.get('WU_CONFIG_PATH')
		super(Config, self).__init__(allow_no_value=True)

		if locale is not None:
			self.locale = locale
			try:
				locale.setlocale(locale.LC_ALL, self.locale)
			except Exception:
				log.error(f'Unable to set locale to {self.locale}')
		if path is None:
			path = 'us.ini' if (self.locale.lower().endswith('us') or 'United States' in self.locale) else 'si.ini'
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

	@cached_property
	def unitPropertiesKeys(self) -> Set[str]:
		return {i.lower() for i in self['UnitProperties'].keys()}

	@property
	def groupingCharacter(self) -> bool | str:
		value = self['UnitDefaults'].get('groupingCharacter', True)
		return convertString(value)

	@property
	def unitDefaults(self):
		return {f'_{prop}': convertString(value) for prop, value in config['UnitDefaults'].items()}

	@property
	def localUnits(self) -> SectionProxy:
		possibleSections = {'Units', f'Units_{self.locale}', 'LocalUnits', 'WeatherUnits'}
		existingSections = set(self.sections())
		if len(existingSections & possibleSections) == 0:
			raise AttributeError(f'No local units defined in the config {self.path}')
		if self.__localUnits is None:
			self.__localUnits = self[next(iter(existingSections & possibleSections))]
		return self.__localUnits

	def search(
		self,
		key: str,
		default: Optional[Any] = None,
		guard: Callable[[Any], bool] = None,
		ignoreSection: Optional[str] = None,
		ignore: Optional[Set[str] | str] = None,
		accept: Optional[Set[str] | Mapping | str] = None,
		fuzzy: Optional[bool] = False,
		fuzzy_threshold: Optional[float] = 0.0,
	) -> Optional[Any]:
		if ignore is None:
			ignore = set()
		elif not isinstance(ignore, Iterable):
			ignore = ignore,
		if ignoreSection is None:
			ignoreSection = set()
		elif not isinstance(ignoreSection, Iterable):
			ignoreSection = ignoreSection,

		if accept is None:
			pass
		elif isinstance(accept, Mapping):
			wasMapping = accept
			accept = [i for j in accept.items() for i in j]
		elif not isinstance(accept, Iterable):
			accept = accept,

		if fuzzy:
			bestValues = (
				section[bestMatch]
				for section in (self[_] for _ in self.sections())
				if (bestMatch := best_match(key, section.keys(), cutoff=0.9))
				   and section.name not in ignoreSection
			)
			matches = (
				scoredMatch
				for bestValueFromSection in bestValues
				if (
					   scoredMatch := scored_get_close_matches(
						   bestValueFromSection, accept, n=1, cutoff=fuzzy_threshold
					   )
				   )
				   and bestValueFromSection not in ignore
				   and (guard is None or guard(bestValueFromSection))
			)
			matches = [i for j in matches for i in j]
			if matches:
				match = matches[0].value
				if "wasMapping" in locals() and match in wasMapping:
					return wasMapping[match]
				return match
			else:
				return default
		return next(
			(
				value
				for section in (self[_] for _ in self.sections())
				if key in section
				   and (value := section[key]) not in ignore
				   and (accept is None or value in accept)
				   and (guard is None or guard(value))
			),
			default,
		)


config = Config()

# search = config.search('locale', fuzzy=True, default=locale.getlocale()[0], accept=locale.locale_alias)
locale.setlocale(locale.LC_ALL, '')

try:
	RADIX_CHAR = locale.nl_langinfo(locale.RADIXCHAR)
	GROUPING_CHAR = locale.nl_langinfo(locale.THOUSEP)
except AttributeError:
	RADIX_CHAR = '.'
	GROUPING_CHAR = ','
