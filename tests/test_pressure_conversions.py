"""Pressure conversions.

`TestConsumerPaths` pins the numbers LevityDash shows (hPa <-> inHg and friends)
so a change to the conversion machinery can't move them.
"""
import pytest

from unitcorn import pressure as P

# Display-level tolerance: these are shown to two decimals.
DISPLAY = dict(rel=1e-4)


class TestConsumerPaths:
	def test_hpa_to_inhg(self):
		h = P.Hectopascal(1013.25)
		assert float(h.inHg) == pytest.approx(29.9213, **DISPLAY)
		assert float(h['inHg']) == pytest.approx(29.9213, **DISPLAY)
		assert float(P.InchOfMercury(h)) == pytest.approx(29.9213, **DISPLAY)

	def test_inhg_to_hpa(self):
		i = P.InchOfMercury(29.92)
		assert float(i.hPa) == pytest.approx(1013.21, **DISPLAY)
		assert float(P.Hectopascal(i)) == pytest.approx(1013.21, **DISPLAY)
		assert float(i['mmHg']) == pytest.approx(759.968, **DISPLAY)

	def test_hpa_to_mmhg(self):
		assert float(P.Hectopascal(1013.25)['mmHg']) == pytest.approx(760.0, **DISPLAY)

	def test_other_sources_to_inhg(self):
		for source in (P.Kilopascal(101.325), P.Millibar(1013.25), P.Pascal(101325), P.MillimeterOfMercury(760)):
			assert float(source.inHg) == pytest.approx(29.9213, **DISPLAY)

	def test_localize_and_bestfit(self):
		# Which unit localize picks depends on the config another test loaded, so
		# pin the quantity, not the unit.
		h = P.Hectopascal(1013.25)
		for result in (h.localize, h.bestFit(), h.auto):
			assert isinstance(result, P.Pressure)
			assert float(result.hPa) == pytest.approx(1013.25, **DISPLAY)


# Size of each unit in Pascal.
PASCALS = {
	'Pascal': 1.0,
	'Decapascal': 10.0,
	'Hectopascal': 100.0,
	'Millibar': 100.0,
	'Kilopascal': 1e3,
	'Megapascal': 1e6,
	'Gigapascal': 1e9,
	'Bar': 1e5,
	'Atmosphere': 101325.0,
	'TechnicalAtmosphere': 98066.5,
	'PoundsPerSquareInch': 6894.757293168,
	'MillimeterOfMercury': 133.322387415,
	'InchOfMercury': 3386.389,
}
UNITS = list(PASCALS)
REL = dict(rel=1e-6)


def _accessor(name: str) -> str:
	return name[0].lower() + name[1:]


@pytest.mark.parametrize('name', UNITS)
class TestUnitAgainstPascal:
	"""Every unit <-> Pa, in both directions, through every path."""

	def test_constructor_to_pascal(self, name):
		assert float(P.Pascal(getattr(P, name)(1))) == pytest.approx(PASCALS[name], **REL)

	def test_constructor_from_pascal(self, name):
		assert float(getattr(P, name)(P.Pascal(PASCALS[name]))) == pytest.approx(1.0, **REL)

	def test_accessor_to_pascal(self, name):
		assert float(getattr(P, name)(1).pascal) == pytest.approx(PASCALS[name], **REL)

	def test_accessor_from_pascal(self, name):
		assert float(getattr(P.Pascal(PASCALS[name]), _accessor(name))) == pytest.approx(1.0, **REL)

	def test_symbol_to_pascal(self, name):
		assert float(getattr(P, name)(1)['Pa']) == pytest.approx(PASCALS[name], **REL)

	def test_symbol_from_pascal(self, name):
		symbol = getattr(P, name)._unit
		assert float(P.Pascal(PASCALS[name])[symbol]) == pytest.approx(1.0, **REL)

	def test_to_base_unit(self, name):
		assert float(getattr(P, name)(1).toBaseUnit()) == pytest.approx(PASCALS[name], **REL)

	def test_value_scales_linearly(self, name):
		assert float(P.Pascal(getattr(P, name)(2.5))) == pytest.approx(2.5 * PASCALS[name], **REL)


@pytest.mark.parametrize('src', UNITS)
@pytest.mark.parametrize('dst', UNITS)
def test_every_pair(src, dst):
	"""Unit to unit, including variant to variant and variant to ladder unit."""
	got = float(getattr(P, dst)(getattr(P, src)(1)))
	assert got == pytest.approx(PASCALS[src] / PASCALS[dst], **REL)
