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
		h = P.Hectopascal(1013.25)
		assert type(h.localize) is P.MillimeterOfMercury
		assert float(h.localize) == pytest.approx(760.0, **DISPLAY)
		assert type(h.bestFit()) is P.MillimeterOfMercury
