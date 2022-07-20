from typing import Type, overload, Tuple

from .config import config

from . import base

SmartFloat = base.SmartFloat
Measurement = base.Measurement
ScalingMeasurement = base.ScalingMeasurement
Dimension = base.Dimension
Dimensionless = base.Dimensionless
NonPlural = base.NonPlural
DerivedMeasurement = base.DerivedMeasurement
Index = base.Index
Quantity = base.Quantity
SystemVariant = base.SystemVariant
FiniteField = base.FiniteField

from .others import (Light, Angle, Percentage, Voltage,
                     LightningStrike, Humidity, Direction,
                     Coverage, Probability)
from .temperature import Temperature
from .length import Length
from .mass import Mass
from .time_ import Time
from .pressure import Pressure
from . import airQuality as AirQuality
from . import digital as Digital
from . import derived

Rate = derived.DistanceOverTime
Wind = derived.Wind
Precipitation = derived.Precipitation
Other = others
Light = others.Light
PartsPer = derived.PartsPer
Volume = derived.Volume
Density = derived.Density
PartsPer = derived.PartsPer


@overload
def auto(value: int | float | int, unit: str) -> Measurement: ...


@overload
def auto(value: str) -> Measurement: ...


@overload
def auto(unit: str) -> Type[Measurement] | Tuple[Type[Measurement], ...]: ...


def auto(*args) -> Measurement | Type[Measurement] | Tuple[Type[Measurement], ...]:
	match args:
		case [int(value) | float(value) | str(value), str(unit)]:
			measurement = float(value)
			unit = Measurement.__findUnitClass__(unit)
			cls = tuple(Measurement.__findUnitClass__(u) for u in unit)

			if len(cls) == 1:
				return cls[0](measurement)
			raise NotImplementedError('Multi-Unit values are not supported yet')

		case [str(value)]:
			number = base.FormatSpec.number.search(value)
			if number is not None:
				number = number.groupdict()['number']

			unit = DerivedMeasurement.__parse_unit__(value.replace(number, ''))
			cls = tuple(Measurement.__findUnitClass__(u) for u in unit)

			if len(cls) == 1:
				if number != '':
					return cls[0](float(number))
				return cls[0]
			raise NotImplementedError('Multi-Unit values are not supported yet')

		case [str(unit)]:
			unit = DerivedMeasurement.__parse_unit__(unit)
			cls = tuple(Measurement.__findUnitClass__(u) for u in unit)
			return cls
		case _:
			raise ValueError


__all__ = ['auto', 'Measurement', 'Temperature', 'Length', 'Mass', 'Time', 'Pressure', 'Other', 'Light', 'PartsPer',
	'Volume', 'Density', 'PartsPer', 'Rate', 'Wind', 'Precipitation', 'AirQuality', 'Voltage', 'Digital', 'config',
	'Precipitation', 'LightningStrike', 'Angle', 'Percentage', 'Humidity', 'Direction', 'Coverage', 'Probability']
