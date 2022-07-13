# WeatherUnits️ 🌧
Easily convert typical weather units from one unit to another with automatic localization.

## Features
🌈 Effortlessly define or extend your own units

☀️ Change nearly every part of unit display from a config.ini file. No need for additional code.

❄️ Localization can is as simple as adding .localize to a units variable or setting it to automatic

## Requirements

- Python 3.7

## How to use

**Note: The following documentation is currently out of date after some major changes**

### Unit Conversion

Conversion is as easy as using the desired unit's name or aliases as either an attribute or subscript

```python
from WeatherUnits.temperature import Fahrenheit
>>> value = Fahrenheit(32)
>>> value
'32º'
>>> value.withUnit
'32ºf'
>>> value['c'].withUnit
'0ºc'
>>> value.celcius
'0º'
```

## Using a Config file

#### Loading a config file
```python
import WeatherUnits as wu
wu.config.read('config.ini')
```
A template config file can be found in [src/WeatherUnits/config](src/WeatherUnits/config/template.ini).  There are three sections in a valid config file
1) LocalUnits: This is what defines what units you want to use for localization
2) UnitDefaults: This section holds the default values that apply to every unit
3) UnitProperties: Defines properties for individual units or unit systems as a whole

### UnitDefaults
The basic rules are:

1) Properties are specified without the leading '_'
2) Units are specified with their lowercase names or types
3) Empty values will be read as '' and denote being set
4) Values without an '=' will be read as None and denote being unset

#### Properties
- **precision:**  The number of digits allowed to be displayed past the decimal but will not exceed max Example number:

    |example|3.14159m|
    |-------|--------|
    |0|3m|
    |1|3.1m|
    |2|3.14m|
    |3|3.141m|

- **max:**  The total number of digits that can be displayed while still showing the decimal.  If shorten is True, numbers would be reduced by factors of 10³

    |example|415.25mm|
    |-----|-------|
    |2|0.4k mm|
    |3|415mm|
    |4|415.3mm|
    |5|415.25mm|

- **unit:** Override built in unit string
- **suffix:** Override built in suffix string._Only used for shortening numbers_
- **decorator:** Override built in decorator._Only used for º with degrees_
- **title:** Title to be used by other display programs
- **exp:** Override exponent.  I can't imagine why this would be used
- **showUnit:** Show unit True: 5km False: 5
- **leadingZero:** Display zero before values less than 1 True: 0.1in False: .1in
- **trailingZero:** Display zero after decimal point to full precision staying under max True: 1.0in False: 1in True: 4.00cm
- **unitSpacer:** Determines if there is a space between measurements and their units True: 90º f False: 90ºf
- **kSeparator:**

    |value|example|
    |----|------|
    |True|1,000ft|
    |False|1000ft|

- **shorten:** Shortens values to fit within the max display amount

    |value|example|
    |----|------|
    |True|1k s|
    |False|1000s|

- **slide:** Scale units for the appropriate values. _Not yet implemented_

    |value|example|
    |----|------|
    |True|1km|
    |False|1000m|

- **cardinal:** Show degrees as cardinal direction. **_Shorten_** _decides full vs abbreviated name_

    |value|example|
    |----|------|
    |True|180º|
    |False|South|

- **key:** Key to be used for other programs
- **sizeHint:** Override generated size hint string. Useful for when you know the expected max string length.


## Defining Your Own Unit

There are currently three types of unit, **Static**, **Scaling**, and **Derived**

### Static Unit
The most simple to define. Temperature is an example of a static unit.
Similar units of the same are a subclass of the unit type. In the example below,
Fahrenheit, Celsius, and Kelvin are subclasses of Temperature. Convert to other
similar units with a single private function sharing the name of the desired unit.

