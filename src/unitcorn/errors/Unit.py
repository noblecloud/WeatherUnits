class NoBaseUnitDefined(Exception):
	def __init__(self, cls):
		message = f'{self} has no defined baseUnit'
		super().__init__(message)
