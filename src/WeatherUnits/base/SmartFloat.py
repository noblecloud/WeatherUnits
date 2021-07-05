import logging
from typing import Union

from math import nan

from ..utils import PropertiesFromConfig
from ..config import config, Config

log = logging.getLogger('SmartFloat')

__all__ = ['SmartFloat']


class Meta(type):
	def __new__(cls, name, bases, dct):
		cls = super().__new__(cls, name, bases, dct)
		for prop in {key: value for key, value in defaults.items() if key not in dct.keys()}.items():
			setattr(cls, *prop)
		cls = PropertiesFromConfig(cls)
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
		self._exp, decimal = list(len(n) for n in str(float(value)).split('.'))
		self._precision = min(self._precision, decimal)
		float.__init__(value)

	def _string(self, hintString: bool = False, forceUnit: bool = False) -> str:
		if self._shorten:
			c, valueFloat = 0, float(self)
			numberLength = len(str(int(valueFloat)))
			while numberLength > 3 and numberLength >= self._max:
				c += 1
				valueFloat /= 1000
				numberLength = len(str(int(valueFloat)))
			suffix = ['', 'k', 'm', 'B'][c]
		else:
			valueFloat = self
			c = False
			suffix = ''

		# TODO: Allow for precision to be overridden if number is scaled.  (10,110 becomes 10.11k instead of 10.1k)
		newScale, decimal = list(len(n) for n in str(round(valueFloat, self._precision)).strip('0').split('.'))

		# Max amount of precision that can be displayed while keeping string under max length
		intAllowedPrecision = max(0, self._max - newScale)

		# Allow at least on level of precision if
		# Removed 1 if not decimal and c else decimal
		decimal = min(self._precision, intAllowedPrecision, decimal)
		formatStr = f"{{:{',' if self._kSeparator else ''}.{decimal}f}}"
		valueString = formatStr.format(10 ** max(newScale - 1, 0) if hintString else valueFloat)
		needsSpacer = (self._unitSpacer and self._showUnit) and (forceUnit and self._unitSpacer and not hintString) or c
		spacer = " " if needsSpacer else ""
		unit = self._unit if self._showUnit and forceUnit else ''
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
	def sizeHint(self) -> int:
		# length = len(string) - (0.5 * (string.count('.') + string.count(','))
		return self._string(hintString=True).replace('1', '0') if self._sizeHint is None else self._sizeHint

	@property
	def decorator(self):
		self._decorator
