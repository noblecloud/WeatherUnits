from . import Pressure


class inHg(Pressure):
	_unit = 'inHg'
	_format = '{2.2f}'

	def _hPa(self):
		return self * 33.86389

	def _mmHg(self):
		return self * 25.4

	def _inHg(self):
		return self
