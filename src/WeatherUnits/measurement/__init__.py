import logging
from typing import Callable, Optional, Union

from .. import config as _config
from .. import errors as _errors, utils as _utils
from .decorators import *


class UnitMeta(str):
	_power = 1

	def __new__(cls, value):
		return str.__new__(cls, value)

	def __init__(self, value):
		str.__init__(value)

	def __mul__(self, other):
		if isinstance(other, self.__class__):
			self._power += other._power
			return self
		elif isinstance(other, UnitMeta):
			return UnitMeta(self + other)

	def __truediv__(self, other):
		if isinstance(other, self.__class__):
			self._power -= 1
			return self

	def __str__(self):
		if self._power > 1:
			return f"{super().__str__()}{self._power + 176:c}"
		elif self._power < 0:
			return f"{super().__str__()}{abs(self._power) + 176:c}"
		else:
			return super().__str__()


class SmartFloat(float):
	_config = _config
	_precision: int = 1
	_max: int = 3
	_unit: str = ''
	_suffix: str = ''
	_decorator: str = ''
	_unitSpacer = True
	_title: str = ''
	_scale = 1
	_showUnit: bool = True
	_shorten: bool = True
	_thousandsSeparator = False

	def __new__(cls, value):
		return float.__new__(cls, value)

	def __init__(self, value):
		self._scale, decimal = list(len(n) for n in str(float(value)).split('.'))
		self._precision = min(self._precision, decimal)
		if isinstance(value, SmartFloat):
			self._title = value._title
		float.__init__(value)

	def _string(self, hintString: bool = False, forceUnit: bool = False) -> str:
		if self._shorten:
			c, valueFloat = 0, float(self)
			while 4 <= len(str(int(valueFloat))) > self._max:
				c += 1
				valueFloat /= 1000
			suffix = ['', 'k', 'm', 'B'][c]
		else:
			valueFloat = self
			c = False
			suffix = ''

		newScale, decimal = list(len(n) for n in str(round(valueFloat, self._precision)).strip('0').split('.'))
		decimal = min(self._precision, 1 if not decimal and c else decimal)
		formatStr = f"{{:{',' if self._thousandsSeparator else ''}.{decimal}f}}"
		valueString = formatStr.format(10 ** newScale if hintString else valueFloat)
		unit = '' if not self._showUnit or forceUnit else f'{" " if self._unitSpacer else ""}{self._unit}'
		return f'{valueString}{suffix}{self._decorator}{unit}'

	def __str__(self):
		return self._string()

	def __bool__(self):
		return super().__bool__() or bool(self.unit)

	@property
	def withUnit(self):
		return self._string(forceUnit=True)

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
	def showUnit(self):
		return self._showUnit

	@showUnit.setter
	def showUnit(self, value):
		self._showUnit = value

	@property
	def sizeHint(self) -> int:
		# length = len(string) - (0.5 * (string.count('.') + string.count(','))
		return self._string(hintString=True)


class Measurement(SmartFloat):
	_type: type
	_Scale: _utils.ScaleMeta = None
	_updateFunction: Optional[Callable] = None

	def __new__(cls, value):
		return SmartFloat.__new__(cls, value)

	def __init__(self, value, title: str = None):
		if isinstance(value, Measurement):
			if title is not None:
				self._title = title
			else:
				self._title = value.title
			SmartFloat.__init__(self, value)
		SmartFloat.__init__(self, value)

	def __getitem__(self, item):
		try:
			return self.__getattribute__(item)
		except ValueError:
			raise _errors.BadConversion

	@property
	def scale(self):
		return self._Scale[self.name]

	@property
	def localized(self):
		if self.convertible:
			try:
				selector = self._config['Units'][self.type.__name__.lower()]
				selector = 'inch' if selector == 'in' else selector
				new = getattr(self, selector)
				new.title = self.title
				return new
			except AttributeError or KeyError as e:
				_errors.BadConversion("Unable to get localized type for {}".format(self.name), e)
		else:
			return self

	@property
	def convertible(self):
		return self._type.__name__.lower() in self._config['Units']

	@property
	def str(self):
		return str(self)

	@property
	def type(self) -> type:
		return self._type

	@property
	def updateFunction(self):
		return self._updateFunction

	@updateFunction.setter
	def updateFunction(self, function: callable):
		self._updateFunction = function

	def _convert(self, other):
		if isinstance(other, self.type):
			return self.__class__(other)
		else:
			return other

	def __mul__(self, other):
		other = self._convert(other) if isinstance(other, self.type) else other
		return self.__class__(super().__mul__(other))

	def __add__(self, other):
		other = self._convert(other) if isinstance(other, self.type) else other
		return self.__class__(super().__add__(other))

	def __sub__(self, other):
		other = self._convert(other) if isinstance(other, self.type) else other
		return self.__class__(super().__sub__(other))

	def __truediv__(self, other):
		other = self._convert(other)

		if isinstance(other, self.type):
			value = super().__truediv__(self._convert(other))

		elif issubclass(self.__class__, DerivedMeasurement) and not isinstance(other, Measurement):
			return DerivedMeasurement(self, self.denominator.__class__(other))

		elif not isinstance(other, Measurement):
			value = super().__truediv__(float(other))

		elif issubclass(other.__class__, Measurement):
			return DerivedMeasurement(self, other)

		return self.__class__(value)

	def __or__(self, other):
		return self.transform(other)

	def __lshift__(self, other):
		return self.transform(other)

	def transform(self, other):
		if self.type != other.type:
			logging.warning(f'{self.withUnit} and {other.withUnit} are not identical types, this may cause issues')
		other.__dict__.update(self.__dict__)
		if other._updateFunction:
			other._updateFunction(other)
		return other


