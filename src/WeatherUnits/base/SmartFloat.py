import logging
from typing import ClassVar, Optional, Set, Type, Union

from math import nan, isnan, inf
from decimal import Decimal

from ..utils import setPropertiesFromConfig
from ..config import config, Config

log = logging.getLogger('SmartFloat')

__all__ = ['SmartFloat']


class Meta(type):
	_derived: ClassVar[bool]

	# def __new__(cls, name, bases, dct):

	@property
	def isGenericType(cls):
		if '__isNamedType' in cls.__dict__:
			return cls.__dict__['__isNamedType']
		if '_unitSystem' in cls.__dict__:
			return cls.__dict__['_unitSystem'] is cls
		return False

	@property
	def isDerived(cls) -> bool:
		if not hasattr(cls, '_derived'):
			cls._derived = getattr(cls.__parent_class__, 'isDerived', None)
		return cls._derived

	@property
	def isScaling(cls) -> bool:
		return hasattr(cls, '_Scale')

	@property
	def __parent_class__(cls):
		return cls.__mro__[1]

	@property
	def subTypes(cls):
		subs: Set[Type['Measurement']] = set()
		if cls.isGenericType:
			for sub in cls.__subclasses__():
				if sub.isGenericType:
					subs.update(sub.subTypes)
				elif sub.isDerived == cls.isDerived:
					subs.add(sub)
		subs.discard(cls)
		return list(subs)

	@property
	def fixedUnits(cls) -> tuple[Optional[Type['Measurement']], Optional[Type['Measurement']]]:
		n: Type['Measurement'] = cls.__annotations__.get('_numerator', None)
		d: Type['Measurement'] = cls.__annotations__.get('_denominator', None)
		if n is not None:
			n = None if n.isGenericType else n
		if d is not None:
			d = None if d.isGenericType else d
		return n, d

	@property
	def limits(cls) -> tuple[Optional[float], Optional[float]]:
		if cls.isDerived:
			return cls.numeratorClass.limits
		return getattr(cls, '_limits', None) or getattr(cls.__parent_class__, 'limits', (0, inf))

	def __repr__(cls):
		if cls.isDerived:
			cls: 'DerivedMeasurement'
			if ((cls.numeratorClass.isGenericType or cls.__parent_class__.numeratorClass.isGenericType)
				and (cls.denominatorClass.isGenericType or cls.__parent_class__.denominatorClass.isGenericType)):
				return f'{cls.__name__}[{repr(cls.numeratorClass)}/{repr(cls.denominatorClass)}]'
			elif cls.numeratorClass.isGenericType or cls.__parent_class__.numeratorClass.isGenericType:
				return f'{cls.__name__}[{repr(cls.numeratorClass)}]'
			elif cls.denominatorClass.isGenericType or cls.__parent_class__.denominatorClass.isGenericType:
				return f'{cls.__name__}[{repr(cls.denominatorClass)}]'
			else:
				return f'{cls.__name__}'
		if cls.isGenericType:
			return f'<{cls.__name__}>'
		return cls.__name__


