from abc import abstractmethod
from enum import Enum, EnumMeta
from itertools import groupby
from typing import Optional, Type, Tuple, Set, Dict

from .. import errors
from . import Measurement, DerivedMeasurement, MetaUnitClass

__all__ = ['ScalingMeasurement', 'SystemVariant', 'Scale']


class AddressableEnum(EnumMeta):

	def __getitem__(self, indexOrName):
		if isinstance(indexOrName, str):
			return super().__getitem__(indexOrName)
		elif isinstance(indexOrName, int) and indexOrName < super().__len__():
			return self._list[indexOrName]
		elif isinstance(indexOrName, slice):
			indices = range(*indexOrName.indices(len(self._list)))
			return [self._list[i] for i in indices]

	@property
	def _list(self):
		return list(self)


class Indexer:
	# Todo: this could probably be moved inside or declared as a class variable of Scale

	i = 0
	lastClass: object = None

	@classmethod
	def get(cls, caller):
		cls.i, cls.lastClass = (0, caller) if not caller == cls.lastClass else (cls.i + 1, caller)
		return cls.i


class Scale(Enum, metaclass=AddressableEnum):

	Base: 'Scale'

	def __new__(cls, *args):
		if isinstance(args[0], int):
			obj = object.__new__(cls)
			obj._value_ = Indexer.get(cls)
			obj._mul_ = args[0]
			obj.isVariant = False
		elif isinstance(args[0], float):
			obj = object.__new__(cls)
			obj._value_ = Indexer.get(cls)
			obj._mul_ = args[0]
			obj.isVariant = True
		elif isinstance(args[0], str):
			obj = object.__new__(cls)
			obj._value_ = getattr(cls, args[0]).index
			obj._mul_ = getattr(cls, args[0]).value
			obj.isVariant = False
		else:
			obj = None

		return obj

	def __str__(self):
		return str(self.value)

	# this makes sure that the description is read-only
	@property
	def index(self):
		if self.isVariant:
			return self.Base.index + 1
		return self._value_

	@property
	def value(self):
		return self._mul_

	def __repr__(self):
		return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, self._mul_)

	def __mul__(self, other):
		if isinstance(other, self.__class__):
			variant = self.isVariant or other.isVariant
			val = 1
			array = self.__class__[min(self.index, other.index) + 1: max(self.index, other.index) + 1]
			array.sort(key=lambda x: x.index)
			array = array[:-1] if variant else array
			for i in array:
				val *= i.value
			if variant:
				val *= self.value if self.isVariant else other.value
			return val

	def __gt__(self, other):
		if isinstance(other, self.__class__):
			return self.index > other.index
		else:
			return self.index > int(other)

	def __lt__(self, other):
		if isinstance(other, self.__class__):
			return self.index < other.index
		else:
			return self.index < int(other)

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.index == other.index
		else:
			return self.index == int(other)

	def __le__(self, other):
		if isinstance(other, self.__class__):
			return self.index <= other.index
		else:
			return self.index <= int(other)

	def __ge__(self, other):
		if isinstance(other, self.__class__):
			return self.index >= other.index
		else:
			return self.index >= int(other)

	def __hash__(self):
		return hash((self.index, self.value))


class BaseUnit:

	@abstractmethod
	def changeSystem(self, system):
		pass


