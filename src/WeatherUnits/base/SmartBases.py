
class SmartString(str):
	_title = ''
	_key = ''

	def __new__(cls, value: str, title: str = None, key: str = None):
		return str(value)

	def __init__(self, value: str, title: str = None, key: str = None):
		self._key = key
		self._title = title
		super(SmartString, self).__init__(value)

	@property
	def title(self):
		return self._title

	@property
	def key(self):
		return self._key

	def type(self):
		return type(self)

	def category(self):
		return self.__class__.__name__
