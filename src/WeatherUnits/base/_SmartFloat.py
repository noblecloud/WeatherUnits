import logging
import re
from builtins import float, isinstance
from collections import ChainMap, namedtuple
from difflib import get_close_matches
from functools import lru_cache, cached_property
from locale import delocalize
from typing import ClassVar, Optional, Set, Type, Union, Tuple, ForwardRef, TypeVar, Literal, Final, Mapping, Iterable
from math import nan, isnan, inf
from decimal import Decimal

from ..utils import modifyCase, pluralize, empty, getFrom, UnsetKwarg, loadUnitLocalization, CaseInsensitiveKey
from ..config import config, GROUPING_CHAR, RADIX_CHAR

__all__ = ('SmartFloat', 'Limits', 'TypedLimits', 'FormatSpec', 'FiniteField', 'UnitDict', 'MetaUnitClass')

regexType: Final = Literal['b', 'c', 'd', 'e', 'E', 'f', 'F', 'g', 'G', 'n', 'o', 's', 'x', 'X', '%']

log = logging.getLogger('SmartFloat')

__all__ = ['SmartFloat', 'FiniteField', 'MetaUnitClass', 'FormatSpec']

Measurement = ForwardRef('Measurement', is_class=True, module='Measurement')
_T = TypeVar('_T', Measurement, float)

Limits = namedtuple('Limits', 'min max')


class TypedLimits(Limits):
	min: _T
	max: _T

	@classmethod
	def fromLimits(cls, limit: tuple, type: _T = float) -> 'TypedLimits':
		return cls(type(limit[0]), type(limit[1]))

	def cast(self, type: _T) -> 'TypedLimits':
		return self.fromLimits(self, type)


class FormatSpec:
	truthy_values: ClassVar[Set[str]] = {'true', 't', 'yes', 'y', 'on', 'shown', 'show'}
	falsy_values: ClassVar[Set[str]] = {'false', 'f', 'no', 'n', 'off', 'hidden', 'hide'}
	limit = re.compile(r'\[(?P<max>([+-]?[\d.]+)|\*)?:(?P<min>([+-]?[\d.]+)|\*)?]')
	precision = re.compile("""	
	^:?
	(?P<format_spec>
		(?P<align>(?P<fill>.)?[<^>])?
		(?P<sign>[-+\s])?
		(?P<alt>\#)?
		(?P<minwidth>\d+)?
		(?P<grouping_option>[_,])?
		(?P<radix>\.)?
		(?(radix)(?P<precision>\d+)|)?
		(?P<type>[bcdeEfFgGnosxX%])?
	)$
	""", re.VERBOSE)
	params = re.compile("""
	(
    (?P<keyquote>[\'\"`]?)    # optional start quote
    (?P<key>\S+?)
    (?P=keyquote)
	)
	:\s*
	(
    (?P<valquote>[\'\"`]?)     # optional start quote
    (?P<value>.*?)           # literal value
    (?P=valquote)
	)
	(,|$)
	""", re.VERBOSE)
	formatParams = re.compile("""{(?P<name>\w+?) (?: :(?P<spec>.*?))?}""", re.VERBOSE)
	conversion = re.compile(r"""
	^(?P<fullmatch>
		(?P<convertTo>[-\w\s/\\]+)
		(?P<delinator>:{1,2})?)
	(?P<rest>
		(?(delinator) # Test for delinator 
			(?: # if True
				# Option 1: [:][any
				(?:[-\w\s/\\]+?:).*$
				| # or 
				# Option 2: [::][format_spec][$]
				(?:\S[^:]+?$)
			)
		| # else
			$ # False
		)
	)
	""", re.VERBOSE)
	number = re.compile(fr"""
	(?P<number>
	[-+]?
	([\d{GROUPING_CHAR}]+)?
	([{RADIX_CHAR}]\d+)?)
	""", re.VERBOSE)
	true = re.compile(rf'^({"|".join(truthy_values)})$', re.IGNORECASE)
	false = re.compile(rf'^({"|".join(falsy_values)})$', re.IGNORECASE)

	valueParams = re.compile(rf'(value|self):{precision.pattern}', re.VERBOSE)

	@classmethod
	def _float(cls, s: str | float | int) -> Optional[float | int]:
		try:
			value = float(delocalize(str(s)))
			return int(value) if value.is_integer() else value
		except ValueError:
			return None

	@classmethod
	def getNumber(cls, value: str, strict: bool = True, default: Optional[float] = None) -> Optional[float]:
		"""
		Get a number from a string.
		:param value: string to get number from:
		:param strict: Only return value if the string is entirely numeric:
		:return: float or None
		"""

		if strict:
			value = cls._float(value)
			return value if value is not None else default
		results = next((i.groupdict() for i in cls.number.search(value) if i is not None or i != ''), None)
		return cls._float(results['number']) if results else default

	@classmethod
	def getBool(cls, value: str, strict: bool | None = True, default: Optional[bool] = None) -> Optional[bool]:
		"""
		Get a boolean from a string.
		:param value: string to get boolean from
		:param strict: Only return value if the string is entirely boolean
		:param default: Default value if the string is not boolean
		:return: bool or None
		"""
		value = value.lower()

		if strict:
			isTrue = cls.true.match(value)
			isFalse = cls.false.match(value)

			if isTrue == isFalse:
				return default
			if isTrue is not None:
				return True
			elif isFalse is not None:
				return False
			else:
				return default

		elif strict is None:
			hasTrue = value in cls.truthy_values
			hasFalse = value in cls.falsy_values
		else:
			hasTrue = any(i == value for i in cls.truthy_values)
			hasFalse = any(i == value for i in cls.falsy_values)

		if hasTrue == hasFalse:
			return default
		return hasTrue


