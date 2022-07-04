__all__ = ['RSSI']

from ..base.Decorators import UnitType
from ..base import Measurement


@UnitType
class RSSI(Measurement):
	_unit = 'dBm'
	_strings = ['Perfect', 'Great', 'Good', 'Bad', 'None']
	_values = [-30, -67, -70, -80, -90]
	_precision = 0
	_max = 2

	@property
	def string(self):
		v = int(self)
		i = 0
		while v < self._values[i] and i < 6:
			i += 1
		return self._strings[i]
