class BadConversion(Exception):
	"""These two measurements can not be converted this way"""
	def __init__(self, first, second):
		self.message = f"{first} can not be converted to {second} this way"
		super().__init__(self.message)


class NoBaseUnitDefined(Exception):
	def __init__(self, cls):
		message = f'{self} has no defined baseUnit'
		super().__init__(message)
