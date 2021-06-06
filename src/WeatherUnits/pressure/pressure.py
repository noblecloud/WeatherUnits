from typing import Callable

from .. import Measurement as _Measurement, MeasurementGroup


@MeasurementGroup
class Pressure(_Measurement):
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
