from ...others import UVI, Direction, Lux, RadiantFlux, Voltage, Strikes, Humidity
from ...time import *
from ...pressure import mmHg
from ...derived import Wind, Precipitation, PrecipitationDaily, PrecipitationHourly, PrecipitationMinutely
from ...temperature import Celsius
from ...length import Kilometer, Meter, Millimeter
from enum import Enum as _Enum


class PrecipitationType(_Enum):
	NONE = 0
	RAIN = 1
	HAIL = 2