```python
from WeatherUnits.base import Measurement, NamedType

@NamedType  # Unit types are defined with this decorator.
class Temperature(Measurement):  # For static unit types, the class inherits Measurement.

    # Shared unit properties are defined here or in a provided config file.
    _decorator = 'º'

    # Properties for converting units are defined in the main parent class.
    @property
    def fahrenheit(self):
        # Unless all the subunits are defined in the same file, importing the desired
        # class locally is currently necessary.
        return Fahrenheit(self._fahrenheit())

    # Unit abbreviations are defined somewhere below the converting property.
    f = fahrenheit

    @property
    def celsius(self):
        return Celsius(self._celsius())
    c = celsius

class Fahrenheit(Temperature):
    # Individual unit strings are defined as protected class variables
    # for each unit or within a config file.
    _unit = 'f'

    # This method is what is called to convert Fahrenheit to Celsius.
    def _celsius(self):
        # Since Measurement is a float subclass, math can be done on self.
        return (self - 32) / 1.8

    def _fahrenheit(self):
        # Currently, a function needs to be defined for even converting to the
        # same unit to prevent errors.
        return self

class Celsius(Temperature):
    _unit = 'c'

    def _celsius(self):
        return self

    def _fahrenheit(self):
        return (self * 1.8) + 32
```

### Scaling Unit

Scaling units have quite a bit going on.  A scaling unit can be reduced to a single unit through a multiplier, this is the base unit.
Multiple unit systems can be defined within one scale.  It is also to split systems separate scales as long as there is a function within
each system that converts from one base unit to the other.

- **SystemVariant:** A class that denotes is not the unit is not within the regular scale
- **Synonym:** Denotes that a unit is the same as an already defined but uses another name. Synonym classes inherit their identically valued class
- **Dimension:** Decorator that assigns the decorated class to _unitSystem of all child classes
- **BaseUnit:** Decorator to define the base unit for the system, this will be used for converting to the non-standard 'SystemVariant'
- **Scale:** Uses the metaclass EnumMeta to define the scaling factors for a ScalingMeasurement class along with the multipliers for any SystemVariants
and the base unit

To define a scaling measurement (one that has multiple units within the same unit system, think Centimeter, Meter, Kilometer)
the unit system class inherits ScalingMeasurement.  The main difference from Measurement is the _Scale class defined inside the
main parent class.  In the example below, two unit systems (US and SI) are defined in the same scale.  Most US units
have an SI basis, so this can be done fairly often.  However, it is sometimes necessary to split them for readability.

#### Unified System

```python

from WeatherUnits.base import NamedType, Synonym, ScalingMeasurement
from WeatherUnits.base import Scale, BaseUnit, SystemVariant, Dimension

@NamedType
class Pressure(ScalingMeasurement):

    # The scale for the unit system is defined with by a class named _Scale inheriting.
    class _Scale(Scale):
        # Every unit is named here starting with the smallest unit and assigned a
        # scaling multiplier.  Scaling multipliers here must be an integer.
        Pascal = 1
        Decapascal = 10
        Hectopascal = 10

        # A base unit is also defined denoted by Base = class.__name__.
        # Base value must be a string.
        Base = 'Pascal'

        # System variants are units that fall outside of the normal scale
        # The multiplier value for variants must be a float and be relative
        # to the base unit.  For example, 1 Bar is 1000 Pascals and
        # 1 MillimeterOfMercury is 1/0.00750062 or 133.3 Pascals.
        Bar = 1000.
        Atmosphere = 101325.
        PoundsPerSquareInch = 6894.757293168
        MillimeterOfMercury = 1 / 0.00750062
        InchOfMercury = 1 / 0.00029530

    @property
    def pascal(self):
        return Pascal(self)

    @property
    def hectopascal(self):
        return Hectopascal(self)

@BaseUnit
class Pascal(Pressure):
    _unit = 'Pa'

class Hectopascal(Pressure):
    _unit = 'hPa'

class Atmosphere(Pascal, SystemVariant):
    _unit = 'atm'

@Synonym
class Millibar(Hectopascal):
    _unit = 'mBar'
    _max = 4
```

#### Split system

