from .units import Heat, Wind, Precipitation, PrecipitationDaily, PrecipitationType
from units.pressure import mmHg
from units.time import Second, Minute
from units.others import Humidity, RadiantFlux, Lux, Volts
from units.length import Meter, Kilometer, Millimeter

classes = {
		'time':               int,
		'day':                int,
		'hour':               int,
		'lullSpeed':          Wind,
		'windSpeed':          Wind,
		'gustSpeed':          Wind,
		'speed':              Wind,
		'direction':          int,
		'windDirection':      int,

		'windSampleInterval': Second,
		'pressure':           mmHg,
		'temperature':        Heat,
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
