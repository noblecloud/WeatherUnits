import pytest

from WeatherUnits import others


@pytest.mark.parametrize('cls', [others.Humidity, others.Probability, others.Coverage, others.Percentage])
class TestPercentageScale:
	def test_percent_scale_keeps_sub_one_values_small(self, cls):
		assert float(cls(0.1, isPercentage=True)) == pytest.approx(0.001)

	def test_percent_scale_one_is_one_percent(self, cls):
		assert float(cls(1, isPercentage=True)) == pytest.approx(0.01)
		assert float(cls(1.0, isPercentage=True)) == pytest.approx(0.01)

	def test_fraction_scale(self, cls):
		assert float(cls(0.1, isPercentage=False)) == pytest.approx(0.1)
		assert float(cls.fromFraction(1.0)) == pytest.approx(1.0)

	def test_percent_scale_regular_values(self, cls):
		assert float(cls(55, isPercentage=True)) == pytest.approx(0.55)
		assert float(cls(100, isPercentage=True)) == pytest.approx(1.0)

	def test_unspecified_scale_still_guesses_for_literals(self, cls):
		assert float(cls(66)) == pytest.approx(0.66)
		assert float(cls(0.5)) == pytest.approx(0.5)


def test_sub_one_percent_is_not_shown_as_ten():
	shown = str(others.Percentage.fromPercent(0.1))
	assert shown.startswith('0.1') and not shown.startswith('10')
