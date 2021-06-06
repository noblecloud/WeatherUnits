from .units import Temperature, Wind, Precipitation, PrecipitationDaily, PrecipitationType
from ...length import Kilometer
from ...others import Direction, Humidity, Lux, RadiantFlux, Voltage, Strikes, UVI

from ...pressure import mmHg
from ...time import Minute, Second, Day, Hour

LargeDistance = Kilometer
Brightness = Lux
Irradiance = RadiantFlux
Power = Voltage
Pressure = mmHg

classes = {
		'time':               int,
		'day':                Day,
		'hour':               Hour,
		'windSpeed':          Wind,
		'direction':          Direction,

		'windSampleInterval': Second,
		'pressure':           mmHg,
		'temperature':        Temperature,
		'humidity':           Humidity,

		'illuminance':        Lux,
		'uvi':                UVI,
		'irradiance':         RadiantFlux,
		'precipitation':      Precipitation,
		'precipitationDaily': PrecipitationDaily,

		'precipitationType':  PrecipitationType,
		'distance':           Kilometer,
		'lightningDistance':  Kilometer,
		'lightning':          Strikes,
		'energy':             int,

		'battery':            Voltage,
		'reportInterval':     Minute,
		'reportIntervalFine': Second

}
