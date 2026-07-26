# Dead-code sweep — DONE

> ✅ **Completed 2026-07-26.** Kept as the record. Author annotations are
> preserved verbatim under each item; the outcome is noted above them.
>
> **Deleted (2 of 5):** `defaultFormat` (both definitions, plus the two
> template properties it orphaned) and `_getUnit`.
>
> **Kept (3 of 5):** `FormatSpec.limit`, `__format_class__` and
> `SmartFloat._string` — each now carries an `INTENTIONALLY KEPT` note at
> the code recording why, so the next reader doesn't re-propose deleting it.
>
> **Item 5** resolved separately: the property is deleted and the
> customization moved to a config override resolved once at load
> (`grouping_character` / `radix_character` in `[UnitDefaults]`),
> rather than a lookup on every rendered value.
>
> Verified: 264-row render snapshot unchanged, 141 WeatherUnits tests
> (up from 132), 189 LevityDash.

**Ground rule from previous sessions:** WIP-looking code is not debris. Items
here are only listed because nothing reaches them *and* they would not work
if it did. Where that second half isn't true, it's called out.

---

## 1. `FormatSpec.limit` — **KEPT**

`base/_SmartFloat.py:66`

```python
limit = re.compile(r'\[(?P<max>([+-]?[\d.]+)|\*)?:(?P<min>([+-]?[\d.]+)|\*)?]')
```

A compiled regex for a `[max:min]` bracket syntax in format specs. **Zero
readers** — nothing ever calls `.limit`, so the syntax it describes is not
accepted anywhere.

Note this is *not* `_limits` (the min/max clamp on `FiniteField`, very much
alive) — only the unused regex sharing the name.

> Worth knowing: the syntax it implies — `{value:[100:0]}` to clamp at
> format time — doesn't exist anywhere else. If that was the intent, this is
> a design note, not debris.

**ANNOTATION:**

I definately want to impplement this at some point. I can't remember what exactly it was supposed to be used for, but there was something.

---

## 2. `__format_class__` — **KEPT**

`base/_SmartFloat.py:1009`, with its only call site commented out at `:989`

```python
# params = value.__format_class__(formatSpec, params)     # line 989
...
def __format_class__(self, formatSpec: str, formatParams: Mapping) -> dict:   # line 1009
```

Never overridden by any subclass, and the single call site is commented out.
Listed in `docs/formatting.md` as a subclass hook, which is currently untrue.

**ANNOTATION:**

I see that this really is unused, but it's there because classes should be able to have custom formating that gets applied. I'm fairly certain I've had this implemented, or something like it, at some point.

---

## 3. `defaultFormat` — **DELETED**

`base/_SmartFloat.py:1133` and its override `others/__init__.py:123`

```python
# _SmartFloat.py:1133
@property
def defaultFormat(self) -> str:
    if self.show_unit:
        return "{value}{unit_symbol}{unit_spacer}{unit}"
    return "{value}{unit_symbol}"

# others/__init__.py:123 — Direction's override
@property
def defaultFormat(self) -> str:
    if self._cardinal:
        return self.__cardinalFormat
    return self.__valueFormat
```

**Zero readers for either.** Superseded by `__format_template__`, which
builds the same string conditionally and *is* called.

⚠️ **Do not confuse with `defaultFormatParams`** — different name, very much
alive (read at `_SmartFloat.py:808`, `:828`, `:859`). Only the one without
`Params` goes.

**ANNOTATION:**

Yeah, I think this one is safe to delete, haha

---

## 4. `SmartFloat._string` — **KEPT, and repaired**

`base/_SmartFloat.py:666`

```python
def _string(
    self,
    shorten: bool = None,
    prefix: str = None,
    suffix: str = None,
    decorator: str = None,
    spacer: Union[bool, str] = None,
    unit: bool = None,
    maxLength: int = None,
    formatSpec: str = None,
) -> str:
```

Legacy formatter, superseded by `__format__`. Two things reference it:

**a) A dead caller that would crash.** `others/__init__.py:111`:

```python
@property
def decoratedInt(self) -> str:
    return super()._string(forceUnit=False, asInt=True)
```

Neither `forceUnit` nor `asInt` is in the signature above — this raises
`TypeError` if reached. It isn't: `decoratedInt` has no callers either.

**b) A live test that monkeypatches it.** `tests/test_conversion_optimization.py:94`:

```python
original = _SmartFloat.SmartFloat._string

def counting_string(self, *args, **kwargs):
    calls['count'] += 1
    return original(self, *args, **kwargs)

_SmartFloat.SmartFloat._string = counting_string
try:
    Temperature.Fahrenheit.convert_array(np.arange(1000, dtype='float64'), Temperature.Celsius)
finally:
    _SmartFloat.SmartFloat._string = original
self.assertEqual(0, calls['count'])
```

