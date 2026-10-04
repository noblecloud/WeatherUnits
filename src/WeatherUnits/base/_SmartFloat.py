import logging
import re
from builtins import float, isinstance
from collections import ChainMap, namedtuple
from difflib import get_close_matches
from functools import lru_cache, cached_property
from locale import delocalize
from typing import ClassVar, Optional, Set, Type, Union, Tuple, ForwardRef, TypeVar, Literal, Final, Mapping, Iterable, Self
from math import nan, isnan, inf, isinf
from decimal import Decimal

from ..errors import FormattingError
from ..utils import modifyCase, pluralize, empty, getFrom, loadUnitLocalization, CaseInsensitiveKey, DEBUG
from ..config import config, GROUPING_CHAR, RADIX_CHAR
from .Registry import UnitRegistry

__all__ = ('SmartFloat', 'Limits', 'TypedLimits', 'FormatSpec', 'FiniteField', 'UnitDict', 'MetaUnitClass')

regexType: Final = Literal['b', 'c', 'd', 'e', 'E', 'f', 'F', 'g', 'G', 'n', 'o', 's', 'x', 'X', '%']

log = logging.getLogger('WeatherUnits').getChild('SmartFloat')

__all__ = ['SmartFloat', 'FiniteField', 'MetaUnitClass', 'FormatSpec']

Measurement = ForwardRef('Measurement', is_class=True, module='Measurement')
_T = TypeVar('_T', bound='SmartFloat')

Limits = namedtuple('Limits', 'min max')

scale_factors = (
	'', 'k', 'm', 'b',
	't', 'q', 'Q', 's',
	'S', 'o', 'n', 'd',
	'U', 'D', 'T', 'Qt',
	'Qd', 'Sd', 'St', 'O',
	'N', 'v', 'c'
)


class TypedLimits(Limits):
	min: _T
	max: _T
	_type: Type[_T] = float

	@classmethod
	def fromLimits(cls, limit: tuple, type: _T = float) -> 'TypedLimits':
		lim = cls(*(type(x) if not isinf(x) else x for x in limit))
		lim._type = type
		return lim

	def cast(self, type: _T) -> 'TypedLimits':
		return self.fromLimits(self, type)


