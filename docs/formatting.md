# Formatting reference

How a measurement becomes a string.

> **This doc is also a spec.** Where current behavior differs from what was
> clearly intended, both are stated and the gap is marked
> **⚠️ NOT IMPLEMENTED** or **🐛 BUG**. Correct this document toward the
> intended behavior and it becomes the work list.
>
> Every example below was executed against the library; the outputs are
> pasted, not predicted. They reflect the **US config** (`config/us.ini`) —
> some defaults, notably `shorten`, differ under `si.ini`.

---

## Quick start

```python
>>> from WeatherUnits import Wind, Temperature
>>> speed = Wind.MilesPerHour(4.1)

>>> f'{speed}'                  # class defaults
'4.1 mph'
>>> f'{speed:showUnit=False}'   # a parameter
'4.1'
>>> f'{speed:ms}'               # a conversion
'0.0 mi/ms'
```

Two convenience properties wrap the common cases:

```python
>>> Temperature.Celsius(0).withUnit      # force the unit on
'0ºc'
>>> Temperature.Celsius(0).withoutUnit   # force it off
'0º'
```

---

## The format-spec mini-language

A spec is up to three things, **always parsed in this order**:

```
{value:  <conversion>  :  <float-spec>  ,  <key>=<value>, <key>=<value>  }
             │                │                      │
             │                │                      └─ parameters, comma-space separated
             │                └─ a standard Python float spec (.2f, >8, +)
             └─ a target unit (mph, km/hr, auto)
```

All three parts are optional:

| Spec | Meaning |
|---|---|
| `''` | class defaults |
| `.2f` | float spec only |
| `mph` | conversion only |
| `mph:.2f` | conversion + float spec |
| `showUnit=False` | one parameter |
| `precision=2, max=5` | several parameters |

