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