class FormatSpec:
	truthy_values: ClassVar[Set[str]] = {'true', 't', 'yes', 'y', 'on', 'shown', 'show'}
	falsy_values: ClassVar[Set[str]] = {'false', 'f', 'no', 'n', 'off', 'hidden', 'hide'}
	# Parameters pasted verbatim into __format_value__'s float format spec,
	# where a bool is always wrong. Without this, single-letter values that
	# happen to be truthy/falsy words get coerced - `type=f` (float) and
	# `type=n` (locale-aware number) both became False and produced
	# '.2False'. Deliberately narrow: keys like unit_spacer/decorator/prefix/
	# suffix/unit DO take False meaningfully (it disables them), so they
	# must keep being coerced.
	never_boolean: ClassVar[Set[str]] = {'type', 'fill', 'align'}
	# UNUSED, INTENTIONALLY KEPT. Nothing reads `.limit`, so the bracket
	# syntax it describes - `{value:[100:0]}`, clamping at format time - is
	# not accepted anywhere yet. Kept because implementing it is still wanted;
	# the exact intent is no longer remembered, so treat the pattern as the
	# specification: an optional max and an optional min, either of which may
	# be `*` to mean "unbounded on this side".
	limit = re.compile(r'\[(?P<max>([+-]?[\d.]+)|\*)?:(?P<min>([+-]?[\d.]+)|\*)?]')
	precision = re.compile(r"""
	(^)?(?(1)|(?<=:))
	(?P<format_spec>
		(?P<align>(?P<fill>.)?[<^>])?
		(?P<sign>[-+\s])?
		(?P<alt>\#)?
		(?P<minwidth>\d+)?
		(?P<grouping_option>[_,])?
		(?P<radix>\.)?
		(?(radix)(?P<precision>\d+)|)?
		(?P<type>[bcdeEfFgGnosxX%])?
	)
	(?=:|$)
	""", re.VERBOSE)
	params = re.compile(r"""
  (^)?(?(1)|,\s)(
    (?P<keyquote>[\'\"`]?)    # optional start quote
    (?P<key>\S+?)             # key
    (?P=keyquote)							# end quote
	)
	\s*[=:]\s*                # separator: '=' or ':' (both are written in
	                          # the wild - `show_unit=False` vs the
	                          # `show_unit: True` / `cardinal: False` style
	                          # used by .withUnit and Direction.__str__.
	                          # Only ':' was ever unsupported, so those
	                          # specs silently parsed as nothing and the
	                          # whole parameter was dropped.
	(
    (?P<valquote>[\'\"`]?)     # optional start quote
    (?P<value>.*?)             # literal value
    (?P=valquote)              # end quote
	)
	(?=,|$)
	""", re.VERBOSE)
	formatParams = re.compile(r"{(?P<name>\w+?) (?: :(?P<spec>.*?))?}", re.VERBOSE)
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

	global Measurement

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

		# A unit is looked up by its class name AND by its unit symbol, because
		# config keys are routinely written as symbols - `inHg`, `mmHg`.
		# Matching on the class name alone meant `InchOfMercury` never found
		# the `inHg` line, so those settings were silently ignored.
		#
		# The match is exact (case-insensitively). It used to run the name
		# through get_close_matches(cutoff=0.3) and take the first hit, which
		# could apply a *different* unit's settings than the one that passed
		# the check above.
		#
		# Only the class's own declared `_unit` counts, never an inherited
		# one: a subclass that inherits its parent's symbol must not silently
		# adopt the parent's config line.
		configPropertiesKey = config.unitPropertiesKeyFor(name, attrs.get('_unit'))
		if configPropertiesKey is not None:
			configProps = {}
			for item in config.unitProperties[configPropertiesKey].split(','):
				key, value = item.strip(' ').split('=')
				if (number := FormatSpec.getNumber(value, strict=True)) is not None:
					value = number
				elif (boolValue := FormatSpec.getBool(value, strict=False)) is not None:
					value = boolValue if boolValue is not None else empty
				configProps[f'_{key}'] = value
			attrs.update(configProps)

		attrs['__annotations__'] = ChainMap(attrs.get('__annotations__', {}), *(b.__dict__.get('__annotations__', {}) for b in bases))

		mcs = super().__new__(mcs, name, bases, attrs, **kwargs)
		UnitRegistry.register(mcs)
		# mcs._addSpecials()
		return mcs

	def _addSpecials(cls):
		name = cls.__name__
		one = cls(1)
		cls.one = one
		setattr(cls.type, f'an{name.title()}', one)
		setattr(cls.type, f'a{name.title()}', one)

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

	def __lt__(cls, other):
		try:
			return cls.scale.__lt__(other.scale)
		except AttributeError:
			return super().__lt__(cls, other)

	def __gt__(cls, other):
		try:
			return cls.scale.__gt__(other.scale)
		except AttributeError:
			return super().__gt__(cls, other)

	def __le__(cls, other):
		try:
			return cls.scale.__le__(other.scale)
		except AttributeError:
			return super().__le__(cls, other)

	def __ge__(cls, other):
		try:
			return cls.scale.__ge__(other.scale)
		except AttributeError:
			return super().__ge__(cls, other)

	@property
	@lru_cache(maxsize=128)
	def localizedUnit(self) -> Type['Measurement'] | Tuple[Type['Measurement'] | None, ...] | None:
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
	def unit_symbol(cls):
		return cls._unit_symbol

	@property
	def suffix(cls):
		return getattr(cls, '_suffix', '')

	@property
	def id(cls):
		return (
			cls.__dict__.get('_id', None)
			or getattr(cls, '_unit', None)
			or getattr(cls, '_unit_symbol', None)
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
	def compatibleTypes(cls) -> Set[Type['Measurement']]:
		return cls._acceptedTypes

	@property
	def fixedUnits(cls) -> tuple[Optional[Type['Measurement']], Optional[Type['Measurement']]]:
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
	def __findUnitClass__(cls, unit: str) -> Type['Measurement'] | None:
		if unit is None:
			return None

		if matched := UnitRegistry.get(unit):
			return matched

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
			return cls.numerator._limitFunc(value)
		return value


class SmartFloat(float, metaclass=MetaUnitClass):
	_limits = -inf, inf
	_precision: int = 3
	valuePrecision: int
	_digit_budget: int = 4
	_unit: Optional[str]
	_suffix: Optional[str]
	_unit_symbol: Optional[str]
	_unit_spacer: Optional[Union[bool, str]]
	_title: Optional[str]
	_show_unit: Optional[bool]
	_shorten: Optional[bool]
	_k_separator: Optional[str]
	_key: Optional[Union[str, Set[Union[str, Tuple[str]]]]]
	_size_hint: Optional[str]
	_acceptedTypes: ClassVar[tuple] = (float, int, Decimal)
	__unitDict__: ChainMap[str, Type]
	__transferable__: set[str] = {
		'leading_zero',
		'trailing_zeros',
		'true_zero',
		'align',
		'fill',
		'sign',
		'minwidth',
		'type',
		'unit_symbol',
		'unit_spacer',
		'unit',
		'show_unit',
		'suffix',
	}

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
		elif isinf(value):
			return 0, 0
		f = f'{abs(value):g}'.split('.')
		f = len(f[1]) if len(f) == 2 else 0
		d = len(str(round(value)))
		return d, f

	@cached_property
	def intLength(self) -> int:
		return len(str(round(float(self))))

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
		unit_symbol: str = None,
		spacer: Union[bool, str] = None,
		unit: bool = None,
		maxLength: int = None,
		formatSpec: str = None,
	) -> str:
		"""Render directly from keyword arguments, bypassing the spec parser.

		INTENTIONALLY KEPT as a second way to format a value. `__format__` is
		the primary path and takes a spec *string*, which has to be parsed and
		validated; this takes the same knobs as plain keywords, which is the
		cheaper call when the caller already has them as values - e.g. a
		plugin schema carrying its own conversion/formatting settings.

		No production caller today, so it is easy to break silently: the
		snake_case rename turned this method's local `decorator` into
		`unit_symbol` in the f-string but not in the parameter list, and every
		call raised `NameError` until it was noticed. `tests/test_string_api.py`
		exists so that cannot happen again.
		"""
		if shorten is None:
			shorten = getattr(self, '_shorten', False)
		if prefix is None:
			prefix = getattr(self, '_prefix', '')
		if suffix is None:
			suffix = getattr(self, '_suffix', '')
		if unit_symbol is None:
			unit_symbol = self.unit_symbol
		if spacer is None:
			spacer = getattr(self, '_unit_spacer', None)
		if spacer is None:
			spacer = ' ' if self._unit and not self.unit_symbol else ''
		elif spacer is True:
			spacer = getattr(self, '_spacer', ' ')
		elif spacer is False:
			spacer = ''
		if unit is None:
			unit = self.show_unit
		if maxLength is None:
			maxLength = getattr(self, '_digit_budget', 4)
		if formatSpec is None:
			formatSpec = getattr(self, '_format', 'g')
		if shorten is None:
			shorten = getattr(self, '_shorten', False)

		if shorten:
			c, valueFloat = 0, float(self)
			numberLength = len(str(int(valueFloat)))
			while numberLength > 3 and numberLength >= maxLength:
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
		intAllowedPrecision = max(0, maxLength - integerLength)
		precision = min(self._precision, intAllowedPrecision)
		if formatSpec == 'g':
			formatSpec = f'.{max(1, precision + integerLength)}g'

		if unit:
			unitString = self.unit
		else:
			unitString = ''
		# No unit means nothing to separate from, so no separator - same rule
		# as __format_template__. Without this a dimensionless value rendered
		# '180° ' with a trailing space.
		spacer = spacer if (spacer and unitString) else ''
		return f'{prefix}{valueFloat:{formatSpec}}{valueSuffix}{suffix}{unit_symbol}{spacer}{unitString}'

	def __str__(self):
		return f'{self}'

	def __format__(self, formatSpec, **extras):
		convertTo = None
		compatible_units = type(self).compatibleUnits

		if isinstance(formatSpec, dict):
			params, formatSpec = formatSpec, formatSpec.get('format', '')
		else:
			params = {}

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

		if (precisionSpec := FormatSpec.precision.search(formatSpec)) and precisionSpec.group():
			formatSpec = formatSpec[:precisionSpec.start()-1] if formatSpec.endswith(precisionSpec.group()) else formatSpec[precisionSpec.end()+1:]
			precisionSpec = precisionSpec.groupdict()
		else:
			precisionSpec = {'format_spec': ''}

		specParams = dict((i['key'], i['value']) for i in FormatSpec.params.finditer(formatSpec))
		for key, value in specParams.items():
			if number := FormatSpec.getNumber(value, strict=True):
				specParams[key] = number
			elif key in FormatSpec.never_boolean:
				# Left as the literal string: several single-letter format
				# codes collide with the boolean words below - 'f' and 'n'
				# are both in falsy_values, so `type=f` used to coerce to
				# False and reach __format_value__ as '.2False', raising
				# ValueError. These keys never take a boolean value.
				continue
			elif (boolValue := FormatSpec.getBool(value, strict=None)) is not None:
				specParams[key] = boolValue if boolValue is not None else empty

		# Conversion
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

		params = ChainMap(extras, specParams, params)
		params.extras = extras
		params.specParams = specParams
		# The caller's own precision, from either spelling - `format(v,
		# 'precision=0')` or `v.__format__('', precision=0)`. Captured now:
		# `extras` is the first map, so every `params['precision'] = ...`
		# below writes into it and the asked-for value is gone by the time
		# trailing_zeros needs it.
		params.explicitPrecision = extras.get('precision', specParams.get('precision'))
		params.default = value.defaultFormatParams
		params.maps.insert(2, params.default)

		intLength, valuePrecision = value.intFloatLength(floatValue)
		max_len = params.get('digit_budget', value._digit_budget)
		shortened = False
		if params.get('shorten', False):
			starting_len = len(str(int(floatValue)))
			if (best_fit := getattr(value, 'bestFit', None)) is not None:
				if (fitted_value := best_fit(max_len)) is not value:
					value = fitted_value
					# The refit changed the unit, so the unit's own settings
					# have to come with it: precision, digit_budget and
					# trailing_zeros all belong to the unit being displayed,
					# not the one the value started in. `params.default` was
					# captured from the original above, so without this a
					# Hectopascal shown as mmHg was formatted with
					# Hectopascal's config while wearing mmHg's label.
					# Spec parameters still outrank it - the defaults sit
					# below `specParams` in the chain.
					params.default = value.defaultFormatParams
					params.maps[2] = params.default
					floatValue = float(value)
					intLength = value.intLength
					precision_offset = starting_len - intLength
					try:
						params['precision'] += precision_offset
					except TypeError:
						params['precision'] = int(params['precision']) + precision_offset
					valuePrecision += precision_offset
			elif (auto := getattr(self, 'auto', None)) is not None:
				value = auto
				floatValue = float(value)
				intLength = value.intLength
				precision_offset = starting_len - intLength
				params['precision'] += precision_offset
				valuePrecision += precision_offset
			else:
				c = f'{floatValue:,}'.count(',')
				if c:
					shortened = self.precision + (2 * c)
					valuePrecision += c * 2
					params['precision'] += c * 2
					intLength -= c * 2
					floatValue /= 1000 ** c
					if (valueSuffix := scale_factors[c]) == value.unit:
						valueSuffix += ' '
					params['valueSuffix'] = valueSuffix

			# update params.default to reflect the new value
			new_defaults = value.transferable_defaults
			params.default.update({k:v for k,v in value.defaultFormatParams.items() if k in new_defaults})

		# get the formatSpec from the params['format']
		formatString = params.get('format', value.__format_template__(params))
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

		# find all sub format spect
		formatVarsSpecs = {i['name']: i.groupdict() for i in FormatSpec.formatParams.finditer(formatString)}
		params.formatVars = formatVarsSpecs

		params['value'] = floatValue
		params['self'] = value
		params.maps.append(self.__dict__)
		params.dict = self.__dict__

		# this was commented out because I don't think it is needed
		# params.maps.insert(0, formatVarsSpecs)

		if params['type'] == 'g':
			p = int(params['precision'])
			if float(value) > 1:
				max_ = int(params['digit_budget'])
				params['value'] = floatValue = round(floatValue, min(p, valuePrecision))
				if p:
					totalLength = intLength + min(p, valuePrecision)
					params['precision'] = min(totalLength - intLength, max_) or 1
					# params['precision'] = max(min(totalLength - intLength, max_), 0) or 1z
					params['type'] = 'f'
				else:
					if shortened:
						totalLength = min(intLength + valuePrecision, max_) - intLength
						params['precision'] = min(valuePrecision, totalLength) or 1
						params['type'] = 'f'
					else:
						params['precision'] = intLength or 1
			else:
				params['type'] = 'f'
				# `max` is a display-width budget (total digits shown) and it
				# applies here too - this branch previously used `p` unclamped,
				# so `max` was inert for every value <= 1 and 0.004 rendered
				# '0.00' at max=3, max=2 AND max=1 alike.
				#
				# A sub-1 value normally spends intLength digits on its integer
				# part (the leading '0'), leaving max - intLength for decimals.
				# When leading_zero is off that '0' is never rendered, so it
				# costs nothing and the whole budget goes to decimals - which is
				# what makes a `precision=2, max=2` config coherent: '.01'
				# rather than an over-budget '0.01' or a useless '0.0'.
				max_ = int(params['digit_budget'])
				intDigits = self.__intDigits(params, floatValue, intLength, max_, p)
				params['leadingZeroDropped'] = intDigits != intLength
				params['precision'] = max(min(p, max_ - intDigits), 0)

		# `precision` above is derived from the value's own decimal content,
		# so a value that happens to land on a whole number renders without
		# any decimals at all: a live pressure readout drifts 29.9 -> 30 ->
		# 30.1 and the panel width jumps with it. `trailing_zeros` overrides
		# that derivation with a stable width. See __resolveTrailingZeros.
		trailing = params.get('trailing_zeros', 'off')
		# Exact zero is exempt by default, because a bare '0' is meaningful:
		# it says the value is *actually* zero, where '0.0' says "not zero,
		# but rounds to it at this width". That distinction holds at default
		# settings - Inch(0) renders '0' while Inch(0.004) renders '0.0'.
		#
		# `true_zero=False` gives it up in exchange for a column that never
		# changes width, which is the better trade wherever zero is a common
		# reading rather than a catastrophe - precipitation, wind.
		if trailing not in (False, None, 'off') \
				and (floatValue != 0 or not params.get('true_zero', True)):
			intDigits = intLength - bool(params.get('leadingZeroDropped'))
			# The configured precision, NOT params['precision'] - the latter
			# has already been clamped down to the value's own decimal count,
			# which is exactly the clamp this option exists to override. An
			# explicit `precision=` in the spec outranks the class default.
			configured = params.explicitPrecision
			if configured is None:
				configured = getattr(value, '_precision', None)
			params['precision'] = self.__resolveTrailingZeros(
				trailing,
				configured=None if configured is None else int(configured),
				fallback=int(params['precision']),
				room=max(int(params['digit_budget']) - intDigits, 0),
			)
			params['type'] = 'f'

		# determine if a plural unit should be used
		if params.get('unit_type', 'unit') == 'name':
			unit = params.get('name', value.name)
		else:
			unit = params.get('unit', value.unit)

		is_plural = round(floatValue, int(params['precision'])) != 1
		if is_plural:
			if params.get('plural', False) or unit == 'plural':
				unit = value.pluralUnit if params.get('unit_type', 'unit') != 'name' else type(value).pluralName
				precisionSpec['unit'] = unit

		for key, opts in formatVarsSpecs.items():
			spec = opts['spec']
			try:
				v = getFrom(key, value, self, params, locals(), globals())
			except KeyError:
				raise FormattingError(f'Invalid format variable {key!r} in {formatString!r} while formatting {self!r}')
			if spec and key not in {'format', 'self', 'value'}:
				try:
					v = f'{v:{spec}}'
				except ValueError as e:
					log.error(f'Error formatting {key} with {spec}: "{e}" while formatting {self}')
					# if msg := next(iter(e.args), '').startswith('Unknown format code'):
					# 	t = FormatSpec.precision.search(spec).groupdict()['type']
					# 	spec = spec.removesuffix(t)
					v = f'{v}'
			formatVarsSpecs[key] = v

		# params = value.__format_class__(formatSpec, params)
		formatString = value.__replace_format_attrs__(formatString, params)

		# params = {k: v if v is not None else '' for k, v in params.items() if not k.startswith('_')}
		# for k, v in params.items():
		# 	if k in {'precision', 'minwidth'} and v:
		# 		params[k] = int(v)

		params['value'] = value.__format_value__(params)
		if params.get('leadingZeroDropped', False):
			# leading_zero off for a value between -1 and 1: drop the '0'
			# before the radix point ('0.01' -> '.01', '-0.5' -> '-.5').
			# The precision computed above already assumed this, so the
			# digit it frees has gone to a decimal place.
			params['value'] = params['value'].replace('0.', '.', 1)

		formattedValue = formatString.format(**params)

		return formattedValue

	def __format_class__(self, formatSpec: str, formatParams: Mapping) -> dict:
		"""Per-class hook to adjust format params before rendering.

		UNUSED, INTENTIONALLY KEPT. No subclass overrides it and its only
		call site is commented out (see `# params = value.__format_class__(...)`
		above), so today it is a no-op returning its input unchanged.

		Kept because the capability is wanted: a unit class should be able to
		apply its own formatting rules without every caller knowing about
		them. `Direction` is the shape of the use case - it currently reaches
		the same end by overriding `__format_value__` and `__format_template__`
		separately, which this hook would have covered in one place.

		To revive: uncomment the call site and have it merge the returned
		mapping into `params`.
		"""
		return formatParams

	def __replace_format_attrs__(self, formatString: str, formatParams: Mapping) -> str:
		formatVars = {**formatParams.get('formatVars', {}), **dict(formatParams)}
		self = formatParams.get('self', self)
		for obj, attr, *frmt in re.findall(r'{(?P<obj>\w+)\.(?P<attr>[\w.]+\w)(:.+?)?}', formatString):
			if obj not in formatVars:
				if (attr_ := (getattr(self, obj, None))) is not None:
					formatParams[obj] = attr_
				continue
			obj = formatVars[obj]
			while '.' in attr:
				attr, sub_attr = attr.split('.', 1)
				obj = getattr(obj, attr, None)
				if obj is None:
					break
				attr = sub_attr
			value = getattr(obj, attr, obj)
			formatString = formatString.replace(f'{{{obj}.{attr}}}', str(value))
		return formatString

	@staticmethod
	def __resolveTrailingZeros(mode, configured: int | None, fallback: int, room: int) -> int:
		"""How many decimal places to render, ignoring the value's own content.

		`precision` is normally derived per value from how many decimals that
		value actually has, which is why 30.0 renders '30' while 29.92 renders
		'29.9'. For anything read at a glance - a dashboard panel, a column of
		figures - that instability is the problem, not a feature: the width
		changes as the value crosses a whole number.

		  mode          | 30.0 at precision=2, budget=5
		  --------------|------------------------------
		  'off'         | 30      (default; today's behaviour)
		  'precision'   | 30.00   (pad to the configured precision)
		  'fill'        | 30.000  (pad to whatever the budget allows)
		  <int>         | exactly that many places

		`True` is accepted as an alias for 'precision', and 'off'/False/None
		all mean off - the spec parser already folds 'off' to False.

		Every mode is capped by `room` (the budget minus the integer digits),
		so trailing zeros can never push a value over its digit budget.
		"""
		if mode is True or mode == 'precision':
			target = configured if configured is not None else fallback
		elif mode == 'fill':
			target = room
		else:
			try:
				target = int(mode)
			except (TypeError, ValueError):
				target = fallback
		return max(0, min(int(target), room))

	@staticmethod
	def __intDigits(params: Mapping, floatValue: float, intLength: int, max_: int, precision: int) -> int:
		"""How many digits the integer part will actually occupy on screen.

		Only ever differs from `intLength` for a value between -1 and 1,
		where the integer part is the lone '0' before the radix point. That
		'0' carries no information, so dropping it frees a digit of the
		`max` budget for a decimal place.

		`leading_zero` is three-state:

		- ``True``   - always keep it
		- ``False``  - always drop it
		- ``'auto'`` (default) - **drop it only when keeping it would render
		  the value as zero, and dropping actually rescues a digit of it.**

		That last condition matters. Keying purely off the configured
		precision drops the zero whenever the budget is tight, which buys
		nothing but a trailing zero: 0.5 became '.50' and 0.9697 became
		'.970' - same digit count, no more information, worse to read. The
		zero is only worth spending when the alternative is showing nothing
		at all, so 0.01 at a 2-digit budget becomes '.01' rather than '0.0',
		while 0.5 keeps its zero and 0.0416 at a 1-digit budget stays '0'
		(dropping would only give '.0', equally empty).
		"""
		if not 0 < abs(floatValue) < 1:
			return intLength
		leading_zero = params.get('leading_zero', 'auto')
		if leading_zero is True:
			return intLength
		if leading_zero is False:
			return 0
		kept = max(min(precision, max_ - intLength), 0)
		if round(abs(floatValue), kept) != 0:
			return intLength  # already shows something; nothing to gain
		dropped = max(min(precision, max_), 0)
		return 0 if round(abs(floatValue), dropped) != 0 else intLength

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
		if params.get('unit_symbol', None):
			formatTemplate.append('{unit_symbol}')
		# An empty unit is not the same as an omitted one: `'' is not False`
		# passed the old check, so dimensionless units (Angle, Direction)
		# emitted the spacer before an empty string and rendered '180° '
		# with a trailing space. Nothing to separate means no separator.
		unit = params.get('unit', self.unit)
		if params.get('show_unit', self.show_unit) and unit is not False and unit:
			if params.get('unit_spacer', self.unit_spacer):
				formatTemplate.append('{unit_spacer}')
			formatTemplate.append('{unit}')
		if params.get('suffix', None):
			formatTemplate.append('{suffix}')

		return ''.join(formatTemplate)

	@property
	def defaultFormatParams(self):
		return {
			'leading_zero':  self.leading_zero,
			'trailing_zeros': self.trailing_zeros,
			'true_zero':     self.true_zero,
			'align':        '',
			'fill':         '',
			'sign':         '',
			'minwidth':     '',
			'precision':    self.precision,
			'value':        self,
			'type':         'g',
			'unit_symbol':    self.unit_symbol,
			'unit_spacer':   self.unit_spacer,
			'unit':         self.unit,
			'show_unit':     self.show_unit,
			'suffix':       self.suffix,
			'digit_budget': self.digit_budget,
			'limits':       self._limits,
			'shorten':      self.shorten,
		}

	@property
	def transferable_defaults(self) -> set[str]:
		return self.__transferable__

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
		if decorator := getattr(self, 'unit_symbol', None):
			attrs['unit_symbol'] = decorator
		if maxLength := getattr(self, 'max', None):
			attrs['maxLength'] = maxLength
		if precision := getattr(self, '_precision', None):
			attrs['precision'] = precision
		if show_unit := getattr(self, 'show_unit', None):
			attrs['show_unit'] = show_unit
		if shorten := getattr(self, 'shorten', None):
			attrs['shorten'] = shorten
		if (limits := getattr(self, '_limits', None)) and limits != (-inf, inf):
			attrs['limits'] = limits
		return attrs

	def __repr_value__(self) -> str:
		return f'{self: format={"{value}{unit_symbol}"}, type=g, shorten=False}'

	if DEBUG:

		def __repr__(self):
			properties = self.properties
			properties['shorten'] = False
			attrsString = ', '.join(f'{k}={str(v)}' for k, v in properties.items())

			if (auto_value := getattr(self, 'auto', None)) is not None:
				if (auto_type := type(auto_value)) is not type(self):
					attrsString = f'auto={auto_value}, ' + attrsString
			else:
				auto_type = type(self)

			if (best_fit := getattr(self, 'bestFit', None)) is not None:
				best_fit = best_fit()
				if type(best_fit) is not auto_type:
					attrsString = f'bestFit={best_fit}, ' + attrsString

			return f'{type(self).__name__}(value={self.__repr_value__()}, {attrsString})'

	else:
		def __repr__(self):
			return f'{type(self).__name__}({self.__repr_value__()})'

	def __bool__(self):
		return super().__bool__() or bool(self.unit)

	def __float__(self) -> float:
		return super().__float__()

	def __round__(self, n=None):
		value = super().__round__(n)
		value = self.__class__(value)
		value.__dict__.update(self.__dict__)
		return value

	def __hash__(self):
		return hash(round(self, max(self._precision, 1)))

	def __dir__(self):
		return list(self.properties) + ['__class__', '__module__', '__doc__', 'defaultFormat', 'defaultFormatParams']

	@property
	def valueUnset(self) -> bool:
		return self == nan

	@property
	def withUnit(self) -> str:
		return f'{self:show_unit: True}'

	@property
	def withoutUnit(self) -> str:
		return f'{self:show_unit=False}'

	@property
	def unit(self) -> str:
		if (unit := getattr(self, '_unit', None)) is None:
			return type(self).unit
		return unit

	@unit.setter
	def unit(self, value: str):
		self._unit = value

	@property
	def pluralUnit(self) -> str:
		if (pluralUnit := getattr(self, '_pluralUnit', None)) is None:
			return type(self).pluralUnit
		return pluralUnit

	@pluralUnit.setter
	def pluralUnit(self, value: str):
		self._pluralUnit = value

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
	def int(self) -> int:
		return int(self)

	@property
	def typedInt(self) -> '_SmartFloat':
		return self.__class__(int(self))

	@property
	def rounded(self) -> '_SmartFloat':
		return self.__class__(round(float(self)))

	@property
	def roundedInt(self) -> int:
		return int(round(float(self)))

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
	def show_unit(self) -> bool:
		return getattr(self, '_show_unit', True)

	@show_unit.setter
	def show_unit(self, value):
		self._show_unit = value

	@property
	def leading_zero(self) -> bool:
		"""Render the '0' before the radix point on values between -1 and 1.

		Three-state, defaulting to ``'auto'``: keep the zero unless keeping it
		would cost a decimal place. 0.5 stays '0.5'; 0.01 becomes '.01'
		rather than a useless '0.0', because the zero it drops is the digit
		the hundredths place needed.

		Force it either way per unit type in [UnitProperties] -
		``leading_zero=True`` where the zero aids legibility at a distance,
		``leading_zero=False`` to always reclaim the digit.
		"""
		return getattr(self, '_leading_zero', 'auto')

	@leading_zero.setter
	def leading_zero(self, value):
		self._leading_zero = value

	@property
	def trailing_zeros(self):
		"""Pad decimals to a stable width instead of the value's own content.

		By default (``'off'``) `precision` is derived per value from how many
		decimals that value actually has, so 29.92 renders '29.9' but 30.0
		renders '30' - a live readout changes width as it crosses a whole
		number. Set this where the value is read at a glance:

		  ``'precision'``  pad to the configured precision  -> '30.00'
		  ``'fill'``       pad to whatever the budget allows -> '30.000'
		  ``<int>``        exactly that many decimal places
		  ``'off'``        the derived, variable width (default)

		Always capped by `digit_budget`, so padding can never push a value
		over its budget. ``True`` is an alias for ``'precision'``.
		"""
		return getattr(self, '_trailing_zeros', 'off')

	@trailing_zeros.setter
	def trailing_zeros(self, value):
		self._trailing_zeros = value

	@property
	def true_zero(self) -> bool:
		"""Keep an exact zero bare, even when `trailing_zeros` is padding.

		A bare '0' carries information: it says the value is *actually* zero,
		where '0.0' says "not zero, but rounds to it at this width". At
		default settings that distinction holds - Inch(0) renders '0' while
		Inch(0.004) renders '0.0'.

		Default ``True``, which preserves it. Set ``False`` where a column
		that never changes width matters more than the distinction, which is
		most places zero is an ordinary reading rather than an emergency -
		precipitation, wind speed, lightning strikes. Then zero pads like
		any other value: '0.00'.

		No effect unless `trailing_zeros` is on; without it zero renders bare
		regardless.
		"""
		return getattr(self, '_true_zero', True)

	@true_zero.setter
	def true_zero(self, value):
		self._true_zero = value

	@property
	def unit_symbol(self) -> str:
		return getattr(self, '_unit_symbol', empty)

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
	def digit_budget(self) -> int:
		return self._digit_budget

	@digit_budget.setter
	def digit_budget(self, value: int):
		self._digit_budget = value

	@property
	def shorten(self) -> bool:
		return getattr(self, '_shorten', False)

	@shorten.setter
	def shorten(self, value):
		self._shorten = value

	@property
	def unit_spacer(self):
		spacer = getattr(self, '_unit_spacer', False)
		if isinstance(spacer, str):
			return spacer
		return " " if spacer else ""

	@unit_spacer.setter
	def unit_spacer(self, value):
		self._unit_spacer = value