**The test asserts `_string` is never called** — it guards that bulk array
conversion doesn't pay presentation cost. That guard is worth keeping, but
it's currently pointed at a method nothing calls anyway, so it passes for the
wrong reason and would keep passing if formatting *were* triggered through
`__format__`.

**Proposed:** delete `_string` and `decoratedInt`, and re-point the test at
the live formatting entry (`__format_value__`), so it actually guards the
thing it describes. That's a small behavior change to the test — it may fail,
which would be a real finding.

**ANNOTATION:**

I want to keep this as a callable function so that there are is than one way to format a value. This is also adds a way to call custom formatting without a whole lot of parsing needed for validation. Like if there is a custom 'convert' function written into a plugin schema in LevityDash. (I don't know if that's a very good example, it's just the first thing I could come up with)

---

## 5. `Config.groupingCharacter` — **DELETED, override moved to load time**

`config/__init__.py:111`

```python
@property
def groupingCharacter(self) -> bool | str:
    value = self['UnitDefaults'].get('groupingCharacter', True)
    return convertString(value)
```

**Zero readers**, and the key it reads (`groupingCharacter`, camelCase) is in
no shipped `.ini`, so it always falls through to `True`.

Separately alive and unrelated: the module-level `GROUPING_CHAR`
(`config/__init__.py:203`), derived from the locale and used in
`_SmartFloat.py:123`'s number regex. That stays.

Two options — your call:
- **delete** the property, since `GROUPING_CHAR` already covers the need, or
- **keep and rename** to `grouping_character` for the snake_case sweep, if
  the intent was a per-config override of the locale's separator.

Related: `grouping_char` is on the never-consumed parameter list in
`parameter-audit.md` §3 — thousands separators are parsed then dropped, so
`{x:,.2f}` silently loses the separator. If you want that fixed, this
property is probably the lever, and it should stay.

**ANNOTATION:**

It's basically the thousand's separator. that character needs to be customizable, but both might be redundant? I'm not sure on this one...

---

## Explicitly NOT proposed for deletion

Listed so you can see they were considered and kept.

| item | why it stays |
|---|---|
| `_getUnit`, `_getUnitTypes` (`_Measurement.py:915`) | Never called in any commit in the repo's history — but they carry `# TODO: Implement into child classes`, which reads as a real design intent (per-class unit resolution, versus the central fuzzy-match in `loadUnitLocalization`). Kept as a design note. |
| `slide`, `k_separator`, `combine_unit_and_suffix`, `size_hint`, `exp`, `grouping_char`, `degrees` | Never consumed, but you've stated intents for them — unfinished features, not debris. See `parameter-audit.md` §3. |
| `defaultFormatParams` | Alive. Only mentioned because of the name collision with item 3. |
| `FiniteField._limits` | Alive. Only mentioned because of the name collision with item 1. |

_getUnit looks like it can be deleted

---

## Outcome notes

**Item 3** also removed `Direction.__cardinalFormat` and `__valueFormat`,
which `defaultFormat` was the only reader of.

**Item 4** turned out to be broken, not merely unused: the snake_case rename
had rewritten this method's local `decorator` into `unit_symbol` inside the
f-string but not in the signature, so every call raised
`NameError: name 'unit_symbol' is not defined`. Nothing called it, so nothing
caught it. Fixed by renaming the parameter to `unit_symbol` (matching the
library-wide rename), and `tests/test_string_api.py` now covers it — all 9
assertions fail if that mistake is reintroduced.

Its only in-tree caller, `Direction.decoratedInt`, passed `forceUnit=`/
`asInt=`, which were never parameters; rewritten against the real signature
as `_string(unit=False, formatSpec='.0f')`. `_string` also inherited the
trailing-space bug on dimensionless units and got the same one-line fix as
`__format_template__`.

**Item 5's outcome:** the separators are a property of the locale — they
change when someone moves country, not between values — so a per-render
branch would buy nothing. `GROUPING_CHAR`/`RADIX_CHAR` now take an optional
`[UnitDefaults]` override at config load, and the unused property is gone.
That keeps the customization the author wanted without the `if` on the
rendering path.

**`_getUnitTypes`** (`_Measurement.py`, beside the deleted `_getUnit`) was
left in place — the annotation named `_getUnit` only. It is also uncalled,
but unlike `_getUnit` it isn't broken. Say the word and it goes.

---

## Verification plan once you've annotated

- the 264-row render snapshot across 5 dimensions and 22 unit classes,
  diffed before/after — expected diff is **zero rows**
- both suites (132 WeatherUnits, 189 LevityDash)
- for item 4 specifically, the re-pointed test run on its own, since a
  failure there is a genuine finding rather than a regression
