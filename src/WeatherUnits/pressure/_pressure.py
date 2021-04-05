
from .._unit import Measurement


class Pressure(Measurement):
	_type = 'pressure'
	_format = "{:2.2f}"

	@property
	def mbar(self):
		from ..pressure import hPa
		return hPa(self._hPa())

	@property
	def mb(self):
		from ..pressure import hPa
		return hPa(self._hPa())

	@property
	def hPa(self):
		from ..pressure import hPa
		return hPa(self._hPa())

	@property
	def mmHg(self):
		from ..pressure import mmHg
		return mmHg(self._mmHg())

	@property
	def inHg(self):
		from ..pressure import inHg
		return inHg(self._inHg())