class SmartFloat(float, metaclass=Meta):
	_limits = 0, inf
	_config: Config
	_precision: int
	_max: int
	_unit: str
	_suffix: str
	_decorator: str
	_unitSpacer: bool
	_title: str
	_exp: int
	_slide: bool
	_showUnit: bool
	_shorten: bool
	_kSeparator: bool
	_combineUnitAndSuffix: bool
	_key: str
	_sizeHint: str
	_forcePrecision: bool
	_acceptedTypes: tuple = (float, int, Decimal)

	def __init_subclass__(cls, **kwargs):
		cls._acceptedTypes = (*kwargs.get('acceptedTypes', ()), *cls._acceptedTypes, cls)

		for prop in {key: value for key, value in config.unitDefaults.items() if key not in cls.__dict__.keys()}.items():
			setattr(cls, *prop)
		setPropertiesFromConfig(cls, config)
		cls._config = config

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
		d, f = [len(i) for i in str(abs(float(value))).split('.')]
		return d, f

	def _string(self, hintString: bool = False, forceUnit: bool = None, multiplier: Union[int, float] = 1.0, asInt: bool = False) -> str:
		if self._shorten:
			c, valueFloat = 0, float(self * multiplier)
			numberLength = len(str(int(valueFloat)))
			while numberLength > 3 and numberLength >= self._max:
				c += 1
				valueFloat /= 1000
				numberLength = len(str(int(valueFloat)))
			suffix = ['', 'k', 'm', 'B'][c]
		else:
			valueFloat = float(self) * multiplier
			c = False
			suffix = ''
		if isnan(valueFloat):
			valueFloat = 0.0

		# TODO: Allow for precision to be overridden if number is scaled.  (10,110 becomes 10.11k instead of 10.1k)
		integerLength, floatingPointLength = self.intFloatLength(valueFloat)
		if floatingPointLength == 1 and valueFloat.is_integer():
			floatingPointLength = 0

		# Max amount of precision that can be displayed while keeping string under max length
		intAllowedPrecision = max(0, self._max - integerLength)
		precision = min(self._precision, integerLength)
		if hintString and floatingPointLength < precision and floatingPointLength < intAllowedPrecision:
			floatingPointLength = 1
		# Allow at least on level of precision if
		# Removed 1 if not decimal and c else decimal

		showUnit = self._showUnit if forceUnit is None else forceUnit
		floatingPointLength = max(intAllowedPrecision, precision) if self._forcePrecision else min(precision, intAllowedPrecision, floatingPointLength)
		formatStr = f"{{:{',' if self._kSeparator else ''}.{0 if asInt else floatingPointLength}f}}"
		valueString = formatStr.format(10 ** max(integerLength - 1, 0) if hintString else valueFloat)
		needsSpacer = (self._unitSpacer and showUnit) and self._unit or c
		spacer = " " if needsSpacer else ""
		unit = self.unit if showUnit else ''
		return f'{valueString}{suffix}{self._decorator}{spacer}{unit}'

	def __str__(self):
		return self._string()

	def __repr__(self):
		return self._string(forceUnit=True)

	def __bool__(self):
		return super().__bool__() or bool(self.unit)

	def __float__(self) -> float:
		return super().__float__()

	def __hash__(self):
		return hash(round(self, max(self._precision, 1)))

	@property
	def valueUnset(self) -> bool:
		return self == nan

	@property
	def withUnit(self):
		return self._string(forceUnit=True)

	@property
	def withoutUnit(self):
		return self._string(forceUnit=False)

	@property
	def unit(self) -> str:
		return self._unit

	@property
	def unitArray(self):
		return [self._unit]

	@property
	def suffix(self):
		return self._suffix

	@property
	def int(self):
		return int(self)

	@property
	def decoratedInt(self):
		return self._string(forceUnit=False, asInt=True)

	@property
	def name(self):
		return self.__class__.__name__

	@property
	def title(self):
		return self._title if self._title else self.name

	@title.setter
	def title(self, value):
		self._title = value

	@property
	def key(self) -> str:
		if self._key:
			return self._key
		else:
			t = self.title
			t = t.lower() if t.isupper() else t
			t = t.replace(' ', '')
			return f"{t[0].lower()}{t[1:]}"

	@key.setter
	def key(self, value: str):
		self._key = value

	@property
	def category(self):
		return self.__class__.__name__

	@property
	def showUnit(self):
		return self._showUnit

	@showUnit.setter
	def showUnit(self, value):
		self._showUnit = value

	@property
	def sizeHint(self) -> str:
		# length = len(string) - (0.5 * (string.count('.') + string.count(','))
		showUnit = not self._unitSpacer
		return self._string(hintString=True, forceUnit=showUnit).replace('1', '0') if self._sizeHint is None else self._sizeHint

	@property
	def decorator(self):
		return self._decorator

	@property
	def precision(self):
		return self._precision

	@precision.setter
	def precision(self, value):
		self._precision = value

	@property
	def max(self):
		return self._max

	@max.setter
	def max(self, value):
		self._max = value

	@property
	def shorten(self):
		return self._shorten

	@shorten.setter
	def shorten(self, value):
		self._shorten = value

	@property
	def unitSpacer(self):
		return self._unitSpacer

	@unitSpacer.setter
	def unitSpacer(self, value):
		self._unitSpacer = value
