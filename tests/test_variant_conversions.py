"""Every unit of every scaled dimension against its true SI value.

A scale's float "variants" (Calorie, Acre, Horsepower, ...) are sized in the
smallest unit of their ladder; these tables are the real-world sizes, so a wrong
entry or a broken conversion path both show up here. Pressure has its own file.
"""
import pytest

from unitcorn import length, mass
from unitcorn.area import area
from unitcorn.energy import energy
from unitcorn.time_ import time
from unitcorn.energy import power

REL = dict(rel=1e-6)

# dimension -> (module, base unit name, {unit name: size in SI})
DIMENSIONS = {
	'length-metric': (length, 'Meter', {
		'Millimeter': 1e-3, 'Centimeter': 1e-2, 'Decimeter': 0.1, 'Meter': 1.0,
		'Decameter': 10.0, 'Hectometer': 100.0, 'Kilometer': 1e3,
	}),
	'length-imperial': (length, 'Foot', {
		'Line': 0.3048 / 144, 'Inch': 0.0254, 'Foot': 0.3048, 'Yard': 0.9144, 'Mile': 1609.344,
	}),
	'mass-metric': (mass, 'Kilogram', {
		'Microgram': 1e-9, 'Milligram': 1e-6, 'Gram': 1e-3, 'Kilogram': 1.0, 'Tonne': 1e3,
	}),
	'mass-imperial': (mass, 'Pound', {
		'Dram': 0.45359237 / 256, 'Ounce': 0.45359237 / 16, 'Pound': 0.45359237,
		'Hundredweight': 45.359237, 'Ton': 907.18474,
	}),
	'time': (time, 'Second', {
		'Millisecond': 1e-3, 'Second': 1.0, 'Minute': 60.0, 'Hour': 3600.0, 'Day': 86400.0,
		'Week': 604800.0, 'Month': 365.2425 / 12 * 86400, 'Year': 365 * 86400.0,
	}),
	'energy': (energy, 'Joule', {
		'Joule': 1.0, 'Kilojoule': 1e3, 'Megajoule': 1e6, 'Gigajoule': 1e9,
		'WattHour': 3600.0, 'KilowattHour': 3.6e6, 'MegawattHour': 3.6e9,
		'Calorie': 4.184, 'BritishThermalUnit': 1055.05585262,
	}),
	'power': (power, 'Watt', {
		'Watt': 1.0, 'Kilowatt': 1e3, 'Megawatt': 1e6, 'Gigawatt': 1e9,
		'Horsepower': 745.69987158227, 'BritishThermalUnitPerHour': 0.29307107,
	}),
	'area': (area, 'SquareMeter', {
		'SquareMeter': 1.0, 'SquareCentimeter': 1e-4, 'SquareKilometer': 1e6, 'Hectare': 1e4,
		'SquareInch': 0.00064516, 'SquareFoot': 0.09290304, 'SquareMile': 2589988.110336,
		'Acre': 4046.8564224,
	}),
}

CASES = [(dim, unit) for dim, (_, _, table) in DIMENSIONS.items() for unit in table]


def _resolve(dim):
	module, baseName, table = DIMENSIONS[dim]
	return module, getattr(module, baseName), table


@pytest.mark.parametrize('dim,unit', CASES)
def test_unit_against_base(dim, unit):
	module, base, table = _resolve(dim)
	cls = getattr(module, unit)
	size = table[unit] / table[base.__name__]
	accessor = base.__name__[0].lower() + base.__name__[1:]

	assert float(base(cls(1))) == pytest.approx(size, **REL)
	assert float(cls(base(size))) == pytest.approx(1.0, **REL)
	assert float(cls(1).toBaseUnit()) == pytest.approx(size, **REL)
	assert float(getattr(cls(1), accessor)) == pytest.approx(size, **REL)
	assert float(cls(1)[base._unit]) == pytest.approx(size, **REL)
	assert float(base(size)[cls._unit]) == pytest.approx(1.0, **REL)


@pytest.mark.parametrize('dim', DIMENSIONS)
def test_every_pair(dim):
	module, _, table = _resolve(dim)
	for src in table:
		for dst in table:
			got = float(getattr(module, dst)(getattr(module, src)(1)))
			assert got == pytest.approx(table[src] / table[dst], **REL), f'{src} -> {dst}'
