# Derived units: one number per unit, and a dimension algebra

**Status:** design; depends on [conversion-core.md](conversion-core.md) phase 1. Resolutions below marked "proposed" are not signed off.
**Base:** `dev` once the conversion core has landed. Step one: `git checkout -B feat/derived-algebra dev`.
**Model:** design-heavy. Phase 1 suits Sonnet once the open question is answered; phases 2 and 3 want Opus.

## Purpose

Easy, automatic conversion of values from any data API. Maintainer decisions, 2026-10-04:

- Arithmetic works within the same dimension, across systems.
- Dimension algebra: "ideally forever but fine with ^3".

## Problem 1: the denominator does two jobs

The maintainer raised this: "knowing when the denominator is implied, like 20mph is actually [20mi/1hr]". Probed on `dev` @ aa10d20:

| expression | result |
|---|---|
| `MilesPerHour(20)` | stores n=Mile(20), d=Hour(1) |
| `MilesPerHour(Mile(40), Hour(2))` | 20 mph, stores n=40 mi, d=2 h; `== MilesPerHour(20)` True |
| `MPH(Mile(40),Hour(2))['m/s']` | 8.9 m/s, stores n=Meter(64373.8), d=Second(7200). Conversion keeps the window |
| `MilesPerHour(MetersPerSecond(10))` | shows 22.4 mph but `.numerator` is Mile(0.0062), the distance in ONE SECOND |
| `MPH(Mile(40),Hour(2)) * 2` | 40 mph, n=40 mi, d=1 h. Arithmetic drops the window (`+` likewise) |
| `MPH(Mile(40),Hour(2)) ** 1` | **10 mph**. `__pow__` divides by the denominator twice (`base/_Measurement.py` ~839) |
| `Hourly(Millimeter(6), Hour(3))` | 2 mm/hr, keeps 6 mm/3 h; `.daily` gives 48 mm/d (correct as a rate) |
| `Hourly(6)` | TypeError "does not support int as numerator", yet `type(Hourly(Millimeter(6),Hour(3)))(6)` works |
| `wind.Wind(5)` | AttributeError: type object 'int' has no attribute 'id' |

LevityDash works around this in three places by rebuilding `valueCls(numerator=n(value), denominator=type(ref.d)(1))`. All in the sibling `../LevityDash` checkout:

- `src/LevityDash/lib/plugins/observation.py` ~739 and ~766 (the checks that trigger them are at ~735 and ~762);
- `src/LevityDash/lib/ui/frontends/PySide/Modules/Displays/Graph.py` ~928.

`lib/wire/codec.py` `decode_measurement` (~179) degrades derived values to a bare float when `cls(value)` fails.

The two jobs the denominator does:

- **The unit's denominator.** mph is miles per ONE hour. It belongs to the unit, like the "kilo" in km. Its magnitude is always 1, and it folds into the unit's factor (mph = 0.44704 m/s).
- **A window.** "6 mm fell in the last 3 h" is a fact about the observation, like its timestamp.

### Proposed resolution

- A derived value stores **one number in its unit**, like every measurement.
- `numerator` and `denominator` are **class-level** descriptions, used for naming, parsing `km/h`, building units and the algebra. On an instance, `.numerator` / `.denominator` return `value × numerator-unit` and `1 × denominator-unit`: always the implied 1.
- Every concrete derived class constructs from a bare number. A generic class (`Wind`) raises a clear `TypeError` asking for a unit.
- **Rate and accumulation are explicit arithmetic:** `Millimeter(6) / Hour(3)` gives 2 mm/h, and a rate times `Hour(3)` gives 6 mm.
- A value that must remember its window (rain in the last 24 h, a daily `precipitation_sum`) carries an optional `period` (`timedelta`) beside the existing `timestamp` metadata (`Measurement.__init__` takes title/key/timestamp/category). It is not a stored denominator, and conversion never touches it.

**Keep amount-over-interval as an input form.** `Hourly(Millimeter(1), Minute(5))` gives 12 mm/h and stays valid. It means "amount over interval, give me the rate". This is the real reason the (numerator, denominator) pair exists: schemas build `comboCls(value, period)` from "amount over the report interval" (`lib/plugins/categories.py` ~210-225, in `/home/user/LevityDash`; WeatherFlow `'sourceUnit': ['mm', '@period']`, `WeatherFlow/__init__.py` ~70-71). Only the stored magnitudes go.

**Closed: does anything read the window back? No** (researched 2026-10-04).

- Storing both values has been there since `4b4026b` (2021-02-08), the initial commit. No commit message mentions a window, accumulation or period.
- It is not recoverable today anyway: `Hourly(Millimeter(1), Minute(5))` is 12 mm/hr with `.n` = 1 mm and `.d` = 0.1 hr. The interval is rescaled into the class's denominator unit.
- LevityDash's only instance readers (`observation.py` ~737-738 and ~764-765, `Graph.py` ~927-928) use the classes and force a denominator of 1.
- Inside WeatherUnits, every reader (`rate.py`, `precipitation.py`, `__getitem__`, `localize`, `_convert`, `nArr`/`dArr`) converts units or reads `.unit`. None needs a magnitude other than the implied 1. The stored pair is how the first `localized` converted each part separately.

