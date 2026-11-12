# Strict unit parsing

**Status:** phase 1 done on `feat/strict-parse` (2026-11-12); phases 2 and 3 open. The strict-lookup half is built. The compound-unit half waits on [derived-units-and-algebra.md](derived-units-and-algebra.md).
**Base:** `dev`. Step one: `git checkout -B feat/unit-parsing dev`.
**Model:** Sonnet for the lookup half. The compound half is design work.

## Purpose

Normalising values from data APIs means reading unit strings you did not choose. A wrong guess is worse than an error: a value shown in the wrong unit looks fine. So parsing must be strict and must fail loudly.

The strict parser's structured errors (`UnknownUnit` with candidates) are also the hook a unit-guessing layer could use later. That is parked; do not build it here.

## Problems (probed on `dev` @ aa10d20)

- `uc.auto(value, unit)` crashes for every unit. It iterates over the class `__findUnitClass__` returns (`__init__.py` ~54-82).
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
- `uc.auto('5 X')` fails for `°C`, `°F`, `kn`, `kt`, `kWh`, `W`, `h`, `°` and `deg`.
- Compound units (`km/h`, `m/s`, `W/m²`, `µg/m³`, `mm/h`) raise `NotImplementedError`.

## Design

- `uc.parse('10 m/s')` and `uc.parse(10, 'm/s')` are **strict**: exact symbol, alias or name.
  - Case-sensitive where it matters: `K` vs `k`, `mm` vs `Mm`.
  - Unicode normalisation: `µ`/`μ`/`u`, `²`/`^2`/`2`, `°`, `·`/`*`.
- Lookup is **scoped by dimension** when one is known (`Length` + `'m'` gives Meter). `Time` + `'m'` is *not* Minute: see the correction under "Phase 1 done".
- Unknown or ambiguous input raises `UnknownUnit` / `AmbiguousUnit`, carrying the candidates.
- **Fuzzy suggestions only via an explicit `uc.suggest('degC')`**, which returns a ranked list and never auto-picks.
- Aliases are declared on the class (see [conversion-core.md](conversion-core.md) phase 2). A collision raises at class creation, so the test import catches it.
- **Compound units** parse via the algebra. Until then, register the common compound symbols as aliases.
- `w['km/h']` uses the same parser.
- `uc.auto` becomes a thin wrapper over `uc.parse`, or is deprecated. Decide when you get there, and say which.

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

## Phase 1 done: what was built and decided

`uc.lookup(unit, dimension=None) -> class`, `uc.parse(text | value, unit, dimension=None) -> instance`, `uc.suggest(text, dimension=None, n=5) -> list of unit classes`, and `uc.UnknownUnit` / `uc.AmbiguousUnit` (`ValueError` and `LookupError`; `.unit`, `.candidates`). Code in `src/unitcorn/strict.py`, errors in `errors/Lookup.py`, tests in `tests/test_parse.py`, Home Assistant strings in `tests/fixtures/home_assistant_units.txt` (fetched 2026-10-23).

- Order: normalise, exact symbol or alias, name, then case-insensitive only if one dimension matches. The fold is refused for one character (`k` is not Kelvin) and for `m` against `M` unless the whole text is capitals (`KM` is the kilometer, `mW` and `Mm` raise).
- Spellings are declared on classes: `_parse_aliases` and `_parse_scoped` (spellings valid only with a `dimension`: `C`, `F`, `%` for PartsPer). Own `__dict__` only, never inherited. `%` is Percentage; `degC`, `°C` and `deg C` are one spelling.
- `m` is Meter, Minute or Month and raises `AmbiguousUnit`, scoped to `Time` too. **Correction:** the first version of this phase (and this doc's design section) had `Time` + `'m'` give Minute. Home Assistant's `UnitOfTime.MONTHS` is `m`, so that would silently turn a month reading into minutes, which strict parsing exists to prevent. `min`/`mins` are Minute, `mth`/`mo`/`month` are Month. Same-dimension classes that share a spelling and are not subclasses of each other are different units, hence ambiguous; only related classes (Wind and Rate `mph`) are duplicates.
- Generated plural symbols (`ms` for Meter, `ts`, `cs`) are not accepted. Plural names are.
- Same-dimension duplicates (Wind and Rate `mph`) are not ambiguous: a unit whose own type is the requested dimension, else the most derived class; unrelated classes are ambiguous.
- Compounds: direct symbol first (`m/s`, `W/m²`, `BTU/h`), else one `/` splits and the sides divide through the algebra. A float, a catch-all `Compound` or identical sides (`m/m`) is refused, so `g/m`, `m³`-based units and `µg/m³` raise `UnknownUnit`. With a derived `dimension` (`uc.Wind`) the dimension builds the class.
- `parse` of a percentage passes `isPercentage=True`.
- Not done: `__findUnitClass__`, `auto()` and `__getitem__` are untouched (their fuzzy fallback is still there, and `wind['km/h']` is still wrong), so the doc's "remove the fuzzy fallback" and "`w['km/h']` uses the same parser" are for a later step. `UnknownUnit` moved to `errors/Lookup.py` and now subclasses `ValueError`; its old `(measurement, unit)` call still works.
- Home Assistant: 182 strings, 72 parse, 108 raise `UnknownUnit`, 2 raise `AmbiguousUnit` (`m`, once for length and once for time).
