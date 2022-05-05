from math import inf

from functools import lru_cache
import logging
from datetime import datetime
from typing import Callable, ClassVar, Dict, List, Optional, Type

from .. import errors
from ..utils import HashSlice, loadUnitLocalization
from . import SmartFloat

__all__ = ['Measurement', 'DerivedMeasurement']

log = logging.getLogger('WeatherUnits')


class Measurement(SmartFloat):
	_derived = False
	_type: type = None
	_updateFunction: Optional[Callable] = None
	_timestamp: datetime
	_indoor: bool = False
	_calculated: bool = False
	_category: str = None
	_subTypes: ClassVar[Dict[str, Type['Measurement']]]

	def __new__(cls, value, title: str = None, key: str = None, timestamp: datetime = None, **kwargs):
		value = sorted((*cls.limits, float(value)))[1]
		return SmartFloat.__new__(cls, value)

	def __class_getitem__(cls, item):
		if (underItem := f'_{item}') in cls.__annotations__:
			return cls.__annotations__[underItem]
		if item in cls.__dict__:
			return cls.__dict__[item]
		if issubclass(item, Measurement):
			parentType = cls._type
			name = f'{parentType.__name__}[{item.__name__}]'
			newCls = type(name, (item, cls,), {})
			return newCls
		raise TypeError(f'{cls.__name__} does not support {item}')

	def __init__(self, value, title: str = None, key: str = None, timestamp: datetime = None, category: str = None):
		if isinstance(value, Measurement):
			if value._timestamp and timestamp is None:
				timestamp = value._timestamp
		if title:
			self._title = title
		if key:
			self._key = key
		self.category = category

		self._timestamp = timestamp

		SmartFloat.__init__(self, value)

	@property
	def category(self):
		if self._category is None:
			return self.__class__.__name__.lower()
		return self._category

	@category.setter
	def category(self, value):
		self._category = value

	@property
	def localize(self):
		if self.convertible:
			try:
				selector = loadUnitLocalization(type(self), self._config)
				selector = 'inch' if selector == 'in' else selector
				new = getattr(self, selector)
				new.title = self.title
				return new
			except AttributeError or KeyError as e:
				errors.Conversion.BadConversion("Unable to get localized type for {}".format(self.name), e)
		else:
			return self

	@property
	def convertible(self):
		try:
			return self._type.__name__.lower() in self._config.localUnits
		except AttributeError:
			return False

	@property
	def str(self):
		return str(self)

	@property
	def type(self) -> type:
		return self._type if self._type is not None else self.__class__.__mro__[0]

	@property
	def timestamp(self) -> datetime:
		return self._timestamp

	@property
	def updateFunction(self):
		return self._updateFunction

	@updateFunction.setter
	def updateFunction(self, function: callable):
		self._updateFunction = function

	@property
	def indoor(self) -> bool:
		return self._indoor

	@indoor.setter
	def indoor(self, value: bool):
		self._indoor = value

	@property
	def calculated(self):
		return self._calculated

	@calculated.setter
	def calculated(self, value):
		self._calculated = value

	def _convert(self, other):
		if isinstance(other, self.type):
			return self.__class__(other)
		if isinstance(other, (float, int)):
			return self.__class__(other)
		else:
			return other

	def transform(self, other, transformTo: type = None):
		if isinstance(other, type) and issubclass(other, Measurement):
			other = other(self)
		nonTransferred = ['_unit', '_suffix', '_scale', '_denominator', '_numerator']
		if self.type != other.type:
			log.warning(f'{self.withUnit} and {other.withUnit} are not identical types, this may cause issues')
		other.__dict__.update({key: value for key, value in self.__dict__.items() if key not in nonTransferred and value is not None})
		if other._updateFunction:
			other._updateFunction(other)
		return other

	def __eq__(self, other):
		if isinstance(other, SmartFloat):
			if not self.__class__ == other.__class__:
				try:
					other = self._convert(other)
				except errors.BadConversion:
					pass
			precision = min(self.precision, other.precision)
			return round(self, precision) == round(other, precision)
		elif isinstance(other, self._acceptedTypes):
			return self._convert(other) == self

	def __getitem__(self, item):
		try:
			return self.__getattribute__(item)
		except AttributeError:
			raise errors.Conversion.UnknownUnit(self, item)

	def __mul__(self, other):
		if isinstance(other, self.type):
			other = self._convert(other)
		if isinstance(other, self._acceptedTypes):
			other = self._convert(other)
		return self._convert(super().__mul__(other))

	def __add__(self, other):
		if isinstance(other, self.type):
			other = self._convert(other)
		elif isinstance(other, self._acceptedTypes):
			other = self._convert(other)
		return self._convert(super().__add__(other))

	def __radd__(self, other):
		if isinstance(other, self.type):
			other = self._convert(other)
		elif isinstance(other, self._acceptedTypes):
			other = self._convert(other)
		return self._convert(super().__radd__(other))

	def __sub__(self, other):
		if isinstance(other, self.type):
			other = self._convert(other)
		elif isinstance(other, self._acceptedTypes):
			other = self._convert(other)
		return self._convert(super().__sub__(other))

	def __rsub__(self, other):
		if isinstance(other, self.type):
			other = self._convert(other)
		elif isinstance(other, self._acceptedTypes):
			other = self._convert(other)
		return self._convert(super().__rsub__(other))

	def __pow__(self, power, modulo=None):
		if isinstance(power, self.type):
			power = self._convert(power)
		elif isinstance(power, self._acceptedTypes):
			power = self._convert(power)
		return self._convert(super().__pow__(power, modulo))

	def __truediv__(self, other):
		if isinstance(other, self.type):
			other = self._convert(other)
		elif isinstance(other, self._acceptedTypes):
			other = self._convert(other)

		if isinstance(other, self.type):
			value = super().__truediv__(self._convert(other))

		elif issubclass(self.__class__, DerivedMeasurement) and not isinstance(other, Measurement):
			return DerivedMeasurement(self, self.denominator.__class__(other))

		elif not isinstance(other, Measurement):
			value = super().__truediv__(float(other))

		elif issubclass(other.__class__, Measurement):
			return DerivedMeasurement(self, other)

		else:
			value = self / other

		return self._convert(value)

	def __gt__(self, other):
		if isinstance(other, self.type):
			other = self._convert(other)
		elif isinstance(other, self._acceptedTypes):
			other = self._convert(other)
		return super().__gt__(other)

	def __lt__(self, other):
		if isinstance(other, self.type):
			other = self._convert(other)
		elif isinstance(other, self._acceptedTypes):
			other = self._convert(other)
		return super().__lt__(other)

	def __ge__(self, other):
		if isinstance(other, self.type):
			other = self._convert(other)
		elif isinstance(other, self._acceptedTypes):
			other = self._convert(other)
		return super().__ge__(other)

	def __le__(self, other):
		if isinstance(other, self.type):
			other = self._convert(other)
		elif isinstance(other, self._acceptedTypes):
			other = self._convert(other)
		return super().__le__(other)

	def __hash__(self):
		return hash(round(self, max(self._precision, 1)))

	## Transform shortcuts ##

	def __or__(self, other):
		return self.transform(other)

	def __lshift__(self, other):
		return self.transform(other)


