from .speed import Speed


class Wind(Speed):
	@property
	def fts(self):
		return Speed(self._numerator.ft, self._denominator.s)

	@property
	def mih(self):
		converted = Speed(self._numerator.mi, self._denominator.hr)
		converted._suffix = 'mph'
		return converted

	@property
	def inh(self):
		return Speed(self._numerator.inch, self._denominator.hr)

	@property
	def ms(self):
		return Speed(self._numerator.m, self._denominator.s)

	@property
	def mh(self):
		return Speed(self._numerator.m, self._denominator.hr)

	@property
	def kmh(self):
		return Speed(self._numerator.km, self._denominator.hr)

	@property
	def mmh(self):
		return Speed(self._numerator.mm, self._denominator.hr)