class MeasurementSystem(Measurement):
	_baseUnit = None
	_unitSystem: type = None

	def __new__(cls, value):
		value: Union[int, float, MeasurementSystem, SystemVariant]
		if isinstance(value, MeasurementSystem) and (not cls._baseUnit or not value.__class__._baseUnit):
			'''For this to work each unit class must have a _baseUnit defined for each scale'''
			raise _errors.NoBaseUnitDefined(cls)
		system = issubclass(cls, MeasurementSystem) and issubclass(value.__class__, MeasurementSystem)
		siblings, cousins = [cls._baseUnit == value._baseUnit, cls._type == value._type] if system else (False, False)
		variant = issubclass(cls, SystemVariant) and issubclass(value.__class__, SystemVariant)

		# If values are siblings change to sibling class with changeScale()
		if siblings:
			# If both are variants convert value to baseUnit first
			value = value._baseUnit(value) if variant else value
			return cls(value.__class__.changeScale(value, cls._Scale[cls.__name__]))

		# If values are cousins initiate with values base sibling causing a recursive call to __new__
		elif cousins:
			return cls.__new__(cls, cls._baseUnit(value.__getattribute__('_' + cls._baseUnit.__name__.lower())()))

		elif isinstance(value, Measurement):
			raise _errors.BadConversion(cls.__name__, value.__class__.__name__)

		else:
			return Measurement.__new__(cls, value)

	def changeScale(self, newUnit: _utils.ScaleMeta) -> Optional[float]:
		if self._Scale:
			multiplier = self.scale * newUnit
			if self.scale > newUnit:
				return float(self) * multiplier
			else:
				return float(self) / multiplier
		else:
			return None

	@property
	def unitSystem(self):
		return self._unitSystem.__name__

	@property
	def isSystemVariant(self):
		return issubclass(self.__class__, SystemVariant)


class SystemVariant:
	_multiplier: float = 1.0


unitFixes = {'mi/hr': 'mph'}


class DerivedMeasurement(Measurement):
	_type = 'derived'
	_numerator: Measurement
	_denominator: Measurement

	def __new__(cls, numerator, denominator):
		value = float(numerator) / float(denominator)
		return Measurement.__new__(cls, value)

	def __init__(self, numerator, denominator):
		self._numerator = numerator
		self._denominator = denominator
		Measurement.__init__(self, float(self._numerator) / float(self._denominator))

	# TODO: Implement into child classes
	def _getUnit(self) -> tuple[str, str]:
		return _config['Units'][self._type].split('/')

	@property
	def localized(self):
		try:
			newClass = self.__class__
			n, d = self._config['Units'][self.type.__name__.lower()].split(',')
			n = 'inch' if n == 'in' else n
			d = self.d.unit if d == '*' else d
			new = newClass(getattr(self._numerator, n), getattr(self._denominator, d))
			new.title = self.title
			return new
		except KeyError:
			logging.error('Measurement {} was unable to localize from {}'.format(self.name, self.unit))
			return self

	@property
	def unit(self):
		if self._unit:
			return self._unit
		elif self._numerator.unit == 'mi' and self._denominator.unit == 'hr':
			return 'mph'
		elif issubclass(self.__class__, DerivedMeasurement):
			l = self.unitArray
			i = 0
			while i < len(l):
				power = 0
				while i + 1 < len(l) and l[i] == l[i + 1]:
					power += 1
					l.pop(i)
				if power:
					unicodePlace = 177 if power < 4 else 0x2074
					l[i] = f"{l[i]}{power + 177:c}"
				i += 1
			return '/'.join(l)
		else:
			return '{}/{}'.format(self._numerator.unit, self._denominator.unit)

	@property
	def unitArray(self) -> list[str]:
		return [*self._numerator.unitArray, *self._denominator.unitArray]

	@property
	def numerator(self) -> Measurement:
		return self._numerator

	n = numerator

	@property
	def denominator(self) -> Measurement:
		return self._denominator

	d = denominator

	@property
	def dArr(self):
		arr = []
		if isinstance(self.n, DerivedMeasurement):
			arr += [*self.n.dArr]
		if isinstance(self.d, DerivedMeasurement):
			arr += [*self.d.dArr]
		else:
			arr += [self.d.unit]
		return arr

	@property
	def nArr(self):
		arr = []
		if isinstance(self.d, DerivedMeasurement):
			arr += [*self.n.nArr]
		if isinstance(self.n, DerivedMeasurement):
			arr += [*self.n.nArr]
		else:
			arr += [self.n.unit]
		return arr
