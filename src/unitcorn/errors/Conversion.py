class BadConversion(Exception):
	"""These two measurements can not be converted this way"""
	def __init__(self, first, second):
		self.message = f"{first} can not be converted to {second} this way"
		super().__init__(self.message)


class UnknownUnit(Exception):
	"""This measurement can not be converted to that unit"""
	def __init__(self, measurement, unit: str):
		self.message = f"{measurement} can not be converted to '{unit}'"
		super().__init__(self.message)
