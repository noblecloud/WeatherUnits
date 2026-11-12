"""PPFD, DLI and VPD: what a grower reads off a light meter and a hygrometer."""
import math
from datetime import timedelta

import pytest

import unitcorn as uc
from unitcorn import DLI, PPFD, Humidity, Pressure, Temperature, Time


def tetens(celsius: float) -> float:
	"""Saturation vapour pressure in kPa, written out from the formula."""
	return 0.6108 * math.exp(17.27 * celsius / (celsius + 237.3))


class TestPPFDAndDLI:
	def test_dli_from_500_for_16_hours(self):
		dli = PPFD(500).dli(16)
		assert isinstance(dli, DLI)
		assert float(dli) == 28.8
		assert float(dli) == 500 * 3600 * 16 / 1e6

	def test_dli_is_exact_arithmetic(self):
		for ppfd, hours in ((1, 1), (200, 12), (1000, 24), (37.5, 18), (0, 16)):
			assert float(PPFD(ppfd).dli(hours)) == ppfd * 3600 * hours / 1e6

	def test_photoperiod_as_a_time_or_a_timedelta(self):
		assert float(PPFD(500).dli(Time.Hour(16))) == 28.8
		assert math.isclose(float(PPFD(500).dli(Time.Minute(960))), 28.8, rel_tol=1e-12)
		assert math.isclose(float(PPFD(500).dli(Time.Second(57600))), 28.8, rel_tol=1e-12)
		assert math.isclose(float(PPFD(500).dli(timedelta(hours=16))), 28.8, rel_tol=1e-12)

	def test_ppfd_from_a_dli(self):
		ppfd = DLI(28.8).ppfd(16)
		assert isinstance(ppfd, PPFD)
		assert math.isclose(float(ppfd), 500, rel_tol=1e-12)
		assert math.isclose(float(DLI(28.8).ppfd(Time.Hour(16))), 500, rel_tol=1e-12)

	@pytest.mark.parametrize('hours', [1, 8, 12.5, 16, 24])
	def test_round_trip(self, hours):
		assert math.isclose(float(PPFD(321.5).dli(hours).ppfd(hours)), 321.5, rel_tol=1e-12)

	@pytest.mark.parametrize('hours', [-1, 24.5, 25])
	def test_a_day_is_at_most_24_hours(self, hours):
		with pytest.raises(ValueError, match='photoperiod'):
			PPFD(500).dli(hours)
		with pytest.raises(ValueError, match='photoperiod'):
			DLI(20).ppfd(hours)

	def test_no_light_for_no_time_has_no_steady_ppfd(self):
		assert float(PPFD(500).dli(0)) == 0
		with pytest.raises(ValueError, match='photoperiod'):
			DLI(20).ppfd(0)

	def test_str(self):
		assert str(PPFD(500)) == '500 µmol/m²/s'
		assert str(PPFD(12.5)) == '12.5 µmol/m²/s'
		assert str(PPFD(1234.56)) == '1234.6 µmol/m²/s'
		assert str(PPFD(2150)) == '2150 µmol/m²/s'
		assert str(DLI(28.8)) == '28.8 mol/m²/d'
		assert str(DLI(0.256)) == '0.3 mol/m²/d'
		assert str(DLI(100)) == '100 mol/m²/d'
		assert PPFD(500).unit == 'µmol/m²/s'
		assert DLI(28.8).unit == 'mol/m²/d'
		assert PPFD(500).withUnit == '500 µmol/m²/s'

	@pytest.mark.parametrize('name', ['µmol/m²/s', 'umol/m2/s', 'PPFD', 'ppfd'])
	def test_ppfd_names(self, name):
		assert isinstance(uc.auto(500, name), PPFD)
		assert float(uc.auto(500, name)) == 500

	@pytest.mark.parametrize('name', ['mol/m²/d', 'mol/m2/d', 'DLI', 'dli'])
	def test_dli_names(self, name):
		assert isinstance(uc.auto(30, name), DLI)

	def test_they_live_under_light_too(self):
		assert uc.Light.PPFD is PPFD and uc.Light.DLI is DLI
		assert isinstance(PPFD(1), uc.Light)

	def test_a_rate_and_an_accumulation_are_not_interchangeable(self):
		assert not isinstance(PPFD(500), DLI)
		with pytest.raises(uc.errors.BadConversion):
			PPFD(500) + DLI(20)
		with pytest.raises(uc.errors.BadConversion):
			PPFD(500) + uc.Light.Irradiance(500)
		assert PPFD(500) != DLI(500)
		assert float(PPFD(500) + PPFD(100)) == 600
		assert isinstance(PPFD(500) + 100, PPFD)

	def test_ppfd_from_illuminance_needs_a_factor(self):
		with pytest.raises(TypeError):
			uc.Light.Illuminance(50000).ppfd()
		ppfd = uc.Light.Illuminance(50000).ppfd(18.5)
		assert isinstance(ppfd, PPFD) and math.isclose(float(ppfd), 925, rel_tol=1e-12)
		assert str(ppfd) == '925 µmol/m²/s'
		assert float(uc.Light.Illuminance(0).ppfd(18.5)) == 0