class FiniteField:
	_limits: Limits

	def _limitFunc(self, value: float) -> float:
		return value%self._limits[1]


class UnitDict(dict):

	def __getitem__(self, k):
		k = CaseInsensitiveKey(k)
		return super().__getitem__(k)

	def __setitem__(self, k, v):
		k = CaseInsensitiveKey(k)
		super().__setitem__(k, v)

	def __delitem__(self, k) -> None:
		k = CaseInsensitiveKey(k)
		super().__delitem__(k)


class MetaUnitClass(type):
	_name: ClassVar[Optional[str]]
	_derived: ClassVar[bool]
	_unit: ClassVar[Optional[str]] = None
	_limits: ClassVar[Tuple[Union[int, float]]]
	_acceptedTypes: ClassVar[Set[Type]]

	class __Dimensionless__:
		_dimension = None
		_unit = None
		_convertable = False

		@property
		def dimension(self):
			return None

		@property
		def unit(self):
			return ''

		@property
		def convertable(self):
			return False

		def _convert(self, *args, **kwargs):
			return self

	class __NonPlural__:

		def __subclasscheck__(self, subclass):
			return issubclass(subclass, type(self))

		@property
		def pluralName(self) -> None:
			return None

		@property
		def pluralUnit(self) -> None:
			return None

	def __new__(mcs, name, bases, attrs, **kwargs):
		if kwargs.get('baseUnit', None):
			attrs['baseUnit'] = kwargs['baseUnit']

		# find the Measurement name
		measurementName = getFrom(
			('fullName', 'name', 'full_name', 'unitName', 'unit_name', 'unitFullName', 'unit_full_name'),
			kwargs, attrs,
			default=None, pop=True, expectedType=str
		) or modifyCase(name, joiner=' ')

		if measurementName:
			attrs['_name'] = measurementName

		if aliases := getFrom(
			('aliases', 'alias', 'alternate'),
			kwargs, attrs,
			default=None, pop=True, findAll=True, expectedType=Iterable
		):
			if isinstance(aliases, str):
				aliases = (aliases,)
			if aliases and isinstance(aliases, list) and not isinstance(aliases[0], str):
				aliases = tuple(aliases[0])
			attrs['_aliases'] = set(aliases)

		# find the unit if not dimensionless
		if not any([issubclass(base, mcs.__Dimensionless__) for base in bases]):
			if (unit := getFrom(
				('_unit', 'unit'),
				kwargs, attrs,
				default=None, pop=True, expectedType=str)
			) is not None:
				attrs['_unit'] = unit

		# find the plurals if not non-plural
		if not any([issubclass(base, mcs.__NonPlural__) for base in bases]):
			if unit := attrs.get('_unit', None):
				attrs['_pluralUnit'] = getFrom(
					('pluralUnit', 'plural_unit', 'plural'),
					kwargs, attrs,
					default=None, pop=True, expectedType=str
				) or pluralize(unit)

			attrs['_pluralName'] = getFrom(
				('pluralName', 'plural_name', 'pluralFullName', 'plural_full_name'),
				kwargs, attrs,
				default=None, pop=True, expectedType=str
			) or pluralize(measurementName)

		# set convertable if found in kwargs
		if (convertable := kwargs.get('convertable', None)) is not None:
			attrs['_convertable'] = convertable

		if limits := getFrom(
			('limits', 'limit', 'minMax', 'min_max'),
			kwargs, attrs,
			default=None, pop=True, expectedType=Iterable,
			findAll=False,
		):
			if None in limits:
				m = limits[0]
				m = m if m is not None else min(getattr(mcs, '_limits', (-inf, inf)))
				M = limits[1]
				M = M if M is not None else max(getattr(mcs, '_limits', (-inf, inf)))
				limits = sorted((m, M))
			if isinstance(limits, dict):
				_max = limits.get('max', None) or max(getattr(mcs, '_limits', (-inf, inf)))
				_min = limits.get('min', None) or min(getattr(mcs, '_limits', (-inf, inf)))
				limits = sorted(_min, _max)
			attrs['_limits'] = Limits(*limits)

		# load attrs from config
		if name == 'Measurement':
			global Measurement
			attrs.update({key: value for key, value in config.unitDefaults.items() if value is not None})
			# attrs['__unitDict__'] = ChainMap()
			Measurement = super().__new__(mcs, name, bases, attrs, **kwargs)
			return Measurement
		# unitDict = ChainMap()
		# for base in genericBases:
		# 	base.__unitDict__.maps.append(unitDict)
		# attrs['__unitDict__'] = unitDict

		if name.lower() in config.unitPropertiesKeys:
			configPropertiesKey = get_close_matches(name, list(config.unitProperties.keys()), cutoff=0.3)
			configProps = {}
			for item in config.unitProperties[configPropertiesKey[0]].split(','):
				key, value = item.strip(' ').split('=')
				if (number := FormatSpec.getNumber(value, strict=True)) is not None:
					value = number
				elif (boolValue := FormatSpec.getBool(value, strict=False)) is not None:
					value = boolValue if boolValue is not None else empty
				configProps[f'_{key}'] = value
			attrs.update(configProps)

		attrs['__annotations__'] = ChainMap(attrs.get('__annotations__', {}), *(b.__dict__.get('__annotations__', {}) for b in bases))

		return super().__new__(mcs, name, bases, attrs, **kwargs)

	@property
	def isGeneric(cls) -> bool:
		return (cls is Measurement and cls is not SmartFloat) or getattr(cls, '_type', None) is cls

	@property
	def genericBases(self):
		return {base for base in self.__mro__ if getattr(base, 'isGeneric', False) or getattr(base, '_system', None) is base}

	@property
	def Generic(self) -> Type:
		genericBases = self.genericBases
		return next((base for base in genericBases if base is not self), None)

	def __subclasscheck__(cls, subclass):
		if subclass is None:
			return False
		value = super().__subclasscheck__(subclass)
		return value

	@property
	@lru_cache(maxsize=128)
	def localizedUnit(self) -> Type[Measurement] | Tuple[Type[Measurement] | None, ...] | None:
		unit = self.__parse_unit__(loadUnitLocalization(self, config))
		if isinstance(unit, (tuple, list)):
			if '*' in unit:
				if unit[0] == '*':
					unit = self.numerator, self.__findUnitClass__(unit[1])
				if unit[1] == '*':
					unit = self.__findUnitClass__(unit[0]), self.denominator
				return unit
			else:
				return tuple(self.__findUnitClass__(i) for i in unit)
		return self.__findUnitClass__(unit)

	def __parse_unit__(self, unit: str) -> str:
		return unit

	@property
	def isDerived(cls) -> bool:
		if not hasattr(cls, '_derived'):
			cls._derived = getattr(cls.__parent_class__, 'isDerived', None)
		return cls._derived

	@property
	def isScaling(cls) -> bool:
		return hasattr(cls, '_Scale')

	@property
	def __parent_class__(cls) -> Measurement:
		return cls.__mro__[1]

	@property
	def type(cls) -> Type[Measurement]:
		return getattr(cls, '_type', None) or next((base for base in cls.__mro__ if getattr(base, 'isGeneric', False)), cls)

	@property
	def dimension(self):
		return getattr(self, '__dimension__', None)

	@property
	def subTypes(cls):
		subs: Set[Type['Measurement']] = set()
		for sub in cls.__subclasses__():
			if sub.dimension == cls.dimension:
				subs.add(sub)
			subs.update(getattr(sub, 'subTypes', set()))
		return subs

	@property
	def unit(cls) -> str:
		return cls._unit or ''

	@property
	def system(self):
		return getattr(self, '_system', None)

	@property
	def name(self):
		return getattr(self, '_name', self.__name__)

	@property
	def decorator(cls):
		return cls._decorator

	@property
	def suffix(cls):
		return getattr(cls, '_suffix', '')

	@property
	def id(cls):
		return (
			cls.__dict__.get('_id', None)
			or getattr(cls, '_unit', None)
			or getattr(cls, '_decorator', None)
			or getattr(cls, '_suffix', None)
			or getattr(cls, '_id', None)
			or getattr(cls, 'unit', None)
			or getattr(cls, 'name', None)
		)

	@property
	def compatibleUnits(cls) -> UnitDict:
		units = UnitDict()
		for subtype in cls.type.subTypes:
			units.update({alias.lower(): subtype for alias in (subtype.unit, *subtype.aliases) if alias})
		units.pop(None, None)
		return units

	@property
	def compatibleTypes(cls) -> Set[Measurement]:
		return cls._acceptedTypes

	@property
	def fixedUnits(cls) -> tuple[Optional[Type[Measurement]], Optional[Type[Measurement]]]:
		n: Type['Measurement'] = getattr(cls, '_numerator', None)
		d: Type['Measurement'] = getattr(cls, '_denominator', None)
		if n is not None:
			n = None if n.isGeneric else n
		if d is not None:
			d = None if d.isGeneric else d
		return n, d

	@property
	def limits(cls) -> Limits:
		if cls.isDerived:
			return getattr(cls, '_limits', None) or getattr(cls.numeratorClass, 'limits', None) or (-inf, inf)
		return cls._limits

	@property
	def typedLimits(cls) -> TypedLimits:
		return TypedLimits.fromLimits(cls.limits, type=cls)

	def __repr__(cls):
		if cls.isDerived:
			match cls.fixedUnits:
				case MetaUnitClass(), MetaUnitClass():
					if '[' in cls.__name__:
						return cls.__name__
					return f'{cls.__name__}[{cls.numerator.__name__}/{cls.denominator.__name__}]'
				case MetaUnitClass(), None:
					return f'{cls.__name__}[{cls.denominator.__name__}]'
				case None, MetaUnitClass():
					return f'{cls.__name__}[{cls.numerator.__name__}]'
				case _:
					pass

			if ((cls.numerator.isGeneric or cls.__parent_class__.numerator.isGeneric)
				and (cls.denominator.isGeneric or cls.__parent_class__.denominator.isGeneric)):
				return f'{cls.__name__}[{repr(cls.numerator)}/{repr(cls.denominator)}]'
			elif cls.numerator.isGeneric or cls.__parent_class__.numerator.isGeneric:
				return f'{cls.__name__}[{repr(cls.numeratorClass)}]'
			elif cls.denominator.isGeneric or cls.__parent_class__.denominator.isGeneric:
				return f'{cls.__name__}[{repr(cls.denominator)}]'
			else:
				return f'{cls.__name__}'
		if cls.isGeneric:
			return f'<{cls.__name__}>'
		return cls.__name__

	# @lru_cache(maxsize=512)
	def __findUnitClass__(cls, unit: str) -> Type[Measurement] | None:
		unitDict = cls.compatibleUnits
		# unitDict.update({v.__name__.lower(): v for v in unitDict.values() if v.__name__.lower() not in unitDict})
		closestMatch = get_close_matches(unit.lower(), (i.lower() for i in unitDict.keys()), 1, cutoff=0.7)
		if closestMatch:
			return unitDict[closestMatch[0]]
		return None

	@property
	def pluralName(self) -> Optional[str]:
		return getattr(self, '_pluralName', None)

	@property
	def pluralUnit(self) -> Optional[str]:
		return getattr(self, '_pluralUnit', None)

	@property
	def aliases(self) -> Set[str]:
		return getattr(self, '_aliases', set()) | {self.name, self.pluralName, self.pluralUnit} - {None, ''}

	def _limitFunc(cls, value: _T) -> float:
		if cls.isDerived:
			return cls.numeratorClass._limitFunc(value)
		return cls._limitFunc(value)


