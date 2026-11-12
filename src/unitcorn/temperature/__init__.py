from .temperature import Temperature
from .fahrenheit import Fahrenheit
from .celsius import Celsius
from .kelvin import Kelvin
from .change import TemperatureChange, CelsiusChange, FahrenheitChange, KelvinChange, summingReadings

__all__ = ['Temperature', 'TemperatureChange', 'CelsiusChange', 'FahrenheitChange', 'KelvinChange', 'summingReadings']

Temperature.Fahrenheit = Fahrenheit
Temperature.Celsius = Celsius
Temperature.Kelvin = Kelvin

Temperature.Change = TemperatureChange
Temperature.CelsiusChange = CelsiusChange
Temperature.FahrenheitChange = FahrenheitChange
Temperature.KelvinChange = KelvinChange
Celsius.change = CelsiusChange
Fahrenheit.change = FahrenheitChange
Kelvin.change = KelvinChange
