from enum import Enum

__all__ = ['PrimaryPollutant', 'HeathConcern', 'AQI', 'PollutionIndex']

from ..base import Measurement


class DescriptiveEnum(Enum):

	def __new__(cls, *args, **kwargs):
		obj = object.__new__(cls)
		obj._value_ = args[0]
		return obj

	def __init__(self, _: str, text: str = None):
		self._text_ = text

	def __str__(self):
		return self.text

	@property
	def text(self):
		return self._text_


class PrimaryPollutant(DescriptiveEnum):
	PM2_5 = 0, 'PM2.5'
	PM10 = 1, 'PM10'
	O3 = 2, 'O₃'
	NO2 = 3, 'NO₂'
	CO = 4, 'CO'
	SO2 = 5, 'SO₂'


class PollutionIndex(DescriptiveEnum):
	none = 0, 'None'
	VeryLow = 1, 'Very Low'
	Low = 2, 'Low'
	Medium = 3, 'Medium'
	High = 4, 'High'
	VeryHigh = 5, 'Very High'


class EmojiEnum(Enum):

	def __new__(cls, *args, **kwargs):
		obj = object.__new__(cls)
		obj._value_ = args[0]
		return obj

	def __init__(self, _: str, text: str = None, emoji: str = None):
		self._text_ = text
		self._emoji_ = emoji

	def __str__(self):
		return self.text

	@property
	def emoji(self):
		return self._emoji_

	@property
	def text(self):
		return self._text_


class HeathConcern(EmojiEnum):
	Good = 0, 'Good', '☺️'
	Moderate = 1, 'Moderate', '😀'
	UnhealthyForSensitiveGroups = 2, 'Unhealthy For Sensitive Groups', '😯'
	Unhealthy = 3, 'Unhealthy', '🙁'
	VeryUnhealthy = 4, 'Very Unhealthy', '☹️'
	Hazardous = 5, 'Hazardous', '😷'


class AQI(Measurement):

	@property
	def text(self) -> str:
		return self.enum.text

	@property
	def emoji(self) -> str:
		return self.enum.emoji

	@property
	def enum(self) -> HeathConcern:
		if self >= 50:
			return HeathConcern.Good
		elif self >= 100:
			return HeathConcern.Moderate
		elif self >= 150:
			return HeathConcern.UnhealthyForSensitiveGroups
		elif self >= 200:
			return HeathConcern.Unhealthy
		elif self >= 300:
			return HeathConcern.VeryUnhealthy
		else:
			return HeathConcern.Hazardous
