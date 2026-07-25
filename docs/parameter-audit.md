# Parameter audit — naming, casing, and dead options

**Nothing has been renamed.** This is decision material for the "the config
params are a mess" problem that has been blocking public documentation. It
catalogues what actually exists so the cleanup can be *decided* rather than
*discovered*.

Every claim here was checked against the source, not remembered.

---

## 1. Casing — less broken than it feels

The impression is "some camel, some snake". The reality is narrower:

**Config file params (`[UnitDefaults]`, `[UnitProperties]`) are uniformly
camelCase or single lowercase words.** There is no snake_case in any `.ini`:

```
precision  max  unit  suffix  unit_symbol  title  exp  slide  shorten
show_unit  unit_spacer  leading_zero  trailing_zero  force_precision
k_separator  size_hint  grouping_char  combine_unit_and_suffix  cardinal
degrees  precipitationRate
```

**The single real outlier is `unit_type`**, a format-spec parameter:

| namespace | convention | exceptions |
|---|---|---|
| `.ini` config keys | camelCase / lowercase | none |
| format-spec params | camelCase / lowercase | **`unit_type`** |
| size-class keys | `Tiny` `Small` `Medium` `Large` `Huge` | (deliberate — a different namespace) |

So the casing fix is *one rename*, not a sweep. `unitType` would make the
set uniform.

Internal regex group names (`format_spec`, `grouping_option`) are also
snake, but those are implementation details never typed by a user.

---

## 2. Names that actively mislead

Ordered by how much confusion each has demonstrably caused.

### `max` — the worst offender

Reads as "maximum value". It is a **total displayed-digit budget**. This
single name cost a multi-hour debugging session: a config saying
`precision=2, digit_budget=2` looks reasonable and is in fact self-contradictory,
because `0.01` needs three digits.

Candidates: `maxDigits`, `digitBudget`, `width`.
`maxDigits` is the smallest change that removes the ambiguity.

### `shorten` — one name, two behaviors

Does *either* "refit to a larger unit" (5120 ft → 0.97 mi) *or* "divide and
append a scale suffix" (12345 → 12.35k), depending on whether the unit type
supports `bestFit`. Callers can't tell which they'll get, and the unit can
change out from under them.

Worth considering splitting into two options, or at minimum documenting the
branch (currently covered in `formatting.md`).

### `unit_symbol` — vague

It is the symbol trailing the number — `°` on temperatures. "Decorator" also
means something entirely different in Python, which makes the code harder to
read than it needs to be. Candidates: `symbol`, `valueSuffix` (taken),
`glyph`.

### `k_separator` — cryptic

The `k` presumably refers to thousands. Never consumed by any code, so its
intent is unrecoverable from behavior alone — **only you know what this was
meant to do.**

### `exp` / `slide` — unrecoverable

Both declared, never consumed, and the ini itself annotates `slide` as "not
yet implemented". `exp` has no annotation at all. Same situation: intent
lives only in your memory.

### `title` / `key` — not formatting at all

Generic names for per-instance metadata sitting in a namespace otherwise
entirely about rendering. Arguably they belong somewhere else.

---

## 3. Declared but never consumed

Verified by searching for both the bare name and the `_`-prefixed attribute
across all `.py` files:

| param | status | notes |
|---|---|---|
| `trailing_zero` | **dead** | documented intent: pad decimals to full precision under `max`. The missing half of the `30.0 → '30'` width-drift problem |
| `force_precision` | **dead** | documented intent: always show decimals to `precision`. Overlaps `trailing_zero` — likely only one is needed |
| `size_hint` | **dead** | documented intent: override the generated size-hint string. The natural lever for reserving layout width |
| `exp` | **dead** | no documented intent |
| `slide` | **dead** | ini says "not yet implemented" |
| `k_separator` | **dead** | intent unclear |
| `grouping_char` | **dead** | thousands separators are parsed then dropped — `{x:,.2f}` silently loses the separator |
| `combine_unit_and_suffix` | **dead** | `si.ini` only |
| `degrees` | **dead** | `[UnitProperties] direction` |
| `limits` | **dead as a format param** | reachable only as a template variable |

`leading_zero` was on this list until it was implemented (see
`formatting.md`).

**Three of these — `trailing_zero`, `force_precision`, `size_hint` — form a
coherent cluster** around controlling rendered width, and are the ones with
real display consequences. The rest are candidates for deletion.

Also dead in the same area: `FormatSpec.limit` (compiled, never applied),
`__format_class__` (never overridden, its only call site commented out),
`defaultFormat` (superseded by `__format_template__`), and
`SmartFloat._string` (legacy formatter whose one remaining caller passes
arguments it no longer accepts — it would `TypeError` if reached).

---

## 4. The library name

Not a recommendation — the decision is yours. Just the facts that bear on
it.

What the package actually contains:

```
airQuality  base  config  defaults  derived  digital  errors
length  mass  others  pressure  temperature  time_
```

`digital` (bytes), `mass`, `length`, `time_`, and the whole `derived`
machinery (any numerator/denominator pair) are general-purpose. The
weather-specific parts are `airQuality`, `pressure` presets, and the
weather-flavored defaults in `us.ini`/`si.ini`.

So it is fairly described as **a general unit library with weather-oriented
defaults and a weather-derived unit set**. That framing suggests the domain
lives in the *config*, not the *code* — which is an argument that a rename
would be honest rather than cosmetic.

Practical costs to weigh: PyPI name, the `WeatherUnits` import used
throughout LevityDash, and the `docs/change-logs/` history.

---

## 5. Suggested order, if you do the work-over

1. **Delete the unrecoverable dead params** (`exp`, `slide`, `k_separator`,
   `combine_unit_and_suffix`, `degrees`, `grouping_char`) — removing them costs
   nothing since nothing reads them, and it shrinks the surface the docs
   have to explain.
2. **Rename `unit_type` → `unitType`** — makes casing uniform in one commit.
3. **Rename `max`** — the highest-value change, and the one most likely to
   prevent a repeat of this week.
4. **Decide `trailing_zero` vs `force_precision`** — probably one option, not
   two, and implementing it closes the width-drift gap.
5. *Then* write the public docs, against a surface that no longer needs
   apologising for.

Renames 2 and 3 are breaking changes for any config in the wild. Both are
mechanical, and both want a compatibility shim reading the old name with a
deprecation warning for at least one release.
