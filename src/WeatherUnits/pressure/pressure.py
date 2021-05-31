from typing import Callable

from .._unit import Measurement


class Pressure(Measurement):
	_type = 'pressure'
	_format = "{:4d}"
	_hPa: Callable
	_mmHg: Callable
	_inHg: Callable

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

	mb = hPa
	mbar = hPa
	bar = hPa
	inches = inHg
	mm = mmHg
