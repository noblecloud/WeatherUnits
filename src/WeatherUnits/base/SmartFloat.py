import logging
from typing import Union

from math import nan, log as lg, isnan
from decimal import Decimal

from ..utils import PropertiesFromConfig
from ..config import config, Config

log = logging.getLogger('SmartFloat')

__all__ = ['SmartFloat']


class Meta(type):
	defaults = config.unitDefaults

	def __new__(cls, name, bases, dct):
		cls = super().__new__(cls, name, bases, dct)
		for prop in {key: value for key, value in Meta.defaults.items() if key not in dct.keys()}.items():
			setattr(cls, *prop)
		cls = PropertiesFromConfig(cls, config)
		cls._config = config
		return cls


class SmartFloat(float, metaclass=Meta):
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
	_subscriptionKey: str
	_sizeHint: str
	_forcePrecision: bool

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
		value = cls.noneToNan(value)
		return float.__new__(cls, value)

	def __init__(self, value):
		# if isinstance(value, SmartFloat):
		# 	self._title = value._title if value._title is not None else self._title
		value = self.noneToNan(value)
		self._exp, _ = self.expPrecision(value)
		float.__init__(value)

	def expPrecision(self, value: float):
		if value != 0 and not isnan(value):
			exp = int(lg(abs(value), 10))
			precision = abs(Decimal(str(abs(value))).as_tuple().exponent)
		else:
			exp = 0
			precision = 0

		return exp, precision

	def _string(self, hintString: bool = False, forceUnit: bool = None, multiplier: Union[int, float] = 1.0) -> str:
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

		# TODO: Allow for precision to be overridden if number is scaled.  (10,110 becomes 10.11k instead of 10.1k)
		newScale, decimal = self.expPrecision(valueFloat)
		decimal += 1

		# Max amount of precision that can be displayed while keeping string under max length
		intAllowedPrecision = max(0, self._max - newScale)
		precision = min(self._precision, abs(Decimal(str(abs(valueFloat))).as_tuple().exponent))
		if hintString and decimal < precision and decimal < intAllowedPrecision:
			decimal = 1
		# Allow at least on level of precision if
		# Removed 1 if not decimal and c else decimal

		showUnit = self._showUnit if forceUnit is None else forceUnit
		decimal = max(intAllowedPrecision, precision) if self._forcePrecision else min(precision, intAllowedPrecision, decimal)
		formatStr = f"{{:{',' if self._kSeparator else ''}.{decimal}f}}"
		valueString = formatStr.format(10 ** max(newScale - 1, 0) if hintString else valueFloat)
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
	def name(self):
		return self.__class__.__name__

	@property
	def title(self):
		return self._title if self._title else self.name

	@title.setter
	def title(self, value):
		self._title = value

	@property
	def subscriptionKey(self) -> str:
		if self._subscriptionKey:
			return self._subscriptionKey
		else:
			t = self.title
			t = t.lower() if t.isupper() else t
			t = t.replace(' ', '')
			return f"{t[0].lower()}{t[1:]}"

	@subscriptionKey.setter
	def subscriptionKey(self, value: str):
		self._subscriptionKey = value

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
		self._decorator

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


