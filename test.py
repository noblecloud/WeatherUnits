# import src.WeatherUnits as wu
#
# x = wu.Precipitation(wu.Length.Inch(1), wu.Time.Day(1))
#
# print(x.__class__.__name__)
# # d = derived.DistanceOverTime(l,tt)
# # x = others.Direction(0)
# # x |= others.Direction(1)
# # print(tt.sizeHint)
# # print(l)
# # print
from datetime import datetime
from unittest import TestCase

import src.WeatherUnits as wu


h1 = wu.Humidity(0.1)
h2 = wu.Humidity(0.01)
hash(h2)

h1 == h2


d = datetime.fromtimestamp(1664144061.0)
t = wu.Time.Second(d).auto
print(f'{t:simple}')
# t = wu.Time.Year < wu.Time.Hour
v = wu.Length.Kilometer(.07) + wu.Length.Meter(0.1) + wu.Length.Millimeter(50.5)
a = v.mm
print(a.upCommon)
print(f'{t:shorten=True}')
print(str(t))
print(f'{t.auto:simple}')
round(t, 2)
v = wu.Length.Kilometer(.7) + wu.Length.Meter(0.1) + wu.Length.Millimeter(50.5)
print(f'{v}')
v += 1
temp = wu.Temperature.Fahrenheit(80)
wu.auto('1 min')
print(f'{temp:c}')
# print(wu.Length.Centimeter.limits)
# print(f'{v:{"decorator": "+"}}')
newCls = wu.Wind['km/hr']
# print (wu.Length.Inch.pluralName)
# print(repr(newCls))
minutely = wu.Precipitation.Rate['mm':'min'](0.011505)
hourly = minutely['inches per hour']
humd = wu.Percentage.Humidity(0.5)
temp.heatIndex(humd)
a = newCls(v)['mph']
a.type.compatibleUnits
str(a['min'].denominator)
print(repr(a))
print('-------')
print(f"{v:precision=5, max=3, format={'{value}{decorator} {unit}'}}")
print(f"{v:unitSpacer=False}")
a = wu.others.Direction(90)
print(f'{a:cardinal: False, format={"{value} {decorator} {cardinal}"}}')
print(repr(a))
v = v.mm
print(v)
b = newCls[:type(t)]
print(a.cardinal)
r = wu.Precipitation.Hourly(v)
f'{r:inches per day:+4.2}'
a = wu.Mass.Milligram(100)
print(f'{a:cm per hour:}')

print(f'{a:mg:format={"{value}{unit}"}}')

print('-----d--')
fire = f'{a:g::.2g}'
f'{a:{"{test}"}}'
print(f'{r:format={"{value}{unit}"}}')
print(r.unit)
print(r)
# kgm = wu.Density[wu.Mass.Kilogram, wu.Length.Meter]
r.localize

# print(wu.derived.precipitation.Daily._precision)
# print(wu.temperature.Fahrenheit._precision)
# print(wu.temperature.Temperature._precision)
# # wu.config['UnitProperties']['humidity'] = 'precision=2, max=5'
# wu.config.read('./tests/config.ini')
# # reload(sys.modules['src.WeatherUnits'])
# print(wu.derived.precipitation.Daily._precision)
# print(wu.temperature.Fahrenheit._precision)
# print(wu.temperature.Temperature._precision)
#
# a = wu.Temperature.Celsius(0)
# a |= wu.Temperature.Celsius(20)
# print(a._precision)
# b = wu.Temperature.Fahrenheit(a)
# b = a.localize
# # temp = wu.Temperature.Celsius(20)
# #
# # x = wu.Light.Lux(1230, title='test', key='non')
# d = wu.Length.Millimeter(1.9)
#
# # h = wu.Humidity(97.13)
# t = wu.Time.Minute(1)
# # value = wu.derived.Wind(d, t)
# temp = wu.Temperature.Celsius(99.1)
# value = wu.Precipitation.Rate(d, t, title='test')
# # print(value.withUnit)
# # value = wu.Precipitation.Daily(d)
# # print(value.title)
# print(temp)
# print(temp.sizeHint)

zero = wu.Light.Lux(0)
zeroIsh = wu.Light.Lux(0.4334)
oneHundred = wu.Light.Lux(100)
oneThousand = wu.Light.Lux(1054)
oneMillion = wu.Light.Lux(1024581)
smaller = wu.Light.Lux(824581)

print(zero)
print(zeroIsh)
print(oneThousand)
print(oneHundred)
print(oneMillion)
print(smaller)

# a = Trend('steady', title='tse;', key='key')
