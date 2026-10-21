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
from .area import Area
from .energy import Energy, Power
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


def auto(*args, dimension: Type[Dimension | Dimensionless] = None) -> Measurement | Type[Measurement] | Tuple[Type[Measurement], ...]:
	dimension = dimension or Measurement
	match args:
		case [int(value) | float(value) | str(value), str(unit)]:
			measurement = float(value)
			unit = dimension.__findUnitClass__(unit)
			cls = tuple(dimension.__findUnitClass__(u) for u in unit)

			if len(cls) == 1:
				return cls[0](measurement)
			raise NotImplementedError('Multi-Unit values are not supported yet')

		case [str(value)]:
			number = base.FormatSpec.number.search(value)
			if number is not None:
				number = number.groupdict()['number']

			unit = DerivedMeasurement.__parse_unit__(value.replace(number, ''))
			cls = tuple(dimension.__findUnitClass__(u) for u in unit)

			if len(cls) == 1:
				if number != '':
					return cls[0](float(number))
				return cls[0]
			raise NotImplementedError('Multi-Unit values are not supported yet')

		case [str(unit)]:
			unit = DerivedMeasurement.__parse_unit__(unit)
			cls = tuple(dimension.__findUnitClass__(u) for u in unit)
			return cls
		case _:
			raise ValueError


__all__ = ['auto', 'Measurement', 'Temperature', 'Length', 'Mass', 'Time', 'Pressure', 'Area', 'Energy', 'Power', 'Other', 'Light', 'PartsPer',
	'Volume', 'Density', 'PartsPer', 'Rate', 'Wind', 'Precipitation', 'AirQuality', 'Voltage', 'Digital', 'config',
	'Precipitation', 'LightningStrike', 'Angle', 'Percentage', 'Humidity', 'Direction', 'Coverage', 'Probability']


def _registerDimensions():
	from .base import _Algebra
	reg = _Algebra.register
	reg(Length, (1, 0, 0, 0), Length.Meter)
	reg(Mass, (0, 1, 0, 0), Mass.Kilogram)
	reg(Time, (0, 0, 1, 0), Time.Second)
	reg(Temperature, (0, 0, 0, 1), Temperature.Kelvin)
	reg(Pressure, (-1, 1, -2, 0), Pressure.Pascal)
	reg(Temperature.Change, (0, 0, 0, 1))
	reg(Area, (2, 0, 0, 0), Area.SquareMeter)
	reg(Energy, (2, 1, -2, 0), Energy.Joule)
	reg(Power, (2, 1, -3, 0), Power.Watt)
	_Algebra._references[(1, 0, -1, 0)] = derived.DistanceOverTime.MetersPerSecond


_registerDimensions()
