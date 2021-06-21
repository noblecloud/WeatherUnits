from typing import Optional, Union

from .. import errors
from .. import utils as _utils
from .Measurement import Measurement


class MeasurementSystem(Measurement):
	_baseUnit = None
	_unitSystem: type = None
	_Scale: _utils.ScaleMeta = None

	def __new__(cls, value):
		value: Union[int, float, MeasurementSystem, SystemVariant]
		if isinstance(value, MeasurementSystem) and (not cls._baseUnit or not value.__class__._baseUnit):
			'''For this to work each unit class must have a _baseUnit defined for each scale'''
			raise errors.Unit.NoBaseUnitDefined(cls)
		system = issubclass(cls, MeasurementSystem) and issubclass(value.__class__, MeasurementSystem)
		siblings, cousins = [cls._baseUnit == value._baseUnit, cls._type == value._type] if system else (False, False)
		variant = issubclass(cls, SystemVariant) and issubclass(value.__class__, SystemVariant)

		# If values are siblings change to sibling class with changeScale()
		if siblings:
			# If both are variants convert value to baseUnit first
			value = value._baseUnit(value) if variant else value
			return cls(value.__class__.changeScale(value, cls._Scale[cls.__name__]))

		# If values are cousins initiate with values base sibling causing a recursive call to __new__
		elif cousins:
			return cls.__new__(cls, cls._baseUnit(value.__getattribute__('_' + cls._baseUnit.__name__.lower())()))

		elif isinstance(value, Measurement):
			raise errors.Conversion.BadConversion(cls.__name__, value.__class__.__name__)

		else:
			return Measurement.__new__(cls, value)

	def changeScale(self, newUnit: _utils.ScaleMeta) -> Optional[float]:
		if self._Scale:
			multiplier = self.scale * newUnit
			if self.scale > newUnit:
				return float(self) * multiplier
			else:
				return float(self) / multiplier
		else:
			return None

	@property
	def scale(self):
		return self._Scale[self.name]

	@property
	def unitSystem(self):
		return self._unitSystem.__name__

	@property
	def isSystemVariant(self):
		return issubclass(self.__class__, SystemVariant)


class SystemVariant:
	_multiplier: float = 1.0
