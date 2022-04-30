import logging
from functools import lru_cache
from typing import Hashable, Type, Union

log = logging.getLogger(__name__)


@lru_cache(maxsize=64)
def loadUnitLocalization(measurement: Type['Measurement'], config):
	if not isinstance(measurement, type):
		measurement = measurement.__class__
	name = measurement.__name__
	possibleNames = [name.lower(), toCamelCase(name), name]

	if hasattr(measurement, '_type') and measurement._type is not None:
		possibleTypes = [measurement._type.__name__.lower(), toCamelCase(measurement._type.__name__), measurement._type.__name__]
		for classType in {*possibleNames, *possibleTypes}:
			if classType in config.localUnits:
				return config.localUnits[classType]
		else:
			log.warning(f'{measurement._type.__name__} has no type defined')


def toCamelCase(string, titleCase: bool = False) -> str:
	string = (string.lower() if string.isupper() else string)
	for char in ['-', ' ', '.', '_']:
		string.replace(char, '')
	return string[0].upper() if titleCase else string[0].lower() + string[1:]



def convertString(value: str) -> Union[int, float, str, bool]:
	if value is None:
		return value
	if value.isnumeric():
		value = float(value)
		if value.is_integer():
			value = int(value)
		return value
	if value == 'True':
		value = True
	elif value == 'False':
		value = False
	return value


def parseString(item: str):
	key, value = item.split('=')
	value = convertString(value)
	return f'_{key}', value


def strToDict(string: str, cls: type) -> type:
	conf = [parseString(a) for a in [(y.strip(' ')) for y in string.split(',')]]
	for item in conf:
		setattr(cls, *item)
	return cls


def setPropertiesFromConfig(cls, config) -> None:
	"""
	Modifies the class in place to add the properties defined in the config.
	:param cls: Class to modify
	:type cls: Type[Measurement]
	:param config: Config to use
	:type config: Config
	"""
	possibleNames = [cls.__name__.lower(), cls._unit, toCamelCase(cls.__name__), cls.__name__]
	if hasattr(cls, '_type') and cls._type is not None and not isinstance(cls._type, str):
		possibleTypes = [cls._type.__name__.lower(), toCamelCase(cls._type.__name__), cls._type.__name__]
		for classType in possibleTypes:
			try:
				cls = strToDict(config.unitProperties[classType], cls)
				config.configuredUnits[cls.__name__] = cls
				break
			except KeyError:
				pass
		else:
			log.debug(f'{cls.__name__} has no type defined')

	for name in possibleNames:
		try:
			cls = strToDict(config.unitProperties[name], cls)
			config.configuredUnits[name] = cls
			break
		except KeyError:
			pass


class HashSlice:
	__slots__ = ('start', 'stop', 'step')
	start: Union[Hashable, type]
	stop: Union[Hashable, type]
	step: Union[Hashable, type]

	def __init__(self, start: Union[Hashable, slice], stop: Hashable = None, step: Hashable = None):
		if isinstance(start, (slice, HashSlice)):
			stop = start.stop
			step = start.step
			start = start.start
		self.start = start
		self.stop = stop
		self.step = step

	def __iter__(self) -> iter:
		return iter((self.start, self.stop, self.step))

	def __repr__(self) -> str:
		return f"HashSlice[{self.start or ''}:{self.stop or ''}:{self.step or ''}]"

	def __str__(self) -> str:
		return f"[{self.start or ''}:{self.stop or ''}:{self.step or ''}]"

	def __eq__(self, other: object) -> bool:
		if hasattr(other, 'start') and hasattr(other, 'stop') and hasattr(other, 'step'):
			return self.start == other.start and self.stop == other.stop and self.step == other.step
		if self.stop is None and self.step is None:
			return self.start == other
		return False

	def __hash__(self) -> int:
		values = [self.start, self.stop, self.step]
		if self.step is None:
			values.pop()
		if self.stop is None and self.step is None:
			values.pop()
		if len(values) == 1:
			return hash(values[0])
		return hash(tuple(values))

	@property
	def isSlice(self) -> bool:
		return self.stop is not None
