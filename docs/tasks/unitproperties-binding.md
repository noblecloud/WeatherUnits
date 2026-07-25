# `[UnitProperties]` keys silently never bind for unit symbols

> ✅ **RESOLVED 2026-07-25.** Kept as the record of what was wrong and what
> changed. Lookup is now exact, case-insensitive, and covers both the class
> name and the class's own `_unit`; a refit now carries the target unit's
> config with it. Verified against a 264-row render snapshot: 10 rows
> changed, all `MillimeterOfMercury` under the default `si.ini`. With
> LevityDash's config the effect is its `inHg` line finally applying, so a
> pressure readout renders `29.90 / 30.00 / 30.10` instead of
> `29.9 / 30 / 30.1`.

**Found:** 2026-07-25, while checking whether `trailing_zeros` could be set
from a config file. It could not — and neither could `precision` or
`digit_budget`, for any unit whose config key is a unit *symbol*.

## Symptom

`config/us.ini` ships:

```ini
[UnitProperties]
inHg = precision=2, digit_budget=4, trailing_zeros=precision
```

and `si.ini` ships the equivalent for `mmHg`. Neither reaches the class:

```python
>>> from WeatherUnits import Pressure
>>> m = Pressure.MillimeterOfMercury(760.0)
>>> m._precision, m._digit_budget      # config says 2 and 5
(1, 3)
```

The values come from `[UnitDefaults]` instead. No warning is emitted; the
line reads as if it works.

## Cause

Two binding paths, and both miss.

**1. The metaclass path** (`base/_SmartFloat.py:338`) is the one that
actually runs at class creation:

```python
if name.lower() in config.unitPropertiesKeys:
```

`name` is the **class name**. `MillimeterOfMercury`.lower() is
`'millimeterofmercury'`, which never matches the key `mmHg`. Keys that
happen to coincide with a class or type name — `temperature`, `direction`,
`humidity`, `illuminance` — do bind, which is why the section looks like it
works.

**2. The `setPropertiesFromConfig` path** (`utils.py:131`) *does* check
`cls._unit`, so it would match `mmHg`. But its only caller is
`config/__init__.py:68`:

```python
for k, v in self.configuredUnits.copy().items():
    setPropertiesFromConfig(v, self)
```

`configuredUnits` is populated **by `setPropertiesFromConfig` itself**. On
first load it is empty, so the loop body never executes. It can only ever
re-apply config to classes that were already configured — and nothing ever
configures them the first time.

## Expected change

Make per-unit keys bind by unit symbol as well as class name. The candidate
list already exists and is correct in `setPropertiesFromConfig`:

```python
possibleNames = [cls.__name__.lower(), cls._unit, toCamelCase(cls.__name__), cls.__name__]
```

The metaclass check needs the same set, matched case-insensitively
(`unitPropertiesKeys` already lowercases, so the *lookup* must lowercase
too — `config.unitProperties['inHg']` is a `KeyError` today because the
stored key case is preserved while the membership set is not).

Worth deciding at the same time whether the dead `setPropertiesFromConfig`
path should be repaired or deleted; keeping two mechanisms that disagree
about which names are valid is how this got missed.

## ⚠️ This will change rendered output

Fixing it *activates* config lines that have been inert since they were
written. Expect at minimum:

- `inHg` gains `precision=2, digit_budget=4, trailing_zeros=precision`,
  so a pressure readout becomes `30.00 inHg` rather than `30 inHg`
- `mmHg` gains `precision=2, digit_budget=5`

That is presumably what the config author intended — but it is a visible
change to every downstream display, so it wants to land deliberately and
with the author's sign-off, not as a side effect.

LevityDash's own `example-config/config.ini` carries the same `inHg` and
`mmHg` lines, so both repos change together.

## Verification

- `Pressure.MillimeterOfMercury(760.0)._precision == 2`
- the full formatting behaviour matrix, diffed before/after — the diff
  should contain *only* units whose config keys are unit symbols
- both suites, and a LevityDash screenshot check on a pressure panel

## Suggested branch

`fix/unitproperties-symbol-binding`