Parameters accept **either separator** — `key=value` or `key: value`. They
are equivalent *for ordinary word values*; see the [`:` caveat](#the--caveat)
for the exception.

---

## Order of operations

This ordering is the source of nearly every surprise in the system, so it is
worth internalizing. `__format__` (`base/_SmartFloat.py`) does:

1. **Conversion is claimed first.** `FormatSpec.conversion` is anchored to
   the start of the spec. If the leading token names a compatible unit it is
   *removed* from the spec before anything else looks at it.
2. **The float spec is claimed second.** `FormatSpec.precision` matches at
   the start or immediately after a `:`, and slices its match out.
3. **Parameters are parsed last**, from whatever text survives steps 1–2.

So by the time `key=value` parsing runs, two other regexes have already
eaten part of the string. In `mph:.2f`, `mph:` is gone before the float spec
is read, and `.2f` is gone before parameters are read.

### Precedence

Resolved values are layered (highest priority first):

```
float-spec groups  →  template's own {value:…}  →  extras  →  spec parameters
   →  class defaults (defaultFormatParams)  →  dict-spec params  →  self.__dict__
```

Practical consequence: **a spec parameter beats the config file**, and an
explicit float spec beats both.

### The `:` caveat

Because the float spec is claimed *before* parameters (step 2), a
`key: value` pair whose **value looks like a float spec** is swallowed:

```python
>>> from WeatherUnits import Length
>>> i = Length.Inch(51)
>>> f'{i:unitSpacer=_}'    # '=' → parsed as a parameter
'51_in'
>>> f'{i:unitSpacer: _}'   # ':' → ' _' eaten by the float-spec regex
' 51 in'
```

The leading space in that second result is the stolen ` ` being applied as a
float-spec *sign*. Same shape for `precision: 2`.

> **Rule of thumb: use `=` when the value is a number or symbol; `:` is safe
> for words** (`True`, `False`, `{unit}`), which covers every use inside this
> library.

---

## Parameter reference

Defaults come from the class, which comes from the config file
(see [Config defaults](#config-defaults)).

### Value shaping

| Key | Default | Effect | Status |
|---|---|---|---|
| `precision` | per class | decimal places, **capped by `max`** | ✅ |
| `max` | per class | **total displayed digits** — the width budget `shorten` rescales to fit | ✅ |
| `forcePrecision` | `False` | *intended:* always show decimals out to `precision` | ⚠️ **NOT IMPLEMENTED** |
| `sizeHint` | per class | *intended:* override the generated size-hint string | ⚠️ **NOT IMPLEMENTED** |
| `type` | `g` | float type; `g` is renormalized to `f` internally | ✅ |
| `shorten` | per config | rescale/refit — may change the unit | ✅ |
| `minwidth` / `fill` / `align` / `sign` | `''` | standard float-spec fields | ✅ |
| `leadingZero` | `'auto'` | the `0` before the radix on values < 1 — `True`/`False`/`'auto'`, see [below](#leadingzero-and-the-borrowed-digit) | ✅ |
| `trailingZero` | `True` | *intended:* pad decimals to full precision, staying under `max` | ⚠️ **NOT IMPLEMENTED** |

### Unit and decoration

| Key | Default | Effect | Status |
|---|---|---|---|
| `showUnit` | per class | render the unit at all | ✅ |
| `unit` | per class | override the unit string | ✅ |
| `unitSpacer` | per class | **a string**, not a flag — the text between value and unit | ✅ (see gotcha) |
| `decorator` | per class | trails the value (`º`) | ✅ |
| `prefix` / `suffix` | none | wrap the whole result | ✅ |
| `plural` | `False` | with a non-1 value, use the plural unit/name | ✅ |
| `unit_type` | none | `name` swaps symbol for class name — **only takes effect together with `plural=True`** | ⚠️ partial |
| `format` | none | replace the whole template (see below) | ✅ |
| `convert` | none | conversion target, alternative to the leading `unit:` form | ✅ |
| `limits` | per class | — | ⚠️ never read while formatting |

---

## How the string is assembled

Unless you supply `format=`, the template is built as:

```
{prefix}{value}{valueSuffix}{decorator}{unitSpacer}{unit}{suffix}
```

`{unitSpacer}{unit}` are appended only when `showUnit` is true. That is why
the two common shapes differ:

```python
>>> f'{Temperature.Fahrenheit(32)}'   # decorator 'º', unitSpacer ''
'32º'
>>> f'{Wind.MilesPerHour(4.1)}'       # decorator '',  unitSpacer ' '
'4.1 mph'
```

The numeric core is then rendered with
`'{value:{fill}{align}{sign}{minwidth}.{precision}{type}}'`.

**`format=` templates cannot carry their own value spec.** The value is
already a `str` by the time the template is applied:

```python
>>> f'{Length.Meter(1234.5):format={"{value:.4f}{unit}"}}'
ValueError: Unknown format code 'f' for object of type 'str'
```

Use `precision=` / `type=` instead.

---

## precision, max and rounding

**`max` is a display-width budget — the total number of digits that may be
shown while still showing the decimal** (`config/template.ini`). It is not a
decimal-place count, and it is not merely a cap: together with `shorten` it
decides *when a value gets rescaled to fit*, by changing the unit or adding
a `k`/`m` suffix.

```python
>>> Light.Lux(1000)          # 4 digits > budget -> rescaled
'1.00k lux'
>>> Length.Foot(5120)        # too wide in feet -> refit to miles
'0.970 mi'
>>> Length.Meter(1234.5)
'1.234 km'
```

`precision` then fills whatever room `max` leaves, derived per value from
that value's own decimal content.

```python
>>> Pressure.InchOfMercury(29.92)   # 3 digits fit → 1 decimal
'29.9 inHg'
>>> Pressure.InchOfMercury(30.5)
'30.5 inHg'
>>> Pressure.InchOfMercury(30.0)    # no meaningful decimals → precision 0
'30 inHg'
>>> Wind.MilesPerHour(12.75)
'12.8 mph'
>>> Length.Inch(1.25)
'1.2 in'
```

Zero always renders bare — no trailing `.0` — across every unit type:

```python
>>> Pressure.InchOfMercury(0), Light.Lux(0), Wind.MilesPerHour(0)
('0 inHg', '0 lux', '0 mph')
```

`max` applies to values **at or below 1 too**. It did not always — the
`type='g'` normalization gated its clamping behind `if float(value) > 1`, so
`0.004` rendered `'0.00'` at `max=3`, `max=2` *and* `max=1` alike. If you
are reading old behavior into a bug report, check whether it predates that.

---

## `leadingZero` and the borrowed digit

The `0` in `0.5` carries no information — it is a legibility convention.
But it **costs a digit of the `max` budget**, and that digit is sometimes
the difference between showing a value and showing nothing.

`leadingZero` is three-state:

| value | behavior |
|---|---|
| `True` | always keep the zero |
| `False` | always drop it |
| `'auto'` *(default)* | decide per value — see the rule below |

### The `auto` rule

> **Drop the leading zero only when keeping it would render the value as
> zero, AND dropping it actually rescues a digit of the value.**

Both clauses are load-bearing. This rule is easy to "simplify" into
something that looks equivalent and is not — two such attempts are recorded
below precisely so they don't get re-attempted.

```python
>>> from WeatherUnits import Length
>>> format(Length.Inch(0.5),  'max=2, showUnit=False')                 # nothing to gain
'0.5'
>>> format(Length.Inch(0.04), 'precision=2, max=2, showUnit=False')    # else it's '0.0'
'.04'
>>> format(Length.Inch(0.04), 'precision=2, max=3, showUnit=False')    # fits with the zero
'0.04'
>>> format(Length.Foot(5120), 'showUnit=False')                        # 0.9697 mi
'0.97'
```

| value | budget | renders | why |
|---|---|---|---|
| `0.5` | `max=2` | `0.5` | already meaningful — clause 1 fails, keep |
| `0.97` (5120 ft) | `max=3` | `0.97` | already meaningful — keep |
| `0.01` | `max=2` | `.01` | keeping gives `0.0`; dropping rescues it |
| `0.04` | `max=3` | `0.04` | fits with the zero — keep |
| `0.0416` | `max=1` | `0` | keeping gives `0`, dropping gives `.0` — **equally empty, so clause 2 fails and the zero stays** |
| `0` | any | `0` | no fractional part to expose |

### Two wrong rules that look right

**"Drop it whenever the budget is tight."** Unconditional suppression makes
every sub-1 value lose its zero — `0.5 mph` becomes `.5 mph` across the
whole app, which is not what anyone wanted.

**"Drop it when `max - intLength < precision`."** Keys off the *configured*
precision rather than what the value actually needs, so it spends the zero
to buy a **trailing** digit that carries nothing:

```
0.5    -> '.50'    same digit count, no more information
0.9697 -> '.970'   same
```

That is why the implementation compares `round(value, kept)` against
`round(value, dropped)` rather than comparing precisions: the question is
never "does it fit" but "**does dropping it show me something I could not
otherwise see**".

### Interaction with `max`

Dropping the zero is what makes an otherwise contradictory config coherent.
`precision=2, max=2` asks for hundredths inside a two-digit budget — with
the zero, `0.01` needs three. LevityDash ships exactly that pairing for
precipitation, and `auto` resolves it to `.01`.

Note this competes with any annotation: a `≲`-style marker also costs a
character, so within a fixed width you can have the precision *or* the
marker, not both.

### ⚠️ The `30.00` gap

`30.0` renders as `'30'`, so a live pressure readout drifts between `29.9`,
`30`, and `30.1` — inconsistent width. Raising `precision`/`max` does not fix
it, because precision is capped by the value's own decimals:

```python
>>> f'{Pressure.InchOfMercury(30.0):precision=2, max=5}'
'30.0 inHg'
```

**Two declared-but-unimplemented options are the intended mechanism**, both
from `config/template.ini`:

| Option | Intent |
|---|---|
| `trailingZero` | *"display zero after decimal point to full precision staying under max"* |
| `forcePrecision` | *"decimals are always displayed within the precision amount"* |

Neither is consumed by any code. Until one lands there is no way to pin a
fixed decimal width — which is why a pressure readout drifts in width.

---

## shorten, bestFit, auto, localize

- **`localize`** — return the same measurement in the unit configured under
  `[LocalUnits]`.
- **`bestFit`** — climb to the largest unit whose integer part still fits
  inside `max` digits.
- **`auto`** — `localize` then `bestFit`. Also usable as a conversion token:
  `f'{v:auto}'`.
- **`shorten`** — picks the first available strategy: `bestFit`, else `auto`,
  else a thousands-scaling fallback that divides by 1000ⁿ and appends a
  `k`/`m`/`b`/`t` suffix.

**`shorten` can change the unit, not just the magnitude** — worth knowing
before you rely on the rendered unit:

```python
>>> Pressure.InchOfMercury(1013.25)
'497.66 psi'
>>> Length.Meter(1234.5)
'1.234 km'
>>> Light.Lux(1054), Light.Lux(1024581)
('1.05k lux', '1.0246m lux')
```

`shorten` defaults to `False` under `us.ini` and `True` under `si.ini`, with
per-type overrides (e.g. `illuminance = max=4, shorten=True`).

---

## Config defaults

`config/*.ini` sets class-level defaults; nothing there is read at format
time directly.

- `[UnitDefaults]` applies library-wide.
- `[UnitProperties]` applies per measurement type:

  ```ini
  temperature = precision=0, max=3, unitSpacer=False, shorten=False, showUnit=False
  ```

  Each key becomes a `_`-prefixed class attribute (`Temperature._precision`),
  surfaced through properties into the defaults layer.

Because class defaults sit *below* spec parameters in the precedence chain,
any format spec overrides the config. Per-instance assignment
(`m.precision = 2`) works through the same layer.

Declared in the config templates but **never consumed**: `trailingZero`,
`forcePrecision`, `sizeHint`, `exp`, `slide` (the ini says "not yet
implemented"), `kSeparator`, `groupingChar`, `combineUnitAndSuffix`, and
`degrees`. The first two are the ones with real display consequences — see
[the `30.00` gap](#-the-3000-gap).

---

## Subclass hooks

| Hook | Purpose |
|---|---|
| `__format_template__` | assemble the template — override to add/remove parts |
| `__format_value__` | render the numeric core |
| `__repr_value__` | the value portion of `repr()` |
| `formatValue` | pre-scale the number (`Percentage` ×100) |
| `__format_class__` | never overridden anywhere; call site is commented out |

Notable implementations: **`Percentage`** scales by 100 and bumps precision;
**`Direction`** adds cardinal handling and drops `{decorator}` when showing a
cardinal; **`Time`** pre-processes `simple`, `simple+`, `ago`, and timestamp
specs before delegating upward. **Derived units** (`Wind`, `Precipitation`,
…) override no formatting at all — they differ only in `unit`, which is
composed as `numerator/denominator`, enabling `f'{wind:km/hr}'`.

---

## Gotchas

**Boolean-looking values are coerced.** `'f'`, `'n'`, `'t'`, `'y'`, `'no'`,
`'on'`, `'hide'` and friends are parsed as booleans. That is usually what you
want (`showUnit=n`), but it means a single-letter *value* can be swallowed.
`type`, `fill` and `align` are exempt, because they are pasted verbatim into
the float format spec where a bool is always wrong — before that exemption,
`type=f` raised `ValueError: Invalid format specifier '.2False'`.

Keys that are **not** exempt take `False` meaningfully — it disables them:

```python
>>> f'{Wind.MilesPerHour(4.1):unitSpacer=False}'
'4.1mph'
```

**🐛 Uppercase conversions raise.** The check is case-insensitive but the
lookup is not:

```python
>>> f'{Temperature.Fahrenheit(72.5):c}'   # fine
'22º'
>>> f'{Temperature.Fahrenheit(72.5):C}'
KeyError: 'pop from an empty set'
```

**🐛 `Direction`'s `cardinal` parameter is ignored.** Every form is a no-op,
so a cardinal can't be turned off:

```python
>>> f'{Direction(183)}', f'{Direction(183):cardinal=False}'
('S ', 'S ')
```

**`unitSpacer` is a string, not a flag.** `unitSpacer=True` renders the
literal word:

```python
>>> f'{Temperature.Kelvin(273.15):unitSpacer=True}'
'273Truek'
>>> f'{Temperature.Kelvin(273.15):unitSpacer=_}'
'273_k'
```

**Thousands separators are dropped.** `,`/`_` grouping is parsed but never
applied, so `{x:,.2f}` silently loses the separator.

**Dead code, for orientation:** `FormatSpec.limit` is compiled but unused;
`defaultFormat` is superseded by `__format_template__`; `SmartFloat._string`
is a legacy formatter whose one remaining caller passes arguments it does not
accept.

---

## See also

- `tests/test_format_spec.py` — separator parsing, pinned behavior
- `tests/test_formatting.py` — display invariants across unit types
- `config/template.ini` — annotated list of every config option
