# from enum import Enum as _Enum, EnumMeta as _Meta
# from types import DynamicClassAttribute
#
# from src.WeatherUnits import Measurement
#
#
# class Enum(_Enum):
#
# 	# @DynamicClassAttribute
# 	# def cls(self):
# 	# 	"""The name of the Enum member."""
# 	# 	return type(self._name_, (Measurement,), {'name': 'dog'})
#
# 	def __init__(self, *args):
# 		self._class_ = type(self._name_, (Measurement,), {'name': 'dog'})
# 		return super(Enum, self).__init__()
#
#
# class AddressableEnum(_Meta):
#
# 	def __new__(mcs, cls, bases, classdict):
# 		return super().__new__(mcs, cls, bases, classdict)
#
# 	def __getitem__(self, indexOrName):
# 		if isinstance(indexOrName, str):
# 			return super().__getitem__(indexOrName)
# 		elif isinstance(indexOrName, int) and indexOrName < super().__len__():
# 			return self._list[indexOrName]
# 		elif isinstance(indexOrName, slice):
# 			indices = range(*indexOrName.indices(len(self._list)))
# 			return [self._list[i] for i in indices]
#
# 	@property
# 	def _list(self):
# 		return list(self)
#
# 	def __getattr__(cls, name):
#
# 		if _Meta._is_dunder(name):
# 			raise AttributeError(name)
# 		try:
# 			return cls._member_map_[name]._class_
# 		except KeyError:
# 			raise AttributeError(name) from None
#
#
# class Indexer:
# 	i = 0
# 	lastClass: object = None
#
# 	@classmethod
# 	def get(cls, caller):
# 		cls.i, cls.lastClass = (0, caller) if not caller == cls.lastClass else (cls.i + 1, caller)
# 		return cls.i
#
#
# class ScaleMeta(Enum, metaclass=AddressableEnum):
#
# 	def __new__(cls, *args):
# 		obj = object.__new__(cls)
# 		obj._value_ = Indexer.get(cls)
# 		# obj._class_ = type(obj.name, (Measurement,), {'_unit': args[1]})
# 		obj._mul_ = args[0]
#
# 		return obj
#
# 	def __str__(self):
# 		return str(self.value)
#
# 	# this makes sure that the description is read-only
# 	@property
# 	def index(self):
# 		return self._value_
#
# 	@property
# 	def value(self):
# 		return self._mul_
#
# 	def __repr__(self):
# 		return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, self._mul_)
#
# 	def __mul__(self, other):
# 		if isinstance(other, self.__class__):
# 			val = 1
# 			array = self.__class__[min(self.index, other.index) + 1: max(self.index, other.index) + 1]
# 			array.sort(key=lambda x: x.index)
# 			for i in array:
# 				val *= i.value
# 			return val
#
# 	def __gt__(self, other):
# 		if isinstance(other, self.__class__):
# 			return self.index > other.index
#
# 	def __lt__(self, other):
# 		if isinstance(other, self.__class__):
# 			return self.index < other.index
#
#
# class test(type):
#
# 	def __new__(mcl, name: str, bases, classdict):
# 		cls = type(name, (object,), {'name': 'dog'})
# 		for name, value in classdict.items():
# 			if not name.startswith('_'):
# 				print(name, value)
# 				setattr(cls, name, type(name, (Measurement,), {'_mul_': value[0], '_unit': value[1]}))
#
# 		return cls
#
#
# class Scale(metaclass=test):
# 	Dram: Measurement = 1, 'dr'
# 	Ounce = 16, 'oz'
# 	Pound = 16, 'lbs'
# 	Hundredweight = 100, 'hw'
# 	Ton = 20, 't'
# import src.WeatherUnits
# from src.WeatherUnits import *
#
# f: src.WeatherUnits.DerivedMeasurement = length.Meter(1) / time.Second(1) / time.Second(1)


# class Meter(UnitMeta):
# 	pass
#
#
# class Time(UnitMeta):
# 	pass
#
#
# m = Meter('m')
# t = Time('s')
#
# print(m * t / t / t)

# def unitS(unit):
# 	return 0
#
#
# if len(f.n.unit) > 1:
# 	print(f.unit)
# 	print(f.n.unit)

from src.WeatherUnits import time, length, temperature, pressure

# from src.WeatherUnits.measurement import Compound


x = pressure.pascal.Pascal(21500)
y = pressure.pascal.Hectopascals(x)
z = pressure.pascal.mmHg(y)

d = time.Day(657)
w = time.Week(d)
m = time.Month(d)
print(d.auto)

# c = 0
# v = 1000 * 100000
# print(v)
# while len(str(v)) >= :
# 	c += 1
# 	v //= 1000
# print(v, c)
