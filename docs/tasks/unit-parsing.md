# Strict unit parsing

**Status:** design. The strict-lookup half can start now. The compound-unit half waits on [derived-units-and-algebra.md](derived-units-and-algebra.md).
**Base:** `dev`. Step one: `git checkout -B feat/unit-parsing dev`.
**Model:** Sonnet for the lookup half. The compound half is design work.

## Purpose

Normalising values from data APIs means reading unit strings you did not choose. A wrong guess is worse than an error: a value shown in the wrong unit looks fine. So parsing must be strict and must fail loudly.

The strict parser's structured errors (`UnknownUnit` with candidates) are also the hook a unit-guessing layer could use later. That is parked; do not build it here.

## Problems (probed on `dev` @ aa10d20)

- `wu.auto(value, unit)` crashes for every unit. It iterates over the class `__findUnitClass__` returns (`__init__.py` ~54-82).
- The registry is global and unscoped. `Minute.__findUnitClass__('m')` returns Meter.
- Symbol collisions:
  - `'ms'`: Meter plural vs Millisecond;
  - `'ts'`;
  - Wind and DistanceOverTime both register `'mph'`.
- The fuzzy fallback (`difflib.get_close_matches`, cutoff 0.7) silently picks a unit:

| input | silently becomes |
|---|---|
| `degC` | Decade |
| `%` | Hundred (PartsPer) |

- `wind.MetersPerSecond(10)['km/h']` gives 0.01 km/s, a wrong unit. `['kn']` returns m/s unchanged, with no error.
- `wu.auto('5 X')` fails for `°C`, `°F`, `kn`, `kt`, `kWh`, `W`, `h`, `°` and `deg`.
- Compound units (`km/h`, `m/s`, `W/m²`, `µg/m³`, `mm/h`) raise `NotImplementedError`.

## Design

- `wu.parse('10 m/s')` and `wu.parse(10, 'm/s')` are **strict**: exact symbol, alias or name.
  - Case-sensitive where it matters: `K` vs `k`, `mm` vs `Mm`.
  - Unicode normalisation: `µ`/`μ`/`u`, `²`/`^2`/`2`, `°`, `·`/`*`.
- Lookup is **scoped by dimension** when one is known (`Time` + `'m'` gives Minute).
- Unknown or ambiguous input raises `UnknownUnit` / `AmbiguousUnit`, carrying the candidates.
- **Fuzzy suggestions only via an explicit `wu.suggest('degC')`**, which returns a ranked list and never auto-picks.
- Aliases are declared on the class (see [conversion-core.md](conversion-core.md) phase 2). A collision raises at class creation, so the test import catches it.
- **Compound units** parse via the algebra. Until then, register the common compound symbols as aliases.
- `w['km/h']` uses the same parser.
- `wu.auto` becomes a thin wrapper over `wu.parse`, or is deprecated. Decide when you get there, and say which.

## Phases

1. **Strict lookup:** normalisation, scoped registry, the two errors, `suggest`. Remove the fuzzy fallback from `__findUnitClass__`.
2. **Collision check at class creation.** Fix each collision it finds by choosing a winner per dimension, not by renaming symbols.
3. **Compound units** via the algebra.

## Verify

A fixture list that every string above runs through, plus Home Assistant's unit strings.

- HA's are listed in the `UnitOf*` enums in `homeassistant/const.py`. Fetch the current list at implementation time; do not copy from memory.
- Each fixture row is one of: parses to class X, raises `UnknownUnit`, raises `AmbiguousUnit`. No row may fall back silently.
- `degC` and `%` must no longer resolve to Decade and Hundred. `%` should resolve to the percent unit; `degC` should be an alias of Celsius.

## Out of scope

- Guessing units from context, and generating schemas. Parked.
- The Home Assistant `device_class` mapping. That belongs in LevityDash; see [ideas.md](ideas.md).

## Report

The fixture table with the outcome per row, and the list of collisions the class-creation check found.
