import logging
import re
from difflib import get_close_matches, SequenceMatcher
from functools import lru_cache
from heapq import nlargest
from itertools import product
from typing import Hashable, Type, Union, Final, Any, Mapping, Callable, Set, Tuple, Optional, NamedTuple

log = logging.getLogger(__name__)

numeric = re.compile(r'^[-+]?[0-9]*\.?[0-9]+$')


@lru_cache()
def loadUnitLocalization(measurement: Type['Measurement'], config):
	if not isinstance(measurement, type):
		measurement = type(measurement)
	unitName = measurement.type.name.lower()
	unitType = measurement.Generic.name.lower()
	match = get_close_matches(unitName, config.localUnits.keys(), n=1, cutoff=0.85) or get_close_matches(unitType, config.localUnits.keys(), n=1, cutoff=0.8)
	return config.localUnits[match[0]] if match else None


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


ScoredMatch = NamedTuple('Match', [('ratio', 'float'), ('value', 'str')])


def scored_get_close_matches(word, possibilities, n=3, cutoff=0.8):
	if not n > 0:
		raise ValueError("n must be > 0: %r"%(n,))
	if not 0.0 <= cutoff <= 1.0:
		raise ValueError("cutoff must be in [0.0, 1.0]: %r"%(cutoff,))
	result = []
	s = SequenceMatcher()
	s.set_seq2(word)
	for x in possibilities:
		s.set_seq1(x)
		if s.real_quick_ratio() >= cutoff and \
			s.quick_ratio() >= cutoff and \
			s.ratio() >= cutoff:
			result.append((s.ratio(), x))

	result = nlargest(n, result)
	return tuple(ScoredMatch(k, v) for (k, v) in result)


def best_match(word, possibilities, cutoff=0) -> Optional[str]:
	"""
	Returns the best guess at a match to the word.
	"""
	guesses = get_close_matches(word, possibilities, n=1, cutoff=cutoff)
	return guesses[0] if guesses else None


class CaseInsensitiveKey(str):

	def __hash__(self):
		return hash(self.lower())

	def __eq__(self, other):
		return self.lower() == other.lower()


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


def getPropertiesFromConfig(name: str, cls: dict, config) -> dict:
	"""
	Modifies the class in place to add the properties defined in the config.
	:param config: Config to use
	:type config: Config
	"""
	possibleNames = [name.__name__.lower(), cls.get('_unit'), toCamelCase(cls.__name__), name]
	# if hasattr(cls, '_type') and cls._type is not None and not isinstance(cls._type, str):
	# 	possibleTypes = [cls._type.__name__.lower(), toCamelCase(cls._type.__name__), cls._type.__name__]
	# 	for classType in possibleTypes:
	# 		try:
	# 			cls = strToDict(config.unitProperties[classType], cls)
	# 			config.configuredUnits[cls.__name__] = cls
	# 			break
	# 		except KeyError:
	# 			pass
	# 	else:
	# 		log.debug(f'{cls.__name__} has no type defined')
	result = {}
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
		elif isinstance(start, tuple) and stop is None and step is None:
			tupleLength = len(start)
			if tupleLength == 1:
				start = start[0]
			elif tupleLength == 2:
				start, stop = start
			elif tupleLength == 3:
				start, stop, step = start
			else:
				raise ValueError(f'Invalid start tuple length: {tupleLength}')
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


def modifyCase(string: str, titleCase: bool = True, joiner: str = '') -> str:
	if string.isupper():
		return string
	stringParts = re.findall(r'((?=[A-Z\_]?)[A-Z]?[A-Za-z][a-z]+)', string) or []
	if titleCase and stringParts:
		return joiner.join(i.title() for i in stringParts)
	return joiner.join(stringParts)


@lru_cache(maxsize=1024)
def pluralize(word: str) -> str:
	if re.search('[sxz]$', word):
		if len(word) <= 2:
			return word
		return re.sub('$', 'es', word)
	elif re.search('[^aeioudgkprt]h$', word):
		return re.sub('$', 'es', word)
	elif re.search('[aeiou]y$', word):
		return re.sub('y$', 'ies', word)
	else:
		return f'{word}s'


class Infix:
	def __init__(self, function=lambda x, y: x if x is not None else y):
		self.function = function

	def __ror__(self, other):
		return Infix(lambda x, self=self, other=other: self.function(other, x))

	def __or__(self, other):
		return self.function(other)

	def __rlshift__(self, other):
		return Infix(lambda x, self=self, other=other: self.function(other, x))

	def __rshift__(self, other):
		return self.function(other)

	def __call__(self, value1, value2):
		return self.function(value1, value2)

	def __rmatmul__(self, other):
		return Infix(lambda x, self=self, other=other: self.function(other, x))

	def __matmul__(self, other):
		return self.function(other)


class _Empty:

	def __bool__(self) -> bool:
		return True

	def __str__(self) -> str:
		return ''

	def __repr__(self) -> str:
		return ''

	def __iter__(self) -> iter:
		return iter(())

	def __getitem__(self, item: object) -> object:
		return self

	def __getattr__(self, item):
		return self

	def __call__(self, *args, **kwargs):
		return self

	def __len__(self) -> int:
		return 0

	def __contains__(self, item: object) -> bool:
		return False

	def __int__(self) -> int:
		return 0

	def __float__(self) -> float:
		return 0.0


NotNone: Final = Infix()
empty: Final = _Empty()
UnsetKwarg: Final = object()
Unset: Final = object()


def getFrom(
	key: Hashable | str | Tuple[Hashable | str, ...],
	*objs: Mapping | object,
	default: Any = UnsetKwarg,
	expectedType: type | Tuple[type, ...] = object,
	factory: Callable[[Any], Any] = lambda x: x,
	ignore: Set[Any] = None,
	findAll: bool = False,
	pop: bool = False,
):
	"""
	Returns the first acceptable attr or value from a list of objects
	:param objs: The mapping or object to search.
	:type objs: Mapping | object
	:param key: The keys to search for.
	:type key: Hashable | str
	:param default: The default value to return if the key is not found.
	:type default: Any
	:return: The value of the key in the mapping or the default value.
	:rtype: Any
	"""
	if ignore is None:
		ignore = set()
	if not isinstance(key, tuple):
		key = (key,)
	if findAll:
		found = []
	for obj, subKey in product(objs, key):
		if isinstance(obj, Mapping):
			value = obj.get(subKey, default)
		else:
			value = getattr(obj, subKey, default)
		if value is not UnsetKwarg and value not in ignore and isinstance(value, expectedType):
			if pop and (_pop := getattr(obj, 'pop', None)) is not None:
				_pop(subKey)
			if not findAll:
				return factory(value)
			found.append(factory(value))
	if findAll:
		return found
	elif default is UnsetKwarg:
		raise KeyError(key)
	return default
