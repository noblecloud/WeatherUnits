from .pressure import *
from enum import Enum as _Enum


class PressureTrend(_Enum):
	Falling = -1
	Steady = 0
	Rising = 1
