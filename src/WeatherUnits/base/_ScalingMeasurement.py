from abc import abstractmethod
from enum import Enum, EnumMeta
from itertools import groupby
from math import prod
from typing import Optional, Type, Tuple, Set, Dict

from ._Measurement import systemName
from .. import errors
from . import Measurement, DerivedMeasurement, MetaUnitClass
from ..utils import Self

__all__ = ['ScalingMeasurement', 'SystemVariant', 'Scale']


class AddressableEnum(EnumMeta):
	_list: list['Scale']

	def __new__(cls, *args, **kwargs):
		instance = super().__new__(cls, *args, **kwargs)
		instance._list = [i for i in instance if not i.isVariant]
		instance._sorted = sorted(instance, key=lambda x: x.absoluteValue)
		for i, scale in enumerate(instance._sorted):
			scale._index_ = i
		return instance

	def __getitem__(self, indexOrName):
		if isinstance(indexOrName, str):
			return super().__getitem__(indexOrName)
		elif isinstance(indexOrName, int) and indexOrName < super().__len__():
			return self._list[indexOrName]
		elif isinstance(indexOrName, slice):
			indices = range(*indexOrName.indices(len(self._list)))
			return [self._list[i] for i in indices]



class Indexer:
	# Todo: this could probably be moved inside or declared as a class variable of Scale

	i = 0
	lastClass: object = None

	@classmethod
	def get(cls, caller):
		cls.i, cls.lastClass = (0, caller) if not caller == cls.lastClass else (cls.i + 1, caller)
		return cls.i


class Scale(Enum, metaclass=AddressableEnum):
	_index_: int

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

	def __repr__(self):
		index = self.sortedIndex
		value = self.value
		absoluteValue = self.absoluteValue
		return f"{self.__class__.__name__}({index=:g}, {value=:g}, {absoluteValue=:g})"

	# this makes sure that the description is read-only
	@property
	def index(self):
		if self.isVariant:
			return self.Base.index + 1
		return self._value_

	@property
	def sortedIndex(self) -> int:
		return self._index_

	@property
	def value(self):
		return self._mul_

	@property
	def absoluteValue(self) -> int | float:
		if not self.isVariant:
			return prod(i._mul_ for i in self._list if i.index <= self.index)
		return self._mul_

	def __truediv__(self, other):
		if isinstance(other, self.__class__):
			return self.absoluteValue / other.absoluteValue
		return self.absoluteValue / other

	def __mul__(self, other):
		if isinstance(other, self.__class__):
			return other.absoluteValue * self.absoluteValue
		return self.absoluteValue * other

	def __rmul__(self, other):
		return self.__mul__(other)

	def __rtruediv__(self, other):
		if isinstance(other, self.__class__):
			return other.absoluteValue / self.absoluteValue
		else:
			return other / self.absoluteValue

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
			if (scale := getattr(other, 'scale', None)) is not None and (index := getattr(scale, 'index', None)) is not None:
				return self.index == index
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

	@property
	def up(self) -> 'Scale':
		try:
			return self._sorted[self.sortedIndex + 1]
		except IndexError:
			return self

	@property
	def down(self) -> 'Scale':
		try:
			return self._sorted[self.sortedIndex - 1]
		except IndexError:
			return self


class BaseUnit:

	@abstractmethod
	def changeSystem(self, system):
		pass


class ScalingMeasurement(Measurement):
	_baseUnit: Type['ScalingMeasurement']
	_Scale: Scale | None = None
	_systemName: systemName
	_system: Type['ScalingMeasurement']

	common: Set[Type[_Scale]] = set()

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
		if cls.name in cls.common:
			cls.common.discard(cls.name)
			cls.common.add(cls.scale)
		elif cls in cls.common:
			cls.common.discard(cls)
			cls.common.add(cls.scale)
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
	def up(self: Self) -> Self:
		value = self.changeScale(self.nextScale)
		return getattr(self.type, self.nextScale.name)(value)

	@property
	def down(self: Self) -> Self:
		value = self.changeScale(self.previousScale)
		return getattr(self.type, self.previousScale.name)(value)

	@property
	def downCommon(self: Self) -> Self:
		down = self.down
		while down.scale not in (self.common or self._Scale) and down.scale is not self.scale:
			down_down = down.down
			if down_down.scale is down.scale:
				return down
			down = down_down
		return down

	@property
	def upCommon(self: Self) -> Self:
		up = self.up
		while up.scale not in (self.common or self._Scale) and up.scale is not self.scale:
			up_up = up.up
			if up_up.scale is up.scale:
				return up
			up = up_up
		return up

	@property
	def nextScale(self) -> Scale:
		return self.scale.up

	@property
	def previousScale(self) -> Scale:
		return self.scale.down

	@property
	def remainder(self: Self) -> Self:
		return sum(i for i in self.splitIntoDict() if i.scale < self.scale)

	@property
	def remainderInt(self) -> int:
		return int(self.remainder)

	@property
	def only(self: Self) -> Self:
		return self.splitIntoDict().get(self.name, None) or type(self)(0)

	@property
	def onlyInt(self) -> int:
		return int(self.only)

	def splitInto(self: Self, *into: Type[Self]) -> Tuple[Self, ...]:
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

	def splitIntoDict(self: Self, *into: Type[Self]) -> Dict[str, Self]:
		values = self.splitInto(*into)
		return {type(i).name: i for i in values}

	def changeScale(self, newUnit: Scale, scale: Scale = None) -> Optional[float]:
		scale = getattr(self, 'scale', scale)
		if scale > newUnit:
			return float(self) / (newUnit / scale)
		else:
			return float(self) * (scale / newUnit)

	def toBaseUnit(self) -> Measurement:
		return self._baseUnit(self.changeScale(self._Scale.Base))

	@classmethod
	@property
	def scale(cls) -> Type[Scale]:
		return cls._Scale[cls.__name__]

	@classmethod
	@property
	def Scale(cls) -> Scale:
		return cls._Scale

	@property
	def isSystemVariant(self):
		return issubclass(self.__class__, SystemVariant)

	@property
	def auto(self: Self) -> Self:
		auto = self
		if abs(auto.up) > abs((up := auto.up).one):
			while abs(up.one) < abs(up) != abs(auto):
				auto, up = up, up.up
		else:
			while not auto.int and auto.down != auto:
				auto = auto.down

		return auto

	def bestFit(self, max_digits: int = None) -> Self:
		"""Returns the best fit unit for the value"""
		if max_digits is None:
			max_digits = self.max

		int_digits_count = self.intLength
		value = self

		while int_digits_count > max_digits:
			old, value = value, value.upCommon
			if type(old) is type(value):
				return value
			if (int_digits_count := value.intLength) <= max_digits:
				return value
		return value


class SystemVariant:
	_multiplier: float = 1.0