class SmartFloat(float, metaclass=MetaUnitClass):
	_limits = -inf, inf
	_precision: int = 3
	valuePrecision: int
	_max: int = 4
	_unit: Optional[str]
	_suffix: Optional[str]
	_decorator: Optional[str]
	_unitSpacer: Optional[Union[bool, str]]
	_title: Optional[str]
	_showUnit: Optional[bool]
	_shorten: Optional[bool]
	_kSeparator: Optional[str]
	_key: Optional[Union[str, Set[Union[str, Tuple[str]]]]]
	_sizeHint: Optional[str]
	_acceptedTypes: ClassVar[tuple] = (float, int, Decimal)
	__unitDict__: ChainMap[str, Type]

	@classmethod
	def noneToNan(cls, value):
		if not isinstance(value, float):
			try:
				value = float(value)
			except ValueError:
				value = nan
			except TypeError:
				value = nan
		return value

	def __new__(cls, value):
		return float.__new__(cls, value)

	def __init__(self, value):
		float.__init__(value)

	@staticmethod
	def intFloatLength(value: float) -> tuple[int, int]:
		value = float(value)
		if value.is_integer():
			return len(str(int(value))), 0
		f = f'{abs(value):g}'.split('.')
		f = len(f[1]) if len(f) == 2 else 0
		d = len(str(round(value)))
		return d, f

	@cached_property
	def intLength(self) -> int:
		return len(str(round(self)))

	@cached_property
	def floatLength(self) -> int:
		value = float(self)
		if value.is_integer():
			return 0
		return len(f'{abs(value):g}'.split('.')[1])

	def _string(
		self,
		shorten: bool = None,
		prefix: str = None,
		suffix: str = None,
		decorator: str = None,
		spacer: Union[bool, str] = None,
		unit: bool = None,
		maxLength: int = None,
		formatSpec: str = None,
	) -> str:
		if shorten is None:
			shorten = getattr(self, '_shorten', False)
		if prefix is None:
			prefix = getattr(self, '_prefix', '')
		if suffix is None:
			suffix = getattr(self, '_suffix', '')
		if decorator is None:
			decorator = getattr(self, '_decorator', '')
		if spacer is None:
			spacer = getattr(self, '_unitSpacer', '')
		elif spacer is True:
			spacer = getattr(self, '_spacer', ' ') or ' '
		else:
			spacer = ''
		if unit is None:
			unit = getattr(self, 'unit', True)
		if maxLength is None:
			maxLength = getattr(self, '_max', 4)
		if formatSpec is None:
			formatSpec = getattr(self, '_format', 'g')

		if shorten:
			c, valueFloat = 0, float(self)
			numberLength = len(str(int(valueFloat)))
			while numberLength > 3 and numberLength >= self._max:
				c += 1
				valueFloat /= 1000
				numberLength = len(str(int(valueFloat)))
			valueSuffix = ['', 'k', 'm', 'B'][c]
		else:
			valueFloat = float(self)
			c = False
			valueSuffix = ''
		if isnan(valueFloat):
			return '???'

		# TODO: Allow for precision to be overridden if number is scaled.  (10,110.0 becomes 10.11k instead of 10.1k)
		integerLength, floatingPointLength = self.intFloatLength(valueFloat)
		if floatingPointLength == 1 and valueFloat.is_integer():
			floatingPointLength = 0

		stringType = 'f'

		# Max amount of precision that can be displayed while keeping string under max length
		intAllowedPrecision = max(0, self._max - integerLength)
		precision = min(self._precision, integerLength)
		# Allow at least on level of precision if
		# Removed 1 if not decimal and c else decimal

		f'{prefix}{self:{formatSpec}}{valueSuffix}{suffix}{decorator}{spacer}{unit}'

	def __str__(self):
		return f'{self}'

	def __format__(self, formatSpec):
		convertTo = None
		compatible_units = type(self).compatibleUnits

		conversionSpecMatch = FormatSpec.conversion.search(formatSpec)
		unitSet = set(compatible_units) | {'auto'}
		if conversionSpecMatch:
			conversionSpecMatch = conversionSpecMatch.groupdict()
			parsedUnit = type(self).__parse_unit__(conversionSpecMatch['convertTo'])
			if isinstance(parsedUnit, str) and parsedUnit.lower() in unitSet:
				formatSpec = re.sub(fr'{conversionSpecMatch["fullmatch"]}', '', formatSpec)
				convertTo = ({parsedUnit} & unitSet).pop()
			elif isinstance(parsedUnit, Iterable) and hasattr(self, 'numerator') and any(i.lower() in unitSet for i in parsedUnit):
				formatSpec = re.sub(fr'{conversionSpecMatch["fullmatch"]}', '', formatSpec)
				convertTo = tuple(i.lower() for i in parsedUnit if i in unitSet)

		if precisionSpec := FormatSpec.precision.search(formatSpec):
			precisionSpec = precisionSpec.groupdict()
		else:
			precisionSpec = {'format_spec': ''}

		specParams = dict((i['key'], i['value']) for i in FormatSpec.params.finditer(formatSpec))
		for key, value in specParams.items():
			if number := FormatSpec.getNumber(value, strict=True):
				specParams[key] = number
			elif (boolValue := FormatSpec.getBool(value, strict=None)) is not None:
				specParams[key] = boolValue if boolValue is not None else empty

		paramsSpecConversionMatch = type(self).__parse_unit__(specParams.get('convert', None))
		paramsSpecConversion = next(iter({paramsSpecConversionMatch} & unitSet), None)
		if convertTo := (convertTo or paramsSpecConversion):
			if convertTo == 'auto':
				if (auto := getattr(self, 'auto', None)) is not None:
					value = auto
				else:
					raise NotImplementedError(f'No auto conversion for {self.name}')
			else:
				value = type(self).type.getClass(convertTo)(self)
		elif convertTo or paramsSpecConversionMatch:
			attemptedUnit = []
			if conversionSpecMatch:
				attemptedUnit.append(conversionSpecMatch['convertTo'])
			if paramsSpecConversionMatch:
				attemptedUnit.append(paramsSpecConversionMatch)
			compatibleUnits = sorted(i.unit for i in type(self).type.subTypes)
			raise NotImplementedError(f'{" or ".join(repr(u) for u in attemptedUnit)} is not a valid conversion for {self.name}.  Valid conversions are: {compatibleUnits!r}')
		else:
			value = self

		floatValue = fm if (fm := getattr(value, 'formatValue', None)) is not None else float(value)

		params = ChainMap(specParams)
		params.specParams = specParams
		params.default = value.defaultFormatParams
		params.maps.insert(1, params.default)

		shortened = False
		if params.get('shorten', False):
			if (auto := getattr(self, 'auto', None)) is not None:
				value = auto
				floatValue = float(value)
			else:
				c = f'{floatValue:,}'.count(',')
				if c:
					shortened = True
					floatValue /= 1000 ** c
					params['valueSuffix'] = ['', 'k', 'm', 'B'][c]

		# get the formatSpec from the params['format']
		formatString = params.get('format', self.__format_template__(params))
		params.formatString = formatString

		# get format specs from inside the param formatSpec
		if formatStringParams := FormatSpec.valueParams.search(formatString):
			formatStringParams = formatStringParams.groupdict()
			formatStringParams = {key: value for key, value in formatStringParams.items() if value is not None}
		else:
			formatStringParams = {}

		params.maps.insert(0, formatStringParams)
		params.formatStringParams = formatStringParams

		# get format specs from formatSpec

		precisionSpec = {key: value for key, value in precisionSpec.items() if value is not None}
		params.maps.insert(0, precisionSpec)
		params.precisionSpec = precisionSpec

		formatVars = {i['name']: i.groupdict() for i in FormatSpec.formatParams.finditer(formatString)}
		params.formatVars = formatVars

		params['value'] = floatValue
		params.maps.append(self.__dict__)
		params.dict = self.__dict__

		for key, opts in formatVars.items():
			spec = opts['spec']
			v = getFrom(key, value, self, params, locals(), globals())
			if v is UnsetKwarg:
				raise ValueError(f"Variable '{key}' is undefined")
			if spec and key not in {'format', 'self', 'value'}:
				v = f'{v:{spec}}'
			formatVars[key] = v

		params.maps.insert(0, formatVars)

		if params['type'] == 'g':
			p = int(params['precision'])
			if floatValue > 1:
				max_ = int(params['max'])
				intLength, valuePrecision = value.intFloatLength(floatValue)
				params['value'] = floatValue = round(floatValue, min(p, valuePrecision))
				if p:
					totalLength = intLength + min(p, valuePrecision)
					params['precision'] = min(totalLength, max_) or 1
				else:
					if shortened:
						totalLength = min(intLength + valuePrecision, max_) - intLength
						params['precision'] = min(valuePrecision, totalLength) or 1
						params['type'] = 'f'
					else:
						params['precision'] = intLength or 1
			else:
				params['type'] = 'f'
				params['precision'] = p

		# params = value.__format_class__(formatSpec, params)
		formatString = params.formatString

		# params = {k: v if v is not None else '' for k, v in params.items() if not k.startswith('_')}
		# for k, v in params.items():
		# 	if k in {'precision', 'minwidth'} and v:
		# 		params[k] = int(v)

		params['value'] = self.__format_value__(params)

		formattedValue = formatString.format(**params)

		return formattedValue

	def __format_class__(self, formatSpec: str, formatParams: Mapping) -> dict:
		return formatParams

	def __format_value__(self, params: Mapping) -> str:
		return '{value:{fill}{align}{sign}{minwidth}.{precision}{type}}'.format(**params)

	def __format_template__(self, params: Mapping) -> str:
		formatTemplate = []
		if params.get('prefix', None):
			formatTemplate.append('{prefix}')
		value = params.get('value', None)
		if value is not False or value is not None:
			formatTemplate.append('{value}')
		if valueSuffix := params.get('valueSuffix', None):
			formatTemplate.append(f'{valueSuffix}')
		if params.get('decorator', None):
			formatTemplate.append('{decorator}')
		if params.get('showUnit', self.showUnit) and params.get('unit', self.unit) is not False:
			if params.get('unitSpacer', self.unitSpacer):
				formatTemplate.append('{unitSpacer}')
			formatTemplate.append('{unit}')
		if params.get('suffix', None):
			formatTemplate.append('{suffix}')

		return ''.join(formatTemplate)

	@property
	def defaultFormat(self) -> str:
		if self.showUnit:
			return "{value}{decorator}{unitSpacer}{unit}"
		return "{value}{decorator}"

	@property
	def defaultFormatParams(self):
		return {
			'leadingZero':  True,
			'trailingZero': True,
			'align':        '',
			'fill':         '',
			'sign':         '',
			'minwidth':     '',
			'precision':    self.precision,
			'value':        self,
			'type':         'g',
			'decorator':    self.decorator,
			'unitSpacer':   self.unitSpacer,
			'unit':         self.unit,
			'showUnit':     self.showUnit,
			'suffix':       self.suffix,
			'max':          self.max,
			'limits':       self._limits,
			'shorten':      self.shorten,
		}

	@property
	def properties(self) -> dict:
		attrs = {}
		if dimension := getattr(self, 'dimension', None):
			attrs['dimension'] = dimension
		if unit := getattr(self, 'unit', None):
			attrs['unit'] = unit
		if (numerator := getattr(self, 'numerator', None)) and (denominator := getattr(self, 'denominator', None)):
			attrs['numerator'] = numerator
			attrs['denominator'] = denominator
		if suffix := getattr(self, 'suffix', None):
			attrs['suffix'] = suffix
		if decorator := getattr(self, 'decorator', None):
			attrs['decorator'] = decorator
		if maxLength := getattr(self, 'max', None):
			attrs['maxLength'] = maxLength
		if precision := getattr(self, '_precision', None):
			attrs['precision'] = precision
		if showUnit := getattr(self, 'showUnit', None):
			attrs['showUnit'] = showUnit
		if shorten := getattr(self, 'shorten', None):
			attrs['shorten'] = shorten
		if (limits := getattr(self, '_limits', None)) and limits != (-inf, inf):
			attrs['limits'] = limits
		return attrs

	def __repr__(self):
		attrsString = ', '.join(f'{k}={str(v)}' for k, v in self.properties.items())
		return f'{type(self).__name__}(value={self.__repr_value__()}, {attrsString})'

	def __repr_value__(self) -> str:
		return f'{self: format:{"{value}{decorator}"}, type: g}'

	def __bool__(self):
		return super().__bool__() or bool(self.unit)

	def __float__(self) -> float:
		return super().__float__()

	def __hash__(self):
		return hash(round(self, max(self._precision, 1)))

	def __dir__(self):
		return list(self.properties) + ['__class__', '__module__', '__doc__', 'defaultFormat', 'defaultFormatParams']

	@property
	def valueUnset(self) -> bool:
		return self == nan

	@property
	def withUnit(self) -> str:
		return f'{self:showUnit: True}'

	@property
	def withoutUnit(self) -> str:
		return f'{self:showUnit: False}'

	@property
	def unit(self) -> str:
		return getattr(self, '_unit', '')

	@unit.setter
	def unit(self, value: str):
		self._unit = value

	@property
	def name(self):
		return getattr(self, '_name', type(self).__name__)

	@property
	def unitArray(self) -> list[str]:
		unit = self.unit
		return [unit] if unit is not None else []

	@property
	def suffix(self) -> Optional[str]:
		return getattr(self, '_suffix', '')

	@property
	def as_int(self) -> float:
		return self.__class__(round(self))

	@property
	def as_decorated_int(self) -> str:
		return f'{self:#.0g}'

	@property
	def name(self) -> str:
		return self.__class__.__name__

	@property
	def title(self) -> Optional[str]:
		return getattr(self, '_title', None)

	@title.setter
	def title(self, value):
		self._title = value

	@property
	def key(self) -> Optional[str]:
		return getattr(self, '_key', None)

	@key.setter
	def key(self, value: str):
		self._key = value

	@property
	def showUnit(self) -> bool:
		return getattr(self, '_showUnit', True)

	@showUnit.setter
	def showUnit(self, value):
		self._showUnit = value

	@property
	def decorator(self) -> str:
		return getattr(self, '_decorator', empty)

	@property
	def precision(self) -> int:
		_, valuePrecision = self.intFloatLength(self)
		return min(valuePrecision, getattr(self, '_precision', inf))

	@precision.setter
	def precision(self, value):
		self._precision = value

	@property
	def formatType(self) -> str:
		return 'g'

	@property
	def max(self) -> int:
		return self._max

	@max.setter
	def max(self, value: int):
		self._max = value

	@property
	def shorten(self) -> bool:
		return getattr(self, '_shorten', False)

	@shorten.setter
	def shorten(self, value):
		self._shorten = value

	@property
	def unitSpacer(self):
		spacer = getattr(self, '_unitSpacer', False)
		if isinstance(spacer, str):
			return spacer
		return " " if spacer else ""

	@unitSpacer.setter
	def unitSpacer(self, value):
		self._unitSpacer = value