```python
from WeatherUnits.base import NamedType, ScalingMeasurement, Dimension, BaseUnit


@NamedType
class Length(ScalingMeasurement):

    @property
    def meter(self):
        return Meter(self)
    m = meter

    @property
    def foot(self):
        return Foot(self)
    ft = foot


class ImperialLength(Length):

    class _Scale(Scale):
        Line = 1
        Inch = 12
        Foot = 12
        Yard = 3
        Mile = 1760
        Base = 'Foot'

    # Since the multipliers are defined in _Scale, changeScale() uses one
    # parameter to change the scale within the same system.
    def _foot(self):
        return self.changeScale(self._Scale.Foot)

    # This function is called to convert from ImperialLength to MetricLength.  Once its
    # converted to MetricLength, changeScale() is called within the MetricLength class
    # to get to the final unit.
    def _meter(self):
        return self._foot() * 0.3048


@BaseUnit
class Foot(ImperialLength):
    _unit = 'ft'


@Dimension
class MetricLength(Length):

    class _Scale(Scale):
        Millimeter = 1
        Centimeter = 10
        Decimeter = 10
        Meter = 10
        Decameter = 10
        Hectometer = 10
        Kilometer = 10
        Base = 'Meter'

    def _meter(self):
        return self.changeScale(self._Scale.Meter)

    # As with the pervious class, this method is called to convert from MetricLength
    # to ImperialLength.
    def _foot(self):
        return self._meter() * 3.280839895013123


@BaseUnit
class Meter(MetricLength):
    _unit = 'm'
```


### Derived Unit
DerivedMeasurement is essentially a measurement with multiple units, eg, m/s [meters per second], mph [miles per hour].
Initiation takes in two Measurements and is stored as the dividend of the two.  Both values are independently stored
as protected variables.

**Note:**
This type still needs quite a lot of work.  Currently, it only has fractional support, and only a single unit can be used for
both the numerator and denominator.  Eventually this will be expanded allowing for more complex unit derivatives.
Support for the following has not been added:
 - Multiplying two units together, for example a pascal second [Pa·s]
 - Negative exponent units like Hertz [s⁻¹]
 - Multiple units in either the numerator or denominator

```python
from WeatherUnits import Length, Time
from WeatherUnits.base import DerivedMeasurement, NamedType, NamedSubType


# Summary of the DerivedMeasurement class
class DerivedMeasurement(Measurement):
    _numerator: Measurement
    _denominator: Measurement

    def __init__(self, numerator, denominator):
        self._numerator = numerator
        self._denominator = denominator
        Measurement.__init__(self, numerator / denominator)


@NamedType
class DistanceOverTime(DerivedMeasurement):
    # Defining the unit types for the derived unit helps keep things clear
    _numerator: Length
    _denominator: Time

    # Currently all variations that will be used have to be defined as properties
    @property
    def mih(self):
        converted = DistanceOverTime(self._numerator.mi, self._denominator.hr)

        # Without this override, the unit would be displayed as 'mi/hr'
        converted._suffix = 'mph'
        return converted

    @property
    def ms(self):
        return DistanceOverTime(self._numerator.m, self._denominator.s)

    @property
    def kmh(self):
        return DistanceOverTime(self._numerator.km, self._denominator.hr)

    mph = mih


@NamedType
class Precipitation(DistanceOverTime):
    _numerator: Length
    _denominator: Time

    @property
    def inh(self):
        return Precipitation(self._numerator.inch, self._denominator.hr)

    @property
    def mmh(self):
        return Precipitation(self._numerator.mm, self._denominator.hr)


@NamedType
class PrecipitationRate(Precipitation):
    pass


@NamedSubType
class Daily(Precipitation):

    def __init__(self, numerator: Length, denominator: int = 1, *args, **kwargs):
        if isinstance(denominator, int):
            denominator = Time.Day(denominator)
        Precipitation.__init__(self, numerator, denominator, *args, **kwargs)

```