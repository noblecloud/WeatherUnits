
from ...others import Direction, Voltage, LightningStrike, Humidity
from ...others.light import UVI, Lux, RadiantFlux
from ...time_ import *
from ...pressure import Millibar
from ...derived import Wind, Precipitation
from ...derived.precipitation import Daily as PrecipitationDaily, Hourly as PrecipitationHourly, Minutely as PrecipitationMinutely
from ...temperature import Celsius
from ...length import Kilometer, Meter, Millimeter
from ...various import RSSI
from enum import Flag as _Flag


class SensorStatus(_Flag):
	OK = 0b000000000
	LightningFailed = 0b000000001
	LightningNoise = 0b000000010
	LightningDisturbance = 0b000000100
	PressureFailed = 0b000001000
	TemperatureFailed = 0b000010000
	RHFailed = 0b000100000
	WindFailed = 0b001000000
	PrecipitationFailed = 0b010000000
	LightFailed = 0b100000000


class Debug(_Flag):
	Disabled = 0
	Enabled = 1


class ResetFlags(_Flag):
	BOR = 'Brownout'
	PIN = 'PIN'
	POR = 'Power'
	SFT = 'Software'
	WDG = 'Watchdog'
	WWD = 'WindowWatchdog'
	LPW = 'LowPower'


UDPClasses = {
		'time':                  int,
		'lullSpeed':             'Wind',
		'windSpeed':             'Wind',
		'gustSpeed':             'Wind',
		'speed':                 'Wind',
		'direction':             Direction,
		'windDirection':         Direction,

		'windSampleInterval':    Time.Second,
		'pressure':              Millibar,
		'temperature':           Celsius,
		'humidity':              Humidity,

	'illuminance':             Lux,
	'uvi':                     UVI,
	'irradiance':              RadiantFlux,

	'precipitationRate':       'Precipitation',
	'precipitationDaily':      'PrecipitationDaily',
	'precipitationType':       Precipitation.Type,

	'distance':                Kilometer,
	'lightningLastDistance':   Kilometer,
	'lightning':               LightningStrike,
	'lightningEnergy':         int,

	'battery':                 Voltage,
	'reportInterval':          Time.Minute,
	'Wind':                    (Wind, Meter, Time.Second),
	'Precipitation':           (Precipitation.Hourly, Millimeter, Time.Minute),
	'PrecipitationDaily':      (Precipitation.Daily, Millimeter, Time.Day),

	'deviceSerial':            str,
	'hubSerial':               str,
		'uptime':                Time.Second,
		'firmware':              int,
		'deviceRSSI':            RSSI,
		'hubRSSI':               RSSI,
		'sensorStatus':          SensorStatus,
		'debug':                 Debug,
		'resetFlags':            'resetFlag',
		'resetFlag':             ResetFlags,
}

'''
Sky
0	Time Epoch	Seconds
1	Illuminance	Lux
2	UV	Index
3	Rain amount over previous minute	mm
4	Wind Lull (minimum 3 second sample)	m/s
5	Wind Avg (average over report interval)	m/s
6	Wind Gust (maximum 3 second sample)	m/s
7	Wind Direction	Degrees
8	Battery	Volts
9	Report Interval	Minutes
10	Solar Radiation	W/m^2
11	Local Day Rain Accumulation	mm
12	Precipitation Type	0 = none, 1 = rain, 2 = hail
13	Wind Sample Interval	seconds

Air
0	Time Epoch	Seconds
1	Station Pressure	MB
2	Air Temperature	C
3	Relative Humidity	%
4	Lightning Strike Count
5	Lightning Strike Avg Distance	km
6	Battery
7	Report Interval	Minutes

Tempest
0	Time Epoch	Seconds
1	Wind Lull (minimum 3 second sample)	m/s
2	Wind Avg (average over report interval)	m/s
3	Wind Gust (maximum 3 second sample)	m/s
4	Wind Direction	Degrees
5	Wind Sample Interval	seconds
6	Station Pressure	MB
7	Air Temperature	C
8	Relative Humidity	%
9	Illuminance	Lux
10	UV	Index
11	Solar Radiation	W/m^2
12	Rain amount over previous minute	mm
13	Precipitation Type	0 = none, 1 = rain, 2 = hail, 3 = rain + hail (experimental)
14	Lightning Strike Avg Distance	km
15	Lightning Strike Count
16	Battery	Volts
17	Report Interval	Minutes

'''


class UDP:
	# __slots__ = ['messageTypes', 'Message', 'Wind', 'Event', 'ObservationSet', 'Status', 'Device', 'Hub']

	messageTypes = {
			'air':        'obs_air',
			'sky':        'obs_sky',
			'tempest':    'obs_st',

			'obs_st':     ['time', 'lullSpeed', 'windSpeed', 'gustSpeed', 'windDirection',
			               'windSampleInterval', 'pressure', 'temperature', 'humidity',
			               'illuminance', 'uvi', 'irradiance', 'precipitationRate',
			               'precipitationType', 'lightningLastDistance', 'lightning',
			               'battery', 'reportInterval'],

			'obs_sky':    ['time', 'illuminance', 'uvi', 'precipitationHourlyRaw', 'lullSpeed',
			               'windSpeed', 'gustSpeed', 'windDirection', 'battery', 'reportInterval',
			               'irradiance', 'precipitationDaily', 'precipitationType', 'windSampleInterval'],

			'obs_air':    ['time', 'pressure', 'temperature', 'humidity', 'lightning', 'lightningLastDistance',
			               'battery', 'reportInterval'],

			'wind':       'rapid_wind',
			'rain':       'evt_precip',
			'lightning':  'evt_strike',

			'rapid_wind': ['time', 'speed', 'direction'],

			'evt_strike': ['time', 'distance', 'energy'],

			'evt_precip': ['time']
	}

	Message = {'serial_number': str, 'hub_sn': str, 'type': str}
	Wind = {**Message, 'ob': list}
	Event = {**Message, 'evt': list}
	ObservationSet = {**Message, 'obs': list}

	Status = {'serial_number': str, 'type': str, 'timestamp': int, 'uptime': Time.Second, 'firmware_revision': int, 'rssi': RSSI}
	Device = {**Status, 'hub_sn': str, 'voltage': Voltage, 'hub_rssi': RSSI, 'sensor_status': SensorStatus, 'debug': Debug}
	Hub = {**Status, 'reset_flags': ResetFlags, 'radio_stats': list}
