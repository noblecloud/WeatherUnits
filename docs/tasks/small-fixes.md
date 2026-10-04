# Small fixes

**Status:** ready to pick up.
**Base:** `dev`. Step one: `git checkout -B fix/small dev`.
**Model:** Sonnet. Four independent items; one commit each, each with a test.

Pin the config first, as in [missing-values-and-locale.md](missing-values-and-locale.md) part 3, or write each test so it does not depend on the loaded config.

## 1. Kelvin's symbol is `'k'`, should be `'K'`

`temperature/kelvin.py` ~13: `_unit = 'k'`. `k` is the SI prefix kilo; the kelvin is `K`.

- Grep for users of the old spelling: `temperature/temperature.py` ~79 and ~85 compare `self._unit != 'k'`; `config/template.ini` ~21 says `kelvin (k)`; check the other `config/*.ini` and `tests/config.ini`.
- In `../LevityDash`, grep `.levity` files and `src/LevityDash/resources/example-config/` for the Kelvin symbol.
- Keep `'k'` working as an alias if the registry allows it, until [unit-parsing.md](unit-parsing.md) lands. Case-insensitive lookup may already do this; check.
- **Test:** `Kelvin(300).unit == 'K'` and `str(Kelvin(300))` ends in `K`.

## 2. `heatIndex` guard is wrong

`temperature/temperature.py` ~71:

```python
if 300 > self.kelvin < 318 or R < 13:
	return self
```

This reads as `300 > K and K < 318`, true for every temperature below 300 K, so the function returns early almost always. It should almost certainly be `300 < self.kelvin < 318` (300 K is about 26.85 °C, where the Rothfusz regression applies).

Check what the intent is before changing it. The upper bound at 318 K (~44.85 °C) also looks like it should not return early for hot days; read the branch and say what you decided.

- **Test against the NWS reference value:** 90 °F at 50% RH gives about 95 °F. Also assert that 60 °F at 50% RH returns the input unchanged.

## 3. `wu.auto(value, unit)` crashes

`__init__.py` ~54-82: the two-argument form iterates over the class `__findUnitClass__` returns, and fails for every unit. Minimal fix plus a test: `wu.auto(5, 'm')` is `Meter(5)`. The parsing brief replaces `auto` later, so keep this to the smallest change that works.

## 4. Add `py.typed`

There is no `py.typed` in `src/WeatherUnits/`. Add an empty one and include it in the build. `pyproject.toml` ~27 has `include = ["*.ini"]`; add `"py.typed"` to it, or confirm poetry picks it up from the package.

- **Test:** build a wheel and check it lists `WeatherUnits/py.typed`.

## Verify

`pytest -q` green; each item's test fails before its fix.

## Out of scope

Anything in the design briefs.

## Report

Per item: commit, and any surprise (especially the `heatIndex` bounds decision).
