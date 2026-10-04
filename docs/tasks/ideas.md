# Ideas

**Status:** backlog. The maintainer prioritises; nothing here is scheduled.

A few lines each. Turn one into a proper brief when it is picked up.

The purpose, for judging what belongs: easy, automatic conversion for normalising and humanising values from any data API.

## Speed

- Knots (`kn` / `kt`).
- Beaufort. Non-linear, so it exercises the escape hatch in [conversion-core.md](conversion-core.md) (overridden `to_reference` / `from_reference`).

## Light and energy

- Irradiance W/m² and insolation Wh/m². An accumulation pair; see the rate/accumulation hazard in [derived-units-and-algebra.md](derived-units-and-algebra.md).
- W / kW, and Wh / kWh, as used by Home Assistant energy dashboards.

## Plant and grow

The maintainer grows carnivorous plants and does tissue culture.

- PPFD (µmol/m²/s) and DLI (mol/m²/day). DLI = PPFD × photoperiod, so a rate/accumulation pair.
- VPD in kPa, computed from temperature and RH like dew point and heat index.
- EC in mS/cm or µS/cm, and TDS in ppm. TDS uses a 0.5 / 0.64 / 0.7 conversion factor, so it is an assumption-carrying value, not a pure unit conversion. The factor must be explicit.

## Home Assistant normalisation

HA states carry `unit_of_measurement` and `device_class`. A LevityDash HA backend is "strict-parse the unit, then map `device_class` to a LevityDash key".

- The `device_class` table lives in LevityDash.
- WeatherUnits' job is that every HA unit string parses. That is the fixture in [unit-parsing.md](unit-parsing.md).

## Serialisation

`Measurement.to_dict()` / `from_dict()`: unit symbol, value, optional timestamp and period.

LevityDash's `lib/wire/codec.py` then stops regex-parsing generated class names (`_PARAMETRIZED_CLS`, ~77) and stops degrading derived values to float (`decode_measurement`, ~179).

## Volume

Restore or delete the commented-out `CubicMeter` / `CubicFoot` in `derived/volume.py` (~85-96), after the conversion core lands. The declared `dimension=(Length, Length, Length)` is the algebra's job.

## Parked (context only)

LLM unit guessing and LLM schema generation are long-term goals. The strict parser's structured errors are the hook a guessing layer could use later.
