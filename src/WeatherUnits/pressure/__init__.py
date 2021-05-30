from ._pressure import Pressure
from ._metric import *
from ._imperial import *

from enum import Enum as _Enum


class PressureTrend(_Enum):
	Falling = -1
	Steady = 0
	Rising = 1