class DerivedMeasurement(Measurement):
	_derived = True
	_type: Type[Measurement] = Measurement
	_numerator: Measurement
	_denominator: Measurement
	numeratorClass: Type[Measurement]
	denominatorClass: Type[Measurement]

	def __new__(cls, numerator: Measurement, denominator: Measurement = 1, *args, **kwargs):
		if not cls.numeratorClass.isGenericType:
			numerator = cls.numeratorClass(numerator)
		if not cls.denominatorClass.isGenericType:
			denominator = cls.denominatorClass(denominator)
		value = float(numerator)/float(denominator)

		if isinstance(numerator, cls.numeratorClass) and isinstance(denominator, cls.denominatorClass):
			if cls.isGenericType:
				cls = cls[type(numerator):type(denominator)]
		elif items := [i for i in cls._subTypes if i['denominatorClass'] is type(denominator)]:
			if len(items) == 1:
				cls = items[0]
			else:
				items = [i for i in items if i['numeratorClass'] is type(numerator)]
				if len(items) == 1:
					cls = items[0]
				else:
					raise TypeError(f'{cls.__name__} does not support {numerator.__class__.__name__} as numerator')
		elif cls.isGenericType:
			cls = cls[type(numerator):type(denominator)]
		return Measurement.__new__(cls, value, *args, **kwargs)

	def __init_subclass__(cls, **kwargs):
		super().__init_subclass__(**kwargs)
		if 'numeratorClass' not in cls.__dict__:
			cls.numeratorClass = cls.__annotations__.get('_numerator', getattr(cls.__mro__[1], 'numeratorClass', cls.__mro__[1].__annotations__.get('_numerator', Measurement)))
		if 'denominatorClass' not in cls.__dict__:
			cls.denominatorClass = cls.__annotations__.get('_denominator', getattr(cls.__mro__[1], 'denominatorClass', cls.__mro__[1].__annotations__.get('_denominator', Measurement)))

	def __class_getitem__(cls, item):
		return cls.__getSlice__(cls, HashSlice(item))

	@lru_cache(maxsize=32)
	def __getSlice__(cls, item: HashSlice):
		fixedN, fixedD = cls.fixedUnits
		# if (underItem := f'_{item}') in cls.__annotations__:
		# 	return cls.__annotations__[underItem]
		if item in cls.__dict__:
			return cls.__dict__[item]
		if item.isSlice:
			sliceNType, sliceDType = fixedN or item.start, fixedD or item.stop
			nType, dType = cls.numeratorClass, cls.denominatorClass
			if sliceNType is not None and not isinstance(sliceNType, type):
				sliceNType = type(sliceNType)
			if sliceDType is not None and not isinstance(sliceDType, type):
				sliceDType = type(sliceDType)
			parentType = cls._type
			sameDType = {i for i in parentType.subTypes if i.denominatorClass is sliceDType}
			sameNType = {i for i in parentType.subTypes if i.numeratorClass is sliceNType}

			if exactMatch := sameDType & sameNType:
				return exactMatch.pop()

			if sameDType and (generics := {i for i in sameDType if i.numeratorClass.isGenericType}):
				if len(generics) == 1:
					generic = generics.pop()
					if not dType.isGenericType:
						return generic[sliceNType or nType]
					if generic.denominatorClass is sliceDType:
						return generic[sliceNType or nType]
			if sameNType and (generics := {i for i in sameNType if i.denominatorClass.isGenericType}):
				if len(generics) == 1:
					generic = generics.pop()
					if not nType.isGenericType:
						return generic[sliceDType or dType]
					if generic.numeratorClass is sliceNType:
						return generic[sliceDType or dType]

			name = f'{parentType.__name__}[{item.start.__name__}/{item.stop.__name__}]'
			return type(name, (parentType,), {'numeratorClass': sliceNType, 'denominatorClass': sliceDType})
		parentType = cls._subType
		item = item.start
		if issubclass(item, cls.numeratorClass):
			if not cls.denominatorClass.isGenericType:
				name = f'{cls.__name__}'
				newCls = type(name, (cls,), {'numeratorClass': item, 'denominatorClass': cls.denominatorClass})
				return newCls
			print(f'{cls.__name__} does not support {item.__name__} as numerator')

		elif issubclass(item, cls.denominatorClass):
			if not cls.numeratorClass.isGenericType:
				name = f'{cls.__name__}[{item.__name__}]'
				newCls = type(name, (cls,), {'denominatorClass': item})
				return newCls
			print(f'{cls.__name__} does not support {item.__name__} as denominator')
		return parentType[item]

	def __init__(self, numerator, denominator=None, *args, **kwargs):
		if isinstance(numerator, DerivedMeasurement) and denominator is None:
			self._numerator = numerator.numerator
			self._denominator = numerator.denominator
		elif denominator is None:
			self._numerator = numerator
			self._denominator = self.denominatorClass(1)
		else:
			self._numerator = numerator
			self._denominator = denominator
		if not isinstance(self._numerator, self.numeratorClass):
			self._numerator = self.numeratorClass(self._numerator)
		if not isinstance(self._denominator, self.denominatorClass):
			self._denominator = self.denominatorClass(self._denominator)
		Measurement.__init__(self, float(self._numerator)/float(self._denominator), *args, **kwargs)

	def __pow__(self, power, modulo=None):
		return self.__class__(super(Measurement, self).__pow__(power, modulo), self._denominator)

	def transform(self, other, transformTo: type = None):
		if isinstance(other, type) and issubclass(other, Measurement):
			other = other(self)
		nonTransferred = ['_unit', '_suffix', '_scale', '_denominator', '_numerator']
		if self.type != other.type:
			log.warning(f'{self.withUnit} and {other.withUnit} are not identical types, this may cause issues')
		other.__dict__.update({key: value for key, value in self.__dict__.items() if key not in nonTransferred and value is not None})
		if other._updateFunction:
			other._updateFunction(other)
		return other

	def _convert(self, other):
		if isinstance(other, (int, float)):
			return self.__class__(self.n.__class__(other), self.d.__class__(1))
		if isinstance(other, self.n.type):
			try:
				other = other[self.n.unit]
			except AttributeError:
				pass
			return self.__class__(other, self.d)
		else:
			return super(DerivedMeasurement, self)._convert(other)

	# TODO: Implement into child classes
	def _getUnit(self) -> List[str]:
		return self._config['LocalUnits'][str(self._type)].split('/')

	def _getUnitTypes(self):
		return self._numerator.type, self._denominator.type

	@property
	def type(self):
		return type(self)[type(self._numerator):type(self._denominator)]

	@property
	def localize(self):
		try:
			n, d = loadUnitLocalization(type(self), self._config).split('/')
			n = 'inch' if n == 'in' else n

			fixedN, fixedD = type(self).fixedUnits
			if n == '*' and fixedN:
				n = fixedN
			if d == '*' and fixedD:
				d = fixedD

			if isinstance(n, type):
				n = n._unit
			if isinstance(d, type):
				d = d._unit

			n = getattr(self._numerator, n)
			d = getattr(self._denominator, d)

			t = getattr(self, '_subType', self._type)
			tFN, tFD = t.fixedUnits
			if (tFN is not None and tFN != n) or (tFD is not None and tFD != d):
				t = t.__parent_class__

			newCls = t[type(n):type(d)]
			return newCls(n, d)
		except KeyError:
			log.error('Measurement {} was unable to localize from {}'.format(self.name, self.unit))
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