### The normalising hazard (document in the README)

API data reports rates and accumulations with the same number and different meanings. The class must say which one it is.

| quantity | rate | accumulation |
|---|---|---|
| precipitation | mm/h | mm |
| energy | kW | kWh |
| solar | W/m² | Wh/m² |
| light for plants | PPFD, µmol/m²/s | DLI, mol/m²/day |

### Follow-ups for LevityDash (list them, do not do them)

Once this lands, the three workarounds above become `valueCls(value)`, and the codec fallback in `decode_measurement` goes.

Also list, do not fix: these are accumulations typed as rates. Re-type them once accumulation types exist.

- WeatherFlow `precip_accum_local_day` (`WeatherFlow/__init__.py` ~73) is typed `precipitationDaily`, a daily rate, but it is a running total since midnight. `precip_accum_last_1hr` (~72) is the same shape.
- `calculateMissing` in commit `c2a3692` (2021-10-09) summed hourly rate observations into `precipitationAccumulation`, treating each rate sample as one hour.
- PirateWeather `precipAccumulation` is typed `precipitationRate` (`PirateWeather.py` ~41).

## Problem 2: no dimension algebra

Today:

| expression | result |
|---|---|
| `Meter(5) * Meter(5)` | Meter |
| `Celsius(5) ** 2` | Celsius |
| `Meter(10) / Meter(2)` | AttributeError |
| `-Celsius(5)`, `2 * Meter(10)`, `Meter(3) % 2` | plain floats |

The README roadmap (README.md ~385-391) already lists products (Pa·s), negative exponents (Hz) and multiple units in either part.

### Design

- Each dimension carries an **exponent vector** over the base dimensions L, M, T and Θ. Add I, N and J only when a unit needs them.
  - Length = L¹, Area = L², Speed = L¹T⁻¹, Pressure = M¹L⁻¹T⁻².
- `*` and `/` add or subtract the vectors and multiply the reference values. The result is already in the result dimension's reference unit (SI coherence).
- The result dimension is the registered named one (Area, Volume, Speed, Pressure, ...). If none matches, use a generic composite that still formats (`Pa·s`).
- A dimensionless result is a plain float (`Meter(10) / Meter(2)` gives `5.0`).
- Exponents −3 to +3 per base dimension, with a clear error beyond. Integer powers only.
- **Result unit:** if a registered unit matches the operands' unit combination (ft × ft gives ft²), use it. Otherwise return the reference unit. The caller can then localise.
- **Type preservation:** unary `-` and `+`, `abs`, scalar `*` and `/` on either side, `%`, `//` and `round` keep the class.

### Temperature: a reading is not a change (decided: maintainer, 2026-10-04)

Temperature separates a **reading** from a **change**.

| expression | result | why |
|---|---|---|
| reading − reading | change | `Celsius(30) - Celsius(20)` is a change of 10 °C, which equals a change of 18 °F. A change converts by factor only. |
| reading ± change | reading | `Fahrenheit(68) + Δ10°C` = 86 °F = 30 °C. Consistent across systems. |
| reading + reading | `TypeError` by default | `20 °C + 10 °C` = 30 °C, but `68 °F + 50 °F` = 118 °F, which is not 86 °F. Same temperatures, and the result depends on the unit. |

- An opt-in mode lets reading + reading add in the left operand's unit.
- The existing `delta` parameter on the temperature conversion methods is the unfinished start of this (`temperature/celsius.py` ~13-17, `fahrenheit.py` ~13-14).
- The change type needs a name and a class. The implementer chooses the spelling, e.g. `TemperatureDelta` or `Celsius.delta(10)`.
- Use cases: "+3° since yesterday", and min/max spreads.

## Phases

1. **Denominator split.** Construct from a bare number, class-level numerator/denominator, `period`, and the `__pow__` fix. Tests: every row of the first table.
2. **Exponent vectors and `*` / `/`.**
3. **Type-preserving operators.**
4. **Reading/change rule** for temperature, as decided above.

## Verify

1. Each probe row above becomes a test with the correct result in the right-hand column.
2. `Millimeter(6) / Hour(3)` gives `2 mm/h`; times `Hour(3)` gives `6 mm`.
3. `Meter(10) / Meter(2) == 5.0` and `isinstance(..., float)`.
4. Cross-system: `Foot(3) * Meter(1)` is an area equal to `0.9144 m²` within `isclose`.
5. From `../LevityDash`: `.venv/bin/python -m pytest -q`, with the three workarounds still in place (they must keep working until their own follow-up).

## Out of scope

- Parsing compound unit strings: [unit-parsing.md](unit-parsing.md).
- The LevityDash follow-ups above.

## Report

Per phase: commit, tests added, the spelling chosen for the temperature change type.
