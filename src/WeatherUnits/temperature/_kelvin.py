from . import Temperature


class Kelvin(Temperature):
	_format = '{value}{decorator}'
	_decorator = ''
	_unit = 'k'
	_unitFormat: str = '{decorated}{unit}'

	def _kelvin(self):
		return self

	def _celsius(self, delta: bool = False):
		return self - 273.15

	def _fahrenheit(self, delta: bool = False):
		if delta:
			return (self - 273.15) * 1.8
		else:
			return ((self - 273.15) * 1.8) + 32