class TestVPD:
	def test_25c_60_percent(self):
		expected = tetens(25) * (1 - 0.60)
		v = uc.vpd(25, 60)
		assert isinstance(v, Pressure.Kilopascal)
		assert math.isclose(float(v), expected, rel_tol=1e-12)
		assert abs(float(v) - 1.27) < 0.005
		assert str(v) == '1.27 kPa'

	def test_the_saturation_pressure_is_tetens(self):
		assert math.isclose(float(uc.saturationVapourPressure(25)), 0.6108 * math.exp(17.27 * 25 / (25 + 237.3)), rel_tol=1e-12)
		assert str(uc.saturationVapourPressure(25)) == '3.2 kPa'
		assert math.isclose(float(uc.saturationVapourPressure(Temperature.Fahrenheit(77))), tetens(25), rel_tol=1e-9)

	@pytest.mark.parametrize('temperature', [
		Temperature.Celsius(25),
		Temperature.Fahrenheit(77),
		Temperature.Kelvin(298.15),
	])
	def test_any_scale_of_temperature(self, temperature):
		assert math.isclose(float(uc.vpd(temperature, 60)), tetens(25) * 0.4, rel_tol=1e-9)

	def test_fahrenheit_input(self):
		expected = tetens((86 - 32) * 5 / 9) * (1 - 0.45)
		v = uc.vpd(Temperature.Fahrenheit(86), 45)
		assert math.isclose(float(v), expected, rel_tol=1e-9)
		assert str(v) == '2.33 kPa'

	def test_plain_floats_are_celsius_and_percent(self):
		assert float(uc.vpd(25.0, 60.0)) == float(uc.vpd(Temperature.Celsius(25), Humidity.fromPercent(60)))
		assert float(uc.vpd(25, 0.6)) == float(uc.vpd(25, Humidity.fromPercent(0.6)))

	def test_a_humidity_is_a_humidity(self):
		assert math.isclose(float(uc.vpd(25, Humidity.fromFraction(0.6))), tetens(25) * 0.4, rel_tol=1e-12)
		assert math.isclose(float(uc.vpd(25, Humidity.fromPercent(60))), tetens(25) * 0.4, rel_tol=1e-12)

	def test_saturated_air_has_no_deficit_and_dry_air_all_of_it(self):
		assert float(uc.vpd(25, 100)) == 0
		assert math.isclose(float(uc.vpd(25, 0)), tetens(25), rel_tol=1e-12)

	@pytest.mark.parametrize('humidity', [-1, 100.5, 150])
	def test_humidity_outside_0_to_100_is_refused(self, humidity):
		with pytest.raises(ValueError, match='between 0 and 100'):
			uc.vpd(25, humidity)

	def test_a_gap_stays_a_gap(self):
		assert math.isnan(float(uc.vpd(25, float('nan'))))

	def test_leaf_offset(self):
		expected = tetens(25 - 2) - tetens(25) * 0.6
		v = uc.vpd(25, 60, leafOffset=2)
		assert math.isclose(float(v), expected, rel_tol=1e-12)
		assert str(v) == '0.91 kPa'
		assert float(uc.vpd(25, 60, leafOffset=0)) == float(uc.vpd(25, 60))
		assert float(uc.vpd(25, 60, leafOffset=-1)) > float(uc.vpd(25, 60))

	def test_leaf_offset_as_a_temperature_change(self):
		expected = float(uc.vpd(25, 60, leafOffset=2))
		assert math.isclose(float(uc.vpd(25, 60, leafOffset=Temperature.CelsiusChange(2))), expected, rel_tol=1e-12)
		assert math.isclose(float(uc.vpd(25, 60, leafOffset=Temperature.FahrenheitChange(3.6))), expected, rel_tol=1e-12)

	def test_the_result_is_a_pressure_that_converts(self):
		v = uc.vpd(25, 60)
		assert math.isclose(float(v.hectopascal), float(v) * 10, rel_tol=1e-12)
		assert math.isclose(float(Pressure.Pascal(v)), float(v) * 1000, rel_tol=1e-12)

	def test_as_a_method_of_a_temperature(self):
		assert float(Temperature.Celsius(25).vpd(60)) == float(uc.vpd(25, 60))
		assert float(Temperature.Fahrenheit(77).vpd(Humidity.fromPercent(60), 2)) == float(uc.vpd(Temperature.Fahrenheit(77), 60, 2))

	def test_cold_and_warm_air_at_the_same_humidity(self):
		assert float(uc.vpd(15, 60)) < float(uc.vpd(25, 60)) < float(uc.vpd(30, 60))
		assert str(uc.vpd(15, 60)) == '0.68 kPa'
