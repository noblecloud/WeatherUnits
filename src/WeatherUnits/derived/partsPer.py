from ..base.Decorators import UnitType
from ..base import Scale
from . import ScalingMeasurement

__all__ = ['PartsPer']


@UnitType
class PartsPer(ScalingMeasurement, baseClass='Hundred'):
	_precision = 0

	class _Scale(Scale):
		Hundred = 100
		Thousand = 10
		TenThousand = 10
		HundredThousand = 10
		Million = 10
		Billion = 1000
		Trillion = 1000
		Base = 'Hundred'
		Precent = 100.

	@property
	def hundred(self):
		return Hundred(self)
	precent=hundred

	@property
	def thousand(self):
		return Thousand(self)

	@property
	def tenThousand(self):
		return TenThousand(self)

	@property
	def hundredThousand(self):
		return HundredThousand(self)

	@property
	def million(self):
		return Million(self)
	ppm = million

	@property
	def billion(self):
		return Billion(self)
	ppb = billion

	@property
	def trillion(self):
		return Trillion(self)
	ppt = trillion


class Hundred(PartsPer):
	_precision = 2
	_max = 3
	_unit = '%'


Percent = Hundred


class Thousand(PartsPer):
	_unit = '‰'


class TenThousand(PartsPer):
	_unit = '‱'


class HundredThousand(PartsPer):
	_unit = 'pcm'


class Million(PartsPer):
	_unit = 'ppm'


class Billion(PartsPer):
	_unit = 'ppb'


class Trillion(PartsPer):
	_unit = 'ppt'


PartsPer.Hunderd = Hundred
PartsPer.Precent = Hundred
PartsPer.Thousand = Thousand
PartsPer.TenThousand = TenThousand
PartsPer.HundredThousand = HundredThousand
PartsPer.Million = Million
PartsPer.Billion = Billion
PartsPer.Trillion = Trillion
