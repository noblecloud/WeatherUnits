from .units import Temperature, Wind, Precipitation, PrecipitationDaily, PrecipitationType
from ...length import Kilometer
from ...others import Direction, Humidity, Lux, RadiantFlux, Volts
from ...pressure import mmHg
from ...time import Minute, Second

LargeDistance = Kilometer
Brightness = Lux
Irradiance = RadiantFlux
Power = Volts
Pressure = mmHg

classes = {
		'time':               int,
		'day':                int,
		'hour':               int,
		'windSpeed':          Wind,
		'direction':          Direction,

		'windSampleInterval': Second,
		'pressure':           mmHg,
		'temperature':        Temperature,
		'humidity':           Humidity,

		'illuminance':        Lux,
		'uvi':                int,
		'irradiance':         RadiantFlux,
		'precipitation':      Precipitation,
		'precipitationDaily': PrecipitationDaily,

		'precipitationType':  PrecipitationType,
		'distance':           Kilometer,
		'lightningDistance':  Kilometer,
		'lightning':          int,
		'energy':             int,

		'battery':            Volts,
		'reportInterval':     Minute,
		'reportIntervalFine': Second

}
