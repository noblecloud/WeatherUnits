# Missing values, and everything the host locale silently decides

**Status:** open, actionable. Found 2026-10-04.
**Base:** `dev`. Step one: `git checkout -B fix/missing-and-locale dev`.
**Model:** Sonnet. Three independent parts; one commit each.

WeatherUnits exists to normalise values from data APIs, and APIs send gaps. Every part below is a way the library misreports a gap, or misbehaves depending on the machine it runs on.

## 1. NaN becomes the upper limit

`Measurement.__new__` (`base/_Measurement.py` ~54) clamps with:

```python
value = sorted((*cls.limits, float(value)))[1]
```

Sorting with a NaN in it is undefined, and in practice NaN lands on the upper limit:

| input | result |
|---|---|
| `Humidity(float('nan'))` | **`Humidity(100%)`**: a missing reading shows as saturated |
| `Celsius(float('nan'))` | **`Celsius(inf°)`** |
| `Celsius(None)` | `TypeError` |

This has been there since 2022 (`ed8b4241`). It is not a July regression.

**Expected:**
- NaN passes through as NaN, unclamped.
- `None` becomes NaN. `SmartFloat.noneToNan` already exists for exactly this, but nothing calls it on construction.
- A NaN value formats as a placeholder: an em dash, or whatever `[UnitDefaults]` names, e.g. `missing = —`.
- `__bool__` on NaN is `False`. Check what it is now.

**Before changing the placeholder,** grep `../LevityDash/src` for how LevityDash detects missing values (`isnan`, `valueUnset`, `'⋯'`). The gauge renders `⋯` for `None`, and the two should agree.

## 2. Negative zero

`str(Celsius(-0.04))` gives `'-0°'`. A value that rounds to zero at the display precision should not keep its sign. Fix it in the formatting path (`base/_SmartFloat.py`, `__format__`), and add it to `tests/test_formatting.py`.

## 3. The locale decides the config, and can crash the import

`Config.__init__` (`config/__init__.py` ~25-40) picks the default config from the locale:

```python
path = 'us.ini' if (self.locale.lower().endswith('us') or 'United States' in self.locale) else 'si.ini'
```

**a. Import crash.** If `locale.getlocale()[0]` is `None`, the import dies:

```
$ LANG=en_US.UTF-8 python -c "import WeatherUnits"   # en_US not installed on the host
AttributeError: 'NoneType' object has no attribute 'lower'
```

That happens with an unset `LANG`, an uninstalled locale, or some containers. A library must never fail to import because of the host's locale. Fall back to `si.ini` and log at debug level.

**b. The test suite's result depends on the machine.** No test pins a config, so:

| host locale | config loaded | result on `dev` (2026-10-04) |
|---|---|---|
| `C.UTF-8` (CI, containers) | `si.ini` | 142 pass, 1 fail |
| `en_US` (the maintainer's Mac, presumably) | `us.ini` | **19 fail** |
| `WU_CONFIG_PATH=tests/config.ini` | `tests/config.ini` | 14 fail |

Reproduce: `WU_CONFIG_PATH=$PWD/src/WeatherUnits/config/us.ini pytest -q`.

**Expected:**
- **Pin the config for the suite** in a `tests/conftest.py` that sets `WU_CONFIG_PATH` *before* the first `import WeatherUnits`. The config is read at import time, in a class body, so later is too late.
- **Pick one config deliberately and say why.** `tests/config.ini` exists, but it has drifted from `us.ini` (diff them: `wind = mi/hraust` looks like a typo, and `[Units]` vs `[LocalUnits]` look like stale section names).
  - Do not just point the suite at whichever config makes it green.
  - For each test that fails under the chosen config, read what it asserts. Decide whether the test, the config or the library is wrong, and say which in the commit.
- **Make the tests that really are about a locale pin their own.** `test_defaults_come_from_the_locale` (`tests/test_string_api.py`) fails in any container because the US separators are unavailable. It should set and restore the locale itself, or skip with a reason when the locale is not installed.
- **CI:** `.github/workflows/tests.yml` tests 3.10-3.13, but the classifiers claim 3.14. Add 3.14, and run the suite once under `LANG=C.UTF-8` and once with `us.ini` pinned. That way a locale-dependent test can't hide again.

## Verify

```bash
LANG=C.UTF-8 pytest -q
WU_CONFIG_PATH=$PWD/src/WeatherUnits/config/us.ini pytest -q   # same result as the line above
LANG=xx_XX.UTF-8 python -c "import WeatherUnits"               # imports, no traceback
python -c "from WeatherUnits.others import Humidity; print(repr(Humidity(float('nan'))))"   # not 100%
```

Then from `../LevityDash`: `.venv/bin/python -m pytest -q`. LevityDash path-depends on this checkout, so any formatting change shows up there.
