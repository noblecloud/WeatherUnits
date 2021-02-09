from units._unit import Measurement


class Volts(Measurement):
	_format = "{:1.2f}"
	_unit = 'v'
	_unitFormat: str = '{}{}'
	_suffix = ''


class Direction(Measurement):
	_suffix = 'º'
	_format = "{:3d}"


	def __init__(self, *args, **kwargs):
		super(Direction, self).__init__(*args, **kwargs)

	def __str__(self) -> str:
		return str(round(self))

	@property
	def cardinal(self):
		dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
		ix = round(self / (360. / len(dirs)))
		return dirs[ix % len(dirs)]
