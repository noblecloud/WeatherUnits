class BadConversion(Exception):
	"""These two measurements can not be converted this way"""
	def __init__(self, first, second):
		self.message = f"{first} can not be converted to {second} this way"
		super().__init__(self.message)
