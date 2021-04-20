from .._unit import Measurement


class Volts(Measurement):
	_max = 3
	_precision = 2
	_unit = 'v'
	_unitFormat: str = '{decorated}{unit}'


class Direction(Measurement):
	_precision = 0
	_decorator = 'º'

	def __init__(self, *args, **kwargs):
		super(Direction, self).__init__(*args, **kwargs)

	def __str__(self) -> str:
		string = self.formatString.format(self)
		return '{cardinal} ({value}{decorator})'.format(cardinal=self.cardinal, value=string, decorator=self._decorator)

	@property
	def cardinal(self):
		dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
		ix = round(self / (360. / len(dirs)))
		return dirs[ix % len(dirs)]
