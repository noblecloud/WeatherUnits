# Parameter audit — naming, casing, and dead options

**Status: the rename landed.** This document started as decision material for
the "the config params are a mess" problem that was blocking public
documentation. Sections 1–2 are now a *record* of what changed and why;
sections 3–5 are the parts still open.

Every claim here was checked against the source, not remembered.

See [`formatting.md`](formatting.md) for how the parameters actually behave.

---

## 1. Casing — resolved, snake_case

**Every config key and format-spec parameter is now `snake_case`**, matching
PEP 8 and the wider Python ecosystem. Before the rename the surface was
camelCase with one snake_case outlier (`unit_type`); the choice was to make
the outlier the rule rather than the exception, since camelCase is the
non-standard side for Python.

This is a **breaking change with no compatibility shim**, taken deliberately
pre-launch. The reasoning: a shim's deprecation warning only helps configs
that are being actively maintained, and there are none in the wild yet.

| namespace | convention |
|---|---|
| `.ini` config keys | `snake_case` |
| format-spec params | `snake_case` |
| size-class keys | `Tiny` `Small` `Medium` `Large` `Huge` (deliberate — a different namespace) |
| unit names in `[UnitProperties]` | as spelled (`inHg`, `mmHg`, `precipitationRate`) — these are *unit identifiers*, not params |

### ~~One straggler~~ — resolved

`Config.groupingCharacter` was the last camelCase key. It read nothing any
`.ini` shipped and was itself read by nobody, so rather than renaming it the
customization moved to where it belongs: `GROUPING_CHAR`/`RADIX_CHAR` take an
optional `grouping_character` / `radix_character` override from
`[UnitDefaults]`, resolved **once at config load** instead of on every
rendered value. The separators are a property of the locale, not of a value.

### Failure modes worth remembering

The rename produced two bugs that are worth knowing about before attempting
a similar mechanical sweep:

1. **`\b` does not match inside `_camelCase`.** The underscore is a word
   character, so a `\bmax\b`-style pattern silently skips every
   private attribute (`self._max`). 33 tests failed at once.
2. **A regex rewriting `.ini` files wrote `digit_budget =4`** inside
   comma-separated value lists, producing a key with a trailing space. The
   config parser then silently fell back to defaults — *the exact failure
   mode the rename was meant to make less likely.*

A third class was missed by inspection rather than by regex: **attribute
*reads*** (`direction.max`, `self.max` inside `bestFit`) when the search
pattern was built around the assignment form.

---

## 2. Names that actively misled — what changed

| old | new | why |
|---|---|---|
| `max` | `digit_budget` | Read as "maximum value". It is a **total displayed-digit budget**. This single name cost a multi-hour debugging session: `precision=2, max=2` looks reasonable but is self-contradictory, because `0.01` needs three digits to render with its leading zero. |
| `decorator` | `unit_symbol` | "Decorator" means something else entirely in Python, which made the code harder to read than it needed to be. It is the symbol trailing the number — `°` on temperatures. |
| everything else | `snake_case` form | see §1 |

### Still misleading, not renamed

**`shorten` — one name, two behaviors.** Does *either* "refit to a larger
unit" (5120 ft → 0.97 mi) *or* "divide and append a scale suffix"
(12345 → 12.35k), depending on whether the unit type supports `bestFit`.
Callers can't tell which they'll get, and the unit can change out from under
them. Worth splitting into two options; documented in `formatting.md` in the
meantime.

**`title` / `key` — not formatting at all.** Generic names for per-instance
metadata sitting in a namespace otherwise entirely about rendering. Arguably
they belong somewhere else.

---

## 3. Declared but never consumed

Verified by searching for both the bare name and the `_`-prefixed attribute
across all `.py` files.

**These are not deletion candidates.** Each one has an intended behavior the
author can state; they are unfinished features, not debris. Intents recorded
here so they survive the next person who reads "never consumed" as "unused".

| param | intended behavior |
|---|---|
| `size_hint` | override the generated size-hint string. The natural lever for reserving layout width |
| `slide` | rescale the *unit* rather than the number — 1000 m → 1 km |
| `k_separator` | the character separating powers of 10³ — the `,` in `1,000` |
| `combine_unit_and_suffix` | merge/remove the spacing between the unit and the class's `suffix` |
| `exp` | *(no recorded intent)* |
| `grouping_char` | thousands separators are parsed then dropped — `{x:,.2f}` silently loses the separator |
| `degrees` | `[UnitProperties] direction` |
| `limits` | dead *as a format param*; reachable only as a template variable |

`leading_zero` was on this list until it was implemented — see the
"leading_zero and the borrowed digit" section of `formatting.md`, which
documents the rule and the two plausible simplifications of it that are both
wrong.

Also unused in the same area — but **mostly not debris**, which the sweep
established by asking rather than assuming (see
[`tasks/dead-code-sweep.md`](tasks/dead-code-sweep.md)):

| item | outcome |
|---|---|
| `FormatSpec.limit` | **kept** — the `[max:min]` clamp syntax is still wanted |
| `__format_class__` | **kept** — per-class custom formatting is still wanted |
| `SmartFloat._string` | **kept** — a deliberate second formatting path taking keywords instead of a spec string. Was silently broken by the rename; now repaired and tested |
| `defaultFormat` | **deleted** — superseded by `__format_template__` |
| `_getUnit` | **deleted** — superseded by `localizedUnit` → `loadUnitLocalization` |

Only two of five turned out to be debris. The lesson is the same one the
parameters above teach: uncalled is not the same as unwanted.

---

## 4. The library name

Still open. Not a recommendation — the decision is the author's. Just the
facts that bear on it.

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
lives in the *config*, not the *code* — an argument that a rename would be
honest rather than cosmetic.

`unitkit` has been floated, and would sit consistently beside the sibling
`qolkit` / `statekit` packages in LevityDash.

Practical costs to weigh: the PyPI name, the `WeatherUnits` import used
throughout LevityDash, and the `docs/change-logs/` history.

---

## 5. What's left

1. ~~Decide `trailing_zero` vs `force_precision`~~ — **done.** Both were
   replaced by a single `trailing_zeros` taking
   `off | precision | fill | <int>`, closing the width-drift gap.
2. **Implement or drop the rest of §3** — now that intents are recorded, each
   is a small self-contained piece of work.
3. **Decide the library name** (§4).
4. **Write the public docs**, against a surface that no longer needs
   apologising for.