class ScalingMeasurement(Measurement):
	_baseUnit: Type[Measurement]
	_Scale: Scale = None

	common: Set[_Scale] = set()

	def __init_subclass__(cls, **kwargs):
		baseUnit = kwargs.get('baseUnit', None)
		if baseUnit:
			cls._baseUnitRef = baseUnit
			cls._system = cls
			cls._systemName = kwargs.get('system', 'mixed')
		else:
			baseUnitRef = getattr(cls, '_baseUnitRef', None)
			if baseUnitRef == cls.__name__:
				cls._system._baseUnit = cls
		super().__init_subclass__(**kwargs)

	def __new__(cls, value, *args, **kwargs):
		if isinstance(value, DerivedMeasurement):
			return value
		valueCls = type(value)

		if not issubclass(valueCls, Measurement) and issubclass(valueCls, (float, int)):
			value = float(value)
			return super().__new__(cls, value, *args, **kwargs)

		if isinstance(value, ScalingMeasurement) and (not cls._baseUnit or not value.__class__._baseUnit):
			'''For this to work each unit class must have a _baseUnit defined for each scale'''
			raise errors.Unit.NoBaseUnitDefined(cls)

		sameDimension = cls.dimension is valueCls.dimension
		sameSystem = cls.system is valueCls.system
		sameUnit = cls.unit is valueCls.unit

		if sameUnit and issubclass(valueCls, cls.type):
			return Measurement.__new__(cls, float(value), *args, **kwargs)

		if sameSystem and sameDimension:
			if isinstance(value, ScalingMeasurement) and not isinstance(value, value._baseUnit):
				value = cls.changeScale(value, cls._Scale.Base)
			if cls is cls._baseUnit:
				return cls.__new__(cls, value)
			else:
				value = cls._baseUnit.changeScale(value, cls._Scale[cls.__name__], cls._Scale.Base)
			return cls.__new__(cls, value)

		# If values are cousins initiate with values base sibling causing a recursive call to __new__
		elif sameDimension:
			if not isinstance(value, value._baseUnit):
				value = value.toBaseUnit()
			if (converter := getattr(value, f'_{cls._baseUnitRef.lower()}', None)) is not None:
				value = cls._baseUnit(converter())
			return cls.__new__(cls, value)

		raise errors.Conversion.BadConversion(cls.__name__, value.__class__.__name__)

	@property
	def up(self) -> 'ScalingMeasurement':
		value = self.changeScale(self.nextScale)
		return getattr(self.type, self.nextScale.name)(value)

	@property
	def down(self) -> 'ScalingMeasurement':
		value = self.changeScale(self.previousScale)
		return getattr(self.type, self.previousScale.name)(value)

	@property
	def downCommon(self) -> 'ScalingMeasurement':
		down = self.down
		while type(down) not in self.common:
			down = down.down
			if down.down.scale == down.scale:
				break
		return down

	@property
	def upCommon(self) -> 'ScalingMeasurement':
		up = self.up
		while up.scale not in self.common or up.scale == self.scale:
			up = up.up
		return up

	@property
	def nextScale(self) -> _Scale:
		return type(self)._Scale[min(self.scale.index + 1, max(type(self)._Scale).index)]

	@property
	def previousScale(self) -> _Scale:
		return type(self)._Scale(max(self.scale.index - 1, min(type(self)._Scale).index))

	@property
	def remainder(self) -> 'ScalingMeasurement':
		return sum(i for i in self.splitIntoDict() if i.scale < self.scale)

	@property
	def remainderInt(self) -> int:
		return int(self.remainder)

	@property
	def only(self) -> 'ScalingMeasurement':
		return self.splitIntoDict().get(self.name, None) or type(self)(0)

	@property
	def onlyInt(self) -> int:
		return int(self.only)

	def splitInto(self, *into: Type['ScalingMeasurement']) -> Tuple['ScalingMeasurement', ...]:
		into = into or type(self).common or self.type.subTypes
		into = sorted(into, key=lambda x: x(self).int)
		if self.down == type(self)(0):
			return self,
		top = into.pop(0)(self).typedInt
		values = [top]
		while into:
			nextVal = into.pop(0)(self)
			if into:
				nextVal = nextVal.typedInt
			nextVal = nextVal - top
			top = nextVal + top
			if abs(nextVal) < type(nextVal)(1):
				values[-1] += nextVal
			else:
				if values[-1] == 0:
					values[-1] = nextVal
				else:
					values.append(nextVal)
		return tuple(values)

	def splitIntoDict(self, *into: Type['ScalingMeasurement']) -> Dict[str, 'ScalingMeasurement']:
		values = self.splitInto(*into)
		return {type(i).name: i for i in values}


	def changeScale(self, newUnit: Scale, scale: Scale = None) -> Optional[float]:
		scale = getattr(self, 'scale', scale)
		multiplier = scale*newUnit
		if scale > newUnit:
			return float(self)*multiplier
		else:
			return float(self)/multiplier

	def toBaseUnit(self) -> Measurement:
		return self._baseUnit(self.changeScale(self._Scale.Base))

	@classmethod
	@property
	def scale(cls) -> _Scale:
		return cls._Scale[cls.__name__]

	@classmethod
	@property
	def Scale(cls) -> _Scale:
		return cls._Scale

	@property
	def isSystemVariant(self):
		return issubclass(self.__class__, SystemVariant)


class SystemVariant:
	_multiplier: float = 1.0
