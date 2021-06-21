from ..base import NamedType
from ..base import Measurement
from . import light
Light = light.Light

__all__ = ['Light', 'Direction', 'Humidity', 'Voltage', 'Strikes']


@NamedType
class Humidity(Measurement):
	_unit = ''
	_decorator = '%'


@NamedType
class Direction(Measurement):
	_precision = 0
	_decorator = 'º'
	_cardinal = True
	_degrees = False

	def __init__(self, *args, **kwargs):
		super(Direction, self).__init__(*args, **kwargs)

	def _string(self, **kwargs) -> str:
		if self._cardinal and self._degrees:
			return f'{self.cardinal} ({super()._string(**kwargs)})'
		if self._cardinal:
			return f'{self.cardinal}'
		else:
			return f'{super()._string(**kwargs)}'

	@property
	def cardinal(self):
		dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
		ix = round(self / (360. / len(dirs)))
		return dirs[ix % len(dirs)]

	@property
	def decorator(self):
		return self._decorator if not self._cardinal else ''


@NamedType
class Voltage(Measurement):
	_max = 3
	_precision = 2
	_unit = 'v'


@NamedType
class Strikes(Measurement):
	# TODO: Create discrete number class for this and similar measurements
	unit = 'strikes'
