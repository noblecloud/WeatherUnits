import re
from collections import ChainMap

from functools import lru_cache, cached_property
import logging
from datetime import datetime
from typing import Callable, ClassVar, Dict, List, Optional, Type, Union, Final, Literal, Iterable

__all__ = ['Measurement', 'DerivedMeasurement', 'Dimension', 'metric', 'imperial', 'both', 'Dimensionless', 'Quantity', 'Index', 'NonPlural']

from .. import errors
from . import SmartFloat, FormatSpec, MetaUnitClass
from ..utils import HashSlice
from ..config import config

log = logging.getLogger('WeatherUnits')


class Measurement(SmartFloat):
	__unitDict__ = ChainMap()
	_derived: bool
	_type: type
	_updateFunction: Optional[Callable]
	_timestamp: datetime
	_indoor: bool
	_calculated: bool
	_category: str
	_subTypes: ClassVar[Dict[str, Type['Measurement']]]

	def __init_subclass__(cls, **kwargs):
		if kwargs.get('type', False):
			cls._type = cls

	def __new__(cls, value, title: str = None, key: str = None, timestamp: datetime = None, **kwargs):
		value = sorted((*cls.limits, float(value)))[1]
		return SmartFloat.__new__(cls, value)

	def __class_getitem__(cls, item):
		if (underItem := f'_{item}') in cls.__annotations__:
			return cls.__annotations__[underItem]
		if item in cls.__dict__:
			return cls.__dict__[item]
		if isinstance(item, str):
			item = cls.__findUnitClass__(item)
		if isinstance(item, type) and issubclass(item, Measurement):
			if item in cls.subTypes:
				return item
			parentType = cls.type
			name = f'{parentType.__name__}[{item.__name__}]'
			newCls = type(name, (item, cls,), {})
			return newCls

		raise TypeError(f'{cls.__name__} does not support {item}')

	@classmethod
	def getClass(cls, unit: str) -> Type['Measurement'] | None:
		if isinstance(unit, Iterable) and not isinstance(unit, str):
			unit = ''.join(unit)
		return cls.__findUnitClass__(unit)

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
		if (category := getattr(self, '_category', None)) is None:
			return self.__class__.__name__.lower()
		return self._category

	@category.setter
	def category(self, value):
		self._category = value

	@property
	def localize(self):
		if self.convertible:
			try:
				if (newUnit := type(self).localizedUnit) is not None:
					return newUnit(self)
				return self
			except AttributeError or KeyError as e:
				errors.Conversion.BadConversion("Unable to get localized type for {}".format(self.name), e)
		else:
			return self

	@property
	def convertible(self) -> bool:
		return getattr(self, '_convertable', True)

	@property
	def str(self):
		return str(self)

	@property
	def type(self) -> type:
		return type(self).type

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

	@cached_property
	def valuePrecision(self) -> int:
		_, value = self.intFloatLength(float(self))
		return value

	def transform(self, other, transformTo: type = None):
		if isinstance(other, type) and issubclass(other, Measurement):
			other = other(self)
		nonTransferred = ['_unit', '_suffix', '_scale', '_denominator', '_numerator']
		if self.type != other.type:
			log.warning(f'{self.withUnit} and {other.withUnit} are not identical types, this may cause issues')
		other.__dict__.update({key: value for key, value in self.__dict__.items() if key not in nonTransferred and value is not None})
		if getattr(other, '_updateFunction', None):
			other._updateFunction(other)
		return other

	def __wrapOther(self, other) -> float:
		if type(other) == type(self):
			pass
		elif isinstance(other, self.type):
			if self.unit != other.unit:
				other = self._convert(other)
		elif isinstance(other, (float, int)):
			return self.__class__(other)
		elif isinstance(other, self._acceptedTypes):
			other = self._convert(other)
		elif isinstance(other, str):
			if (other := FormatSpec.number.search(other)) is not None:
				other = other.groupdict()['number']
		return float(other)

	def __eq__(self, other):
		otherPrecision = getattr(other, 'valuePrecision', self.valuePrecision)
		other = self.__wrapOther(other)
		precision = min(self.valuePrecision, otherPrecision)
		selfVal = round(float(self), precision)
		other = round(float(other), precision)
		return selfVal == other

	def __getitem__(self, item):
		try:
			return self.__getattribute__(item)
		except AttributeError:
			if isinstance(item, str):
				return type(self)[item](self)
			raise errors.Conversion.UnknownUnit(self, item)

	def __mul__(self, other):
		other = self.__wrapOther(other)
		return type(self)(super().__mul__(other))

	def __add__(self, other):
		other = self.__wrapOther(other)
		return type(self)(super().__add__(other))

	def __radd__(self, other):
		other = self.__wrapOther(other)
		return type(self)(super().__radd__(other))

	def __sub__(self, other):
		other = self.__wrapOther(other)
		return type(self)(super().__sub__(other))

	def __rsub__(self, other):
		other = self.__wrapOther(other)
		return type(self)(super().__rsub__(other))

	def __pow__(self, power, modulo=None):
		other = self.__wrapOther(power)
		return type(self)(super().__pow__(other, modulo))

	def __truediv__(self, other):
		if isinstance(self, DerivedMeasurement) and not isinstance(other, DerivedMeasurement):
			numerator = type(self.numerator)(other)
			value = numerator/other
			return type(self)(value, self.denominator.__class__(1))

		other = self.__wrapOther(other)
		return type(self)(super().__truediv__(other))

	def __lt__(self, other):
		other = self.__wrapOther(other)
		return super().__lt__(other)

	def __gt__(self, other):
		other = self.__wrapOther(other)
		return super().__gt__(other)

	def __ge__(self, other):
		otherPrecision = getattr(other, 'valuePrecision', self.valuePrecision)
		other = self.__wrapOther(other)
		precision = min(self.valuePrecision, otherPrecision)
		selfVal = round(float(self), precision)
		other = round(float(other), precision)
		return selfVal >= other

	def __le__(self, other):
		otherPrecision = getattr(other, 'valuePrecision', self.valuePrecision)
		other = self.__wrapOther(other)
		precision = min(self.valuePrecision, otherPrecision)
		selfVal = round(float(self), precision)
		other = round(float(other), precision)
		return selfVal <= other

	def __abs__(self):
		return type(self)(super().__abs__())

	def __hash__(self):
		return hash(round(self, max(self._precision, 1)))


class DimensionlessMeta(MetaUnitClass):

	def __new__(cls, name, bases, attrs, **kwargs):
		return super().__new__(cls, name, bases, attrs, **kwargs)

	@property
	def type(cls):
		return getattr(cls, '_type', None) or next((base for base in cls.__mro__ if Dimensionless in base.__bases__), cls)

	@property
	def isGeneric(cls):
		return cls is Dimensionless

	@property
	def dimension(self):
		return Dimensionless


class Dimensionless(SmartFloat.__Dimensionless__, Measurement, metaclass=DimensionlessMeta):
	pass


class NonPlural(SmartFloat.__NonPlural__, Measurement):
	pass


class Quantity(Dimensionless):
	_max = 3
	_precision = 0


class Index(Dimensionless, NonPlural):
	_max = 3
	_precision = 0


class DerivedMeasurementMeta(MetaUnitClass):
	numerator: Type[Measurement]
	_numerator: Type[Measurement]

	denominator: Type[Measurement]
	_denominator: Type[Measurement]

	def __new__(mcs, *args, numerator: Type[Measurement] = None, denominator: Type[Measurement] = None, **kwargs):
		name, bases, attrs, *args = args
		if numerator is None:
			numerator = next((j for i in bases if (j := getattr(i, 'numerator', None)) is not None), None)
		else:
			attrs['_numerator'] = numerator
			annotations = attrs.get('__annotations__', {})
			annotations['numerator'] = Type[numerator]
			attrs['__annotations__'] = annotations

		if denominator is None:
			denominator = next((base_d for base in bases if (base_d := getattr(base, 'denominator', None)) is not Measurement), None)
		else:
			attrs['_denominator'] = denominator
			annotations = attrs.get('__annotations__', {})
			annotations['denominator'] = Type[denominator]
			attrs['__annotations__'] = annotations

		return super().__new__(mcs, name, bases, attrs, **kwargs)

	@property
	def isGeneric(cls):
		return cls.numerator.isGeneric or cls.denominator.isGeneric

	@property
	def numerator(self) -> Type[Measurement]:
		return getattr(self, '_numerator', None)

	@property
	def denominator(self) -> Type[Measurement]:
		return getattr(self, '_denominator', None)

	@property
	def numeratorClass(self) -> Type[Measurement]:
		return getattr(self, '_numerator', None)

	@numeratorClass.setter
	def numeratorClass(self, value: Type[Measurement]):
		self._numerator = value

	@property
	def denominatorClass(self) -> Type[Measurement]:
		return getattr(self, '_denominator', None)

	@denominatorClass.setter
	def denominatorClass(self, value: Type[Measurement]):
		self._denominator = value

	@property
	def pluralName(self) -> Optional[str]:
		if not self.numerator.isGeneric:
			return None
		return f'{self.numerator.pluralName}/{self.denominator.name}'

	@property
	def pluralUnit(self) -> Optional[str]:
		if not self.numerator.isGeneric:
			return None
		return f'{self.numerator.pluralUnit}/{self.denominator.unit}'

	@property
	def unitArray(mcs):
		return [mcs.numerator.unit, mcs.denominator.unit]

	@property
	def Generic(self) -> Type:
		genericBases = self.genericBases
		genericBases = sorted(
			(
				base for base in genericBases
				if base is not self
				   and issubclass(base, DerivedMeasurement)
				   and base.numerator.isGeneric
				   and base.denominator.isGeneric),
			key=lambda base: self.__mro__.index(base)
		)
		return next(iter(genericBases), None)

	@property
	def genericBases(self):
		return super().genericBases | self.numerator.genericBases | self.denominator.genericBases

	@property
	def compatibleUnits(cls) -> dict:
		parentCls = cls.type
		n = parentCls.numerator.type.compatibleUnits
		d = parentCls.denominator.type.compatibleUnits
		specifiedUnits = {u: t for t in parentCls.subTypes if (u := getattr(t, '_unit', None))}
		return {**specifiedUnits, **n, **d}

	# @property
	# def subTypes(cls):
	# 	subs = super().subTypes
	# 	fixed = cls.fixedUnits
	# 	if fixed[0] is None:
	# 		subs |= cls.numerator.subTypes
	# 	else:
	# 		subs |= {cls.numerator}
	# 	if fixed[1] is None:
	# 		subs |= cls.denominator.subTypes
	# 	else:
	# 		subs |= {cls.denominator}
	# 	return subs

	@property
	def unit(cls):
		clsUnit = getattr(cls, '_unit', None)
		if clsUnit:
			return clsUnit
		numUnit = cls.numerator.unit or f'({cls.numerator.__name__})'
		denUnit = cls.denominator.unit or f'({cls.denominator.__name__})'
		return f'{numUnit}/{denUnit}'

	def __parse_unit__(self, unit: str | None):
		if unit is None:
			return None
		units = re.sub(r'((?<=[A-Z_\-\s])(per)(?=[A-Z_\-\s]))|\\', '/', unit).split('/')
		return tuple(i.strip(' ') for i in units)

	@property
	def id(cls):
		clsID = getattr(cls, '_id', None)
		if clsID:
			return clsID
		clsUnit = getattr(cls, '_unit', None)
		if clsUnit:
			return clsUnit

		numUnit = cls.numerator.id or f'{cls.numerator.__name__}'
		denUnit = cls.denominator.id or f'{cls.denominator.__name__}'
		return f'{cls.__name__}({numUnit}/{denUnit})'

	@property
	def type(cls):
		if (t := getattr(cls, '_type', None)) is not None:
			return t
		bases = cls.genericBases
		n = {i for i in bases if (j := getattr(i, 'numerator', None)) is not None and j.isGeneric}
		d = {i for i in bases if (j := getattr(i, 'denominator', None)) is not None and j.isGeneric}
		_both = n | d
		return sorted(_both, key=lambda i: cls.mro().index(i))[0]

	@property
	@lru_cache(maxsize=512)
	def __unitDict__(self) -> ChainMap:
		return ChainMap(self.numerator.__unitDict__, self.denominator.__unitDict__)


metric: Final = 'metric'
imperial: Final = 'imperial'
both: Final = 'mixed'
systemName: Final = Literal['metric', 'imperial', 'mixed']


class Dimension(MetaUnitClass):
	__systems__: Dict[str, Type['Dimension']] = {metric: {}, imperial: {}, both: ChainMap()}
	_system: systemName
	__dimensions__: Type['Dimension']

	def __new__(mcs, name, bases, attrs, *args, **kwargs):
		system = kwargs.get('system', None)
		if system is not None:
			attrs['_systemName'] = system

		if symbol := kwargs.pop('symbol', None):
			attrs['_symbol'] = symbol

		newCls = super().__new__(mcs, name, bases, attrs, **kwargs)

		if system is not None:
			newCls._system = newCls
		if dimension := getattr(newCls, 'dimension', None):
			dimension.register(newCls)
		else:
			mcs.registerDimension(newCls)

		return newCls

	@classmethod
	def registerDimension(mcs, dimension):
		systems = mcs.__systems__
		dimension.__dimension__ = dimension
		if dimension not in systems[both]:
			dimensionDictMetric, dimensionDictImperial = {}, {}

			dimensionDictBoth = ChainMap(dimensionDictMetric, dimensionDictImperial)

			systems[metric][dimension] = dimensionDictMetric
			systems[metric][dimension.__name__] = dimensionDictImperial

			systems[imperial][dimension] = dimensionDictImperial
			systems[imperial][dimension.__name__] = dimensionDictImperial

			systems[both][dimension] = dimensionDictBoth
			systems[both][dimension.__name__] = dimensionDictBoth

	@classmethod
	def register(mcs, newCls):
		systems = mcs.__systems__

		dimension = newCls.dimension or newCls

		unit = newCls.unit
		if unit:
			if newCls.systemName is both:
				systems[imperial][dimension][unit] = newCls
				systems[metric][dimension][unit] = newCls
			else:
				systems[newCls.systemName][dimension][unit] = newCls
		else:
			newCls._unitSystem = newCls
			newCls._systemID = f'{newCls.__dimension__.__name__}[{newCls._systemName.title()}]'
		# newCls.__name__ = newCls.systemName

	@property
	def isGeneric(cls) -> bool:
		return cls is cls.__dimension__ or (cls is cls._system and bool(cls.__subclasses__()))

	@property
	def systemName(self) -> metric or imperial:
		return getattr(self, '_systemName', None)

	@property
	def system(self) -> str:
		return getattr(self, '_system', None)

	@property
	def systems(self):
		if self.systemName is None:
			return self.__systems__
		return self.__systems__[self.systemName]


class DerivedMeasurement(Measurement, metaclass=DerivedMeasurementMeta):
	_derived = True
	_type: Type[Measurement] = Measurement
	_numerator: Union[Measurement, Type[Measurement]] = Measurement
	_denominator: Union[Measurement, Type[Measurement]] = Measurement

	def __new__(cls, numerator: Measurement, denominator: Measurement = None, *args, **kwargs):
		if denominator is None:
			if (d := getattr(numerator, 'denominator', None)) is not None:
				denominator = d
				numerator = numerator.numerator
			else:
				denominator = 1
		if not cls.numerator.isGeneric:
			numerator = cls.numerator(numerator)
		if not cls.denominatorClass.isGeneric:
			denominator = cls.denominator(denominator)
		value = float(numerator)/float(denominator)

		if isinstance(numerator, cls.numeratorClass) and isinstance(denominator, cls.denominatorClass):
			if cls.isGeneric:
				cls = cls[type(numerator):type(denominator)]
		elif items := [i for i in cls.type.subTypes if i.denominator is type(denominator)]:
			if len(items) == 1:
				cls = items[0]
			else:
				items = [i for i in items if i.numerator is type(numerator)]
				if len(items) == 1:
					cls = items[0]
				else:
					raise TypeError(f'{cls.__name__} does not support {numerator.__class__.__name__} as numerator')
		elif cls.isGeneric:
			cls = cls[type(numerator):type(denominator)]
		return Measurement.__new__(cls, value, *args, **kwargs)

	def __class_getitem__(cls, item):
		# By default, this method respects fixed units
		# To get a class regardless of fixed units, use cls.getClass(item)
		if isinstance(item, str):
			item = cls.__parse_unit__(item)
		if isinstance(item, tuple):
			item = tuple(cls.type.__findUnitClass__(i) if isinstance(i, str) else i for i in item)
		return cls.__getSlice__(HashSlice(item))

	@classmethod
	def getClass(cls, units):
		if isinstance(units, str):
			units = units,
		clsType = cls.type
		units = tuple(clsType.__findUnitClass__(i) for i in units)
		n = next((i for i in units if cls.numerator.dimension is not None and issubclass(i, cls.numerator.dimension)), None) or cls.numeratorClass
		d = next((i for i in units if cls.denominator.dimension is not None and issubclass(i, cls.denominator.dimension)), None) or cls.denominatorClass
		return cls[n:d:True]

	@classmethod
	@lru_cache(maxsize=32)
	def __getSlice__(cls, item: HashSlice, ignoreFixed=False):
		if isinstance(getattr(item, 'step', None), bool):
			ignoreFixed = item.step
		fixedN, fixedD = cls.fixedUnits if not ignoreFixed else (None, None)
		if item in cls.__dict__:
			return cls.__dict__[item]
		if isinstance(item, HashSlice):
			sliceNType, sliceDType = fixedN or item.start, fixedD or item.stop
			nType, dType = cls.numerator, cls.denominator
			if isinstance(sliceNType, str):
				sliceNType = nType.__findUnitClass__(sliceNType)
			if isinstance(sliceDType, str):
				sliceDType = dType.__findUnitClass__(sliceDType)
			if sliceNType is not None and not isinstance(sliceNType, type):
				sliceNType = type(sliceNType)
			elif sliceNType is None:
				sliceNType = nType

			if sliceDType is not None and not isinstance(sliceDType, type):
				sliceDType = type(sliceDType)
			elif sliceDType is None:
				sliceDType = dType

			genericType = cls if cls.isGeneric else cls.type
			if ignoreFixed and any(i is not None for i in genericType.fixedUnits):
				genericType = cls.Generic
			subTypes = genericType.subTypes
			sameDType = {i for i in subTypes if i.denominator is sliceDType}
			sameNType = {i for i in subTypes if i.numerator is sliceNType}

			if exactMatch := sameDType & sameNType:
				matchedType = exactMatch.pop()
				if not issubclass(matchedType._type, genericType) and issubclass(cls._type, matchedType._type):
					return type(f'{cls._type.__name__}[{matchedType.unit}]', (matchedType, cls._type), {})

			if sameDType and (generics := {i for i in sameDType if i.numeratorClass.isGeneric}):
				if len(generics) == 1:
					generic = generics.pop()
					if not dType.isGeneric:
						return generic[sliceNType or nType]
					if generic.denominatorClass is sliceDType:
						return generic[sliceNType or nType]
			if sameNType and (generics := {i for i in sameNType if i.denominatorClass.isGeneric}):
				if len(generics) == 1:
					generic = generics.pop()
					if not nType.isGeneric:
						return generic[sliceDType or dType]
					if generic.numeratorClass is sliceNType:
						return generic[sliceDType or dType]

			name = f'{genericType.__name__}[{sliceNType.id or sliceNType.__name__}/{sliceDType.id or sliceDType.__name__}]'
			return type(name, (genericType,), {}, numerator=sliceNType, denominator=sliceDType)
		item = item.start
		if issubclass(item, cls.numerator):
			if not cls.denominator.isGeneric:
				name = f'{cls.__name__}'
				newCls = type(name, (cls,), {'_numerator': item})
				return newCls
			print(f'{cls.__name__} does not support {item.__name__} as numerator')

		elif issubclass(item, cls.denominator):
			if not cls.numeratorClass.isGeneric:
				name = f'{cls.__name__}[{item.__name__}]'
				newCls = type(name, (cls,), {'_denominator': item})
				return newCls
			print(f'{cls.__name__} does not support {item.__name__} as denominator')

		raise TypeError(f'{cls.__name__} does not support {item.__name__} as unit')

	def __init__(self, numerator, denominator=None, *args, **kwargs):
		if isinstance(numerator, DerivedMeasurement) and denominator is None:
			self._numerator = numerator.numerator
			self._denominator = numerator.denominator
		elif denominator is None:
			self._numerator = numerator
			self._denominator = self.denominator(1)
		else:
			self._numerator = numerator
			self._denominator = denominator
		if not isinstance(self.numerator, type(self).numerator):
			self._numerator = type(self).numerator(self._numerator)
		if not isinstance(self.denominator, type(self).denominator):
			self._denominator = type(self).denominator(self._denominator)
		Measurement.__init__(self, float(self._numerator)/float(self._denominator), *args, **kwargs)

	def __pow__(self, power, modulo=None):
		return self.__class__(super(Measurement, self).__pow__(power, modulo), self._denominator)

	def __getitem__(self, item):
		if isinstance(item, str):
			item = type(self).__parse_unit__(item)
			if len(item) == 2:
				item = HashSlice(*item, True)
			elif len(item) == 1:
				item = item[0]
				cls = self.type.__findUnitClass__(item)
				if issubclass(cls, self.type):
					return cls(self.numerator, self.denominator)
				if issubclass(cls, self.numerator.type):
					cls = type(self)[cls: type(self.denominator): True]
				else:
					cls = type(self)[type(self.numerator): cls: True]
				return cls(self.numerator, self.denominator)
		if hasattr(item, 'denominator'):
			item = HashSlice(item.numerator, item.denominator, True)

		if isinstance(item, (slice, HashSlice)):
			newCls = self.type[item]
			if newCls is not type(self):
				return newCls(self.numerator, self.denominator)
			numerator = item.start or self._numerator
			denominator = item.stop or self._denominator

			if isinstance(numerator, str):
				numeratorCls = self.type.__findUnitClass__(numerator)
			else:
				numeratorCls = type(self).numerator

			if isinstance(denominator, str):
				denomDict = self._denominator.__unitDict__
				denominatorCls = denomDict.get(denominator, None) or {
					v.__name__.lower(): v for k, v in denomDict.items()
					if v.__name__.lower() == denominator.lower()
				}.get(denominator, None) or type(self).denominator
			else:
				denominatorCls = type(self).denominator

			return self.__class__[numeratorCls, denominatorCls, True](self._numerator, self._denominator)
		return self.__class__(self._numerator[item], self._denominator)

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
		return config['LocalUnits'][str(self._type)].split('/')

	def _getUnitTypes(self):
		return self._numerator.type, self._denominator.type

	@property
	def type(self) -> Type[Measurement]:
		return type(self).type

	@property
	def localize(self):
		try:
			units = type(self).localizedUnit
			if len(units) == 1:
				unit = units[0]
				if issubclass(unit, self.type):
					return unit(self.numerator, self.denominator)
				if issubclass(unit.type, self.n.type):
					n, d = unit, None
				elif issubclass(unit.type, self.d.type):
					n, d = None, unit
				else:
					n, d = self.n, self.d
			else:
				n, d = units
			t = self.type[n:d:True]
			return t(self.n, self.d)
		except KeyError:
			log.error('Measurement {} was unable to localize from {}'.format(self.name, self.unit))
			return self

	@property
	def unit(self):
		return getattr(self, '_unit', '') or f'{self.numerator.unit}/{self.denominator.unit}'

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
