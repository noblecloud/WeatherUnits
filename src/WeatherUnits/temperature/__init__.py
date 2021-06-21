from .temperature import Temperature
from .fahrenheit import Fahrenheit
from .celsius import Celsius
from .kelvin import Kelvin

__all__ = ['Temperature']

Temperature.Fahrenheit = Fahrenheit
Temperature.Celsius = Celsius
Temperature.Kelvin = Kelvin
