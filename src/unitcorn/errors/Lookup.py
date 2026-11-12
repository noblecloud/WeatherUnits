"""The two ways a strict unit lookup can fail. See `unitcorn.parse`."""
from typing import Iterable, Optional

__all__ = ['UnknownUnit', 'AmbiguousUnit']


def _describe(unit) -> str:
	"""A unit class as `Meter ('m')`, for a message."""
	symbol = getattr(unit, 'unit', None)
	name = getattr(unit, 'name', None) or getattr(unit, '__name__', str(unit))
	return f'{name} ({symbol!r})' if symbol else str(name)


class UnknownUnit(ValueError, LookupError):
	"""No unit matches this text.

	`unit` is the text that was looked up. `candidates` are the closest unit
	classes (from `suggest`), best first. They are hints for a person to read:
	nothing here picks one.

	Raised by `unitcorn.lookup` and `unitcorn.parse`, and by `value['text']`
	when the value cannot convert to that unit.
	"""
	unit: str
	candidates: list
	dimension: Optional[type]
	measurement: object

	def __init__(self, unit, candidates: Iterable = (), *, dimension: Optional[type] = None, measurement=None, reason: str = None):
		if isinstance(candidates, str):
			# The original signature was UnknownUnit(measurement, unit)
			measurement, unit, candidates = unit, candidates, ()
		self.unit = unit
		self.candidates = list(candidates)
		self.dimension = dimension
		self.measurement = measurement
		if measurement is not None:
			message = f"{measurement} can not be converted to '{unit}'"
		else:
			scope = f' for {getattr(dimension, "__name__", dimension)}' if dimension is not None else ''
			message = f'Unknown unit {unit!r}{scope}'
			if reason:
				message += f': {reason}'
		if self.candidates:
			message += '. Did you mean ' + ', '.join(_describe(c) for c in self.candidates) + '?'
		self.message = message
		super().__init__(message)


class AmbiguousUnit(ValueError, LookupError):
	"""More than one unit of different dimensions matches this text.

	`unit` is the text that was looked up. `candidates` are the matching unit
	classes. Pass a dimension (`dimension=uc.Time`) to choose between them.
	"""
	unit: str
	candidates: list

	def __init__(self, unit: str, candidates: Iterable = (), *, dimension: Optional[type] = None):
		self.unit = unit
		self.candidates = list(candidates)
		self.dimension = dimension
		self.message = (f'Ambiguous unit {unit!r}: could be '
			+ ', '.join(_describe(c) for c in self.candidates)
			+ '. Pass a dimension to choose, e.g. dimension=unitcorn.Time')
		super().__init__(self.message)
