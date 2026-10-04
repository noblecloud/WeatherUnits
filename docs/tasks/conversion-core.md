# One conversion path: a reference unit per dimension

**Status:** design. Phase 0 is ready. Get sign-off on the declaration spelling (below) before building past phase 1.
**Base:** `dev`. Step one: `git checkout -B feat/conversion-core dev`.
**Model:** phase 0 and the phase 2 migration suit Sonnet. Phase 1 is the design-heavy one.

## Purpose

WeatherUnits exists for easy, automatic conversion of values from data APIs, to normalise and humanise them. Any data API, not just weather. Two decisions follow from that, both made by the maintainer on 2026-10-04:

- Defining a unit should be a class declaration. Everything else should be automatic.
- Conversion is "convoluted" today. This brief fixes that.

## Problem: four conversion paths

| dimension | how it converts | where |
|---|---|---|
| Pressure | one base (Pascal) plus a `_Scale` enum. **This is the good model.** | `pressure/pressure.py` ~29 |
| Length, mass | two bases per dimension (Meter/Foot, Gram/Pound), each with its own `_Scale`. Bridge methods `_foot()`, `_meter()`, `_pound()`, `_gram()` cross systems. | `length/metric.py` ~21, `length/imperial.py` ~19, `mass/metric.py` ~20, `mass/imperial.py` ~20 |
| Temperature | pairwise `_celsius/_fahrenheit/_kelvin` methods on each class, plus `Temperature._convert`. n units need n² methods. | `temperature/celsius.py`, `fahrenheit.py`, `kelvin.py`; `temperature/temperature.py` ~114 |
| Time | its own `_convert` | `time_/time.py` ~150 |

On top of those sits a fourth layer, `_conversionParams(toUnit, fromUnit)` (`base/_Measurement.py` ~26, used by `convert_array` ~95). It runs 0 and 1 through the paths above and caches a factor and offset. It is the source of float noise: 32 °F converts to 4.97e-14 °C.

Comparisons use yet another path, `_comparableValue` per system (`base/_Measurement.py` ~247; see [same-dimension-regressions.md](same-dimension-regressions.md)).

`Mile(Kilometer(1))` goes km → m → bridge → ft → mi. Four steps, each with rounding.

The README's own "Defining Your Own Unit" section (README.md ~172-230) shows the boilerplate cost: a property per target unit on the dimension class, and an identity converter (`def _celsius(self): return self`) on every unit, "to prevent errors".

## Design

- **One reference unit per dimension: the SI coherent unit** (m, kg, s, K, Pa, m/s, ...).
  - Why SI: it is coherent. Products and quotients of reference units are already the reference unit of the result (m × m = m², kg·m⁻¹·s⁻² = Pa). So the algebra brief needs no conversion tables.
  - The reference is internal only. Display and localisation are unaffected.
- **Every unit has `to_reference(x)` and `from_reference(x)`.**
  - The default is affine: `ref = (x + offset) * factor` and `x = ref / factor - offset`.
  - Non-linear units (Beaufort, dB, AQI) override both functions. That is the escape hatch.
- **Conversion is always source → reference → target.** That deletes the bridges, the pairwise temperature methods and `_conversionParams`.
- **`_Scale` enums stay as declaration syntax.** The metaclass derives each member's factor from the chain, plus ONE declared cross-system equivalence on the system base (1 ft = 0.3048 m exactly).
- **Comparison and hash use the reference value.** The minimal fix in `same-dimension-regressions.md` can land first, as a stepping stone. This supersedes its "left operand's unit" choice.
  - Equality: `math.isclose(rel_tol=1e-9)` on reference values.
  - Hash: the reference value rounded to ~9 significant digits.
  - `displays_same()` (name provisional) stays a display-level check.
- **Generated accessors** (`.kmh`, `.fahrenheit`, `['km/h']`) come from the registry. No hand-written property per target.

### Proposed declaration spelling (not signed off)

Present this to the maintainer before migrating every unit.

```python
class Kelvin(Temperature, unit='K', reference=True): ...
class Celsius(Temperature, unit='°C', offset=273.15, aliases=('c', 'degC')): ...
class Fahrenheit(Temperature, unit='°F', offset=459.67, factor=5/9, aliases=('f', 'degF')): ...
# reference = (value + offset) * factor

class ImperialLength(ScalingMeasurement, Length, system=imperial, baseUnit='Foot', equals=Meter(0.3048)): ...
class Knot(Speed, unit='kn', aliases=('kt',), equals=NauticalMile / Hour): ...
```

The last line needs the algebra from [derived-units-and-algebra.md](derived-units-and-algebra.md). Until then, spell a knot as `factor=1852/3600`.

## Phases

### Phase 0: characterization tests

For every unit pair within each dimension, convert 0, 1, 21.5, -40 and 1e6. Assert against **physical constants, not against current output**. Current cross-system output is partly wrong.

| constant | value |
|---|---|
| 1 ft | 0.3048 m |
| 1 lb | 0.45359237 kg |
| 1 mi | 1609.344 m |
| 1 inHg | 3386.389 Pa |
| 1 mph | 0.44704 m/s |
| 1 kn | 1852/3600 m/s |
| temperature | the °C / °F / K formulas |

Conversions must not depend on the loaded config. Pin it as described in [missing-values-and-locale.md](missing-values-and-locale.md) part 3. Tests that fail today are expected; mark them `xfail(strict=True)` with the reason, so phase 1 flips them.

### Phase 1: the reference core behind the existing API

- Compute to/from reference per class from the existing declarations.
- Route `_convert`, `__getitem__`, `convert_array` and comparisons through it.
- Delete the bridges, the pairwise methods and `_conversionParams`.
- No user-visible changes to class definitions.
- The phase 0 tests and the existing suite must both be green. `convert_array(32 °F → °C)` gives exactly 0.

### Phase 2: declaration keywords and generated accessors

- Add the keywords (`reference=`, `offset=`, `factor=`, `equals=`, `aliases=`) and the generated accessors.
- Migrate the built-in units. Delete the redundant hand-written properties.
- Rewrite the README's unit-definition section around the new spelling.

## Verify

1. Phase 0 tests green on `dev`'s physical-constants rows that already pass; the rest `xfail(strict=True)` until phase 1.
2. After phase 1: no `xfail` left, `pytest -q` green under both `LANG=C.UTF-8` and `us.ini`.
3. `git grep -n "_conversionParams\|_foot\|_meter\|_pound\|_gram"` returns nothing.
4. From `../LevityDash`: `.venv/bin/python -m pytest -q`. LevityDash path-depends on this checkout.

## Out of scope

- Derived units and algebra: [derived-units-and-algebra.md](derived-units-and-algebra.md).
- Parsing: [unit-parsing.md](unit-parsing.md).

## Report

The commit per phase, the phase 0 pass/xfail counts, and any unit whose declared factor disagreed with the physical constant.
