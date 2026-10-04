# Same-dimension comparison and arithmetic regressed in `8f1ce65`

**Status:** open, actionable. Found 2026-10-04.
**Base:** `dev`. Step one: `git checkout -B fix/same-dimension dev`.
**Model:** a bounded fix with decided semantics. Sonnet is fine.

## Symptom

On every axis below, the behaviour on `801b513` (before the July commit) differs from the behaviour now. Probed with `WU_CONFIG_PATH=.../config/us.ini`. The old code ran under Python 3.11, since it predates the 3.13 fixes.

| expression | before `8f1ce65` | now | correct |
|---|---|---|---|
| `Meter(1) + Foot(1)` | `Meter(1.3 m)` | **`BadConversion`** | `1.3048 m` |
| `Celsius(0) == Fahrenheit(32)` | `True` | **`False`** | `True` |
| `Meter(1) == Foot(3.280839895)` | `True` | **`False`** | `True` |
| `Celsius(25) > Fahrenheit(70)` | `True` | **`False`** | `True` (25 °C = 77 °F) |
| `Kilometer(1) < Mile(1)` | `True` | **`False`** | `True` |
| `Mile(1) > Kilometer(1)` | `False` | `False` | `True`, broken in both |
| `Meter(1) < Foot(4)` | `False` | `False` | `True`, broken in both |
| `sorted([Fahrenheit(40), Celsius(1), Kelvin(270)])` | K, C, F ✅ | **C, F, K** | K, C, F |
| `MetersPerSecond(10) > MilesPerHour(20)` | | **`False`** | `True` (22.4 mph) |
| `Meter(10) / Meter(2)` | `Meter(5 m)` | **`AttributeError`** | `5.0`, dimensionless |
| `Celsius(20) == Celsius(20.09)` | `True` | `True` | `False`; see "Semantics" below |
| `hash(Celsius(20)) == hash(Celsius(20.05))` while `==` says True | | `False` | they must agree |

## Cause

Three separate faults, all in `base/_Measurement.py` and `base/_ScalingMeasurement.py`.

1. **`self.type` is used as if it were the dimension.** For scaling units, `.type` is the *system* family: `Meter.type` is `MetricLength`, while `Foot.type` is `ImperialLength`. The dimension is `.dimension` (`Length`).
   - `__wrapOther` and `__prepareValues` test `isinstance(other, self.type)`. So a foot is "not the same dimension" as a metre.
   - In arithmetic, the dimensionality guard then raises `BadConversion`.
   - In comparisons, the `except` swallows that error and returns `False`.
2. **`_comparableValue` uses each system's own base.** `ScalingMeasurement._comparableValue` is `changeScale(self._Scale.Base)`, so a metre compares as metres and a foot as feet.
3. **Temperature has no comparable value at all.** It falls back to `float(self)`, so `Celsius(0)` and `Fahrenheit(32)` are compared as `0` vs `32`.

## Semantics (decided by the maintainer, 2026-10-04)

- **Equality compares the actual value, not the displayed one.** Exact, after both sides are converted into one unit of their dimension.
  - Exact cannot mean bit-identical across units: `Foot(Meter(1))` round-trips with float noise. So use `math.isclose(a, b, rel_tol=1e-9, abs_tol=0)`, after converting into a common unit. Use the left operand's unit for now; a later redesign moves to a per-dimension reference unit, see `unit-definition-v2.md` once it exists.
  - Remove the `abs(selfVal - other) < 1e-1` tolerance, and the rounding to `valuePrecision` in `__prepareValues`.
- **`__hash__` must agree with `__eq__`.** Hash the value converted to a per-dimension canonical unit, rounded to ~9 significant digits (`float(f'{v:.9g}')`).
  - A `isclose` relation is not transitive, so a pair exactly at the rounding boundary could still disagree. Note that in a comment rather than pretending otherwise.
- **The display comparison is configurable** but not the default:
  - add a `displays_same(other) -> bool` method: true when both format to the same string under their own config, after converting `other` into `self`'s unit;
  - its job is answering "does this readout need repainting?";
  - the name is provisional; check `docs/tasks/README.md` for a maintainer decision before shipping it.
- **Arithmetic works within a dimension, across systems and units.** Convert `other` into `self`'s unit, operate, and return `self`'s type.
  - Different dimensions still raise `BadConversion`.
  - Comparing different dimensions returns `False` for `==` and raises `TypeError` for ordering. That is Python's own contract for unorderable types, and the current silent `False` from `<` makes `sorted()` lie.
- **`Measurement / Measurement` of the same dimension is a dimensionless float.** Once the algebra work lands it becomes a `Dimensionless` value.

## Expected change

- Replace the `self.type` "same dimension" checks with `self.dimension` / `other.dimension`, in:
  - `__wrapOther`;
  - `__prepareValues`;
  - `_convert`;
  - and anywhere else `grep -n "self.type" base/_Measurement.py` finds the same intent.
- Convert `other` into `self`'s unit with `type(self)(other)` or `other[self.unit]` (`__getitem__`). Both already handle the bridge between systems.
- Delete `_comparableValue`, or turn it into the per-dimension canonical value used by `__hash__`. Do not keep two notions.
- Derived units: compare their converted values the same way. `MetersPerSecond(10)` vs `MilesPerHour(20)` converts the right-hand side through `[self.unit]`.

## Verify

1. Add `tests/test_same_dimension.py` with every row of the table above as an assertion, plus:
   - `len({Meter(1), Centimeter(100), Millimeter(1000)}) == 1`;
   - `Celsius(20) != Celsius(20.05)` and `Celsius(20).displays_same(Celsius(20.05))`.
2. **Write those tests first and watch them fail.** The "before" column is the evidence.
3. `pytest -q` with the locale-independent config (see [missing-values-and-locale.md](missing-values-and-locale.md) part 3, if that has landed).
4. Check LevityDash is not relying on the old tolerance. From `../LevityDash`, run `grep -rn "== \| != " src/LevityDash/lib/plugins | grep -i "value\|measurement"` and read each hit.
   - The place most likely to care is observation de-duplication.
   - If something relies on display-level equality, switch it to `displays_same` in the same change, and say so in the commit.

## Not in scope

- The reference-unit redesign (one SI reference per dimension; every unit carries `to_reference`/`from_reference`). That is the right long-term home for comparison, and it supersedes the "left operand's unit" choice above. Do the minimal fix first, so LevityDash stops sorting temperatures wrong now.
- Operators that drop the unit: `-Celsius(5)` and `2 * Meter(10)` return plain floats, and `Meter(3) % 2` does too. These are covered in the algebra brief.
