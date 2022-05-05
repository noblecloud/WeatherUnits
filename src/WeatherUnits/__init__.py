from datetime import timedelta
from typing import Any, Dict, Iterable, List, SupportsIndex, Type, Union

UnitSystems: Dict[str, Dict[str, Type]] = {}

from . import errors
from .config import config
from . import utils
from . import base
from . import temperature
from . import length
from . import mass
from . import time
from . import pressure
from .airQuality import *
from .derived import *
from .others import *
from .various import *

Temperature = temperature.Temperature
Length = length.Length
Mass = mass.Mass
Time = time.Time
Pressure = pressure.Pressure


class Trend(List[Measurement]):

	def __init__(self, value: Union[Measurement, List[Measurement], Type[Measurement]] = None, max: Union[int, Time, timedelta] = None):
		if isinstance(value, Measurement):
			value = [value]
		if isinstance(value, list):
			pass
		elif isinstance(value, type):
			value = [value(0)]
		metadata = value[0]
		self.title = metadata.title
		self.key = metadata.key
		self.category = metadata.category
		self._valueClass = type(metadata)
		self.max = max
		self.insertValue(value)
		super(Trend, self).__init__()

	def insertValue(self, value: Any):
		if isinstance(value, self._valueClass):
			self.append(value)
		elif isinstance(value, Iterable):
			for v in value:
				self.insertValue(v)
		else:
			raise TypeError("Value must be a list of Measurement or a Measurement")
		while self.listIsTooLong():
			self.pop(0)

	def listIsTooLong(self):
		if isinstance(self.max, int):
			return len(self) > self.max
		elif isinstance(self.max, Time):
			max = timedelta(seconds=self.max.seconds)
		start = self[0].timestamp
		end = self[-1].timestamp
		return end - start > self.max
