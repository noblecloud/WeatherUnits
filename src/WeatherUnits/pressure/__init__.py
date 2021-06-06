from .pressure import Pressure
from .metric import *
from .imperial import *
from enum import Enum as _Enum


class PressureTrend(_Enum):
	Falling = -1
	Steady = 0
	Rising = 1
