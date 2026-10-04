# Tasks

Self-contained briefs for work meant to be picked up later or by someone
else. Same convention as LevityDash's `docs/tasks/`: each file carries its
own context, the expected change, how to verify it, and a suggested branch.

Nothing here is scheduled.

---

## Needs a decision first

These are blocked on a judgment call, not on effort.

| | |
|---|---|
| **Library name** | `WeatherUnits` undersells it — `digital`, `mass`, `length`, `time_` and the whole `derived` machinery are general-purpose; the weather part lives in the config. `unitcorn` 🦄 is the standing candidate and is free on PyPI. The current name is already published at 0.7.1 and is the author's own, so a rename is a clean handoff: publish the new name, then ship the old one as a shim that depends on it and warns. See [parameter-audit.md](../parameter-audit.md) §4. |
| ~~**`trailing_zero` vs `force_precision`**~~ | **Resolved 2026-07-25.** Both replaced by a single `trailing_zeros` taking `off \| precision \| fill \| <int>`, always capped by the budget. Default stays `off`, so no existing output changed. |
| ~~**`shorten=False` on `Direction`**~~ | **Resolved 2026-07-25.** The budget counts compass *components*; the atom is a letter when abbreviated and a word when spelled out. Both forms now read one shared index ladder, so they always name the same heading. Word forms are derived from the abbreviations rather than kept in a parallel list — the old list had `NE` spelling as the single word `Northeast`, so word count never matched the budget. |

## Bugs — ready to pick up (found 2026-10-04)

- **[same-dimension-regressions.md](same-dimension-regressions.md)** — `8f1ce65`
  broke metric↔imperial comparison and arithmetic (`Meter(1) + Foot(1)` raises,
  `Celsius(0) == Fahrenheit(32)` is False, mixed temperatures sort wrong) and left
  `==` tolerant while `hash` is not. Equality semantics are decided; see the brief.
- **[missing-values-and-locale.md](missing-values-and-locale.md)** — NaN becomes the
  upper limit (`Humidity(nan)` shows `100%`); the import crashes when the locale is
  unrecognised; the test suite's verdict depends on the host locale (19 failures
  under `us.ini`).

## Ready to pick up

- **[small-fixes.md](small-fixes.md)** — four independent items: Kelvin's symbol
  is `'k'` (should be `'K'`), the `heatIndex` guard reads `300 > K < 318`,
  `wu.auto(value, unit)` crashes, and there is no `py.typed`.

> **The cleanup gate is clear.** Everything that was blocking "show it to
> people and then decide the name" has landed: the README executes, the
> parameter surface is snake_case and documented, the dead code is resolved,
> and the config actually binds. What remains below is either a decision or
> a new feature, not tidying.

- **[format-playground.md](format-playground.md)** — interactive demo page
  with sliders for every formatting parameter. Runs the real library in the
  browser via Pyodide (the package has zero runtime dependencies), so it
  can't drift from actual behaviour the way hand-written examples did.
  **Not blocked on the name** — the name appears only in the title, and a
  live page is a better thing to show someone than a description of one.

## Loose ends

Small, self-contained, no decisions needed.

- **The never-consumed parameters.** `slide`, `k_separator`,
  `combine_unit_and_suffix`, `size_hint`, `exp`, `grouping_char`,
  `degrees`. Intents are recorded in
  [parameter-audit.md](../parameter-audit.md) §3 — these are unfinished
  features, **not** debris, and should not be deleted on the strength of
  "nothing reads it".
- ~~**`groupingCharacter` casing straggler.**~~ **Resolved 2026-07-26.**
  Rather than renamed: the separators are a property of the locale, not of a
  value, so `GROUPING_CHAR`/`RADIX_CHAR` now take an optional
  `grouping_character` / `radix_character` override from `[UnitDefaults]`,
  resolved once at config load. The unused property is gone.
- ~~**Dead code in the formatting area.**~~ **Resolved 2026-07-26** — see
  [dead-code-sweep.md](dead-code-sweep.md). Only 2 of 5 candidates were
  actually debris. `FormatSpec.limit`, `__format_class__` and
  `SmartFloat._string` are wanted and kept, each annotated at the code;
  `defaultFormat` and `_getUnit` are deleted. `_string` turned out to be
  *broken* rather than merely unused (the rename had left a `NameError` in
  it) and is now repaired and covered by `tests/test_string_api.py`.
- **`digit_budget` caps but does not grant.** Raising it does not buy more
  decimals, because `precision` is separately capped by the class default
  and by the value's own decimal content. Documented in the README with a
  ⚠️; unclear whether that's the intent or a second gap.
- ~~**`[UnitProperties]` only half-binds to derived unit classes.**~~
  **Resolved** by the symbol-key binding fix
  ([unitproperties-binding.md](unitproperties-binding.md)). Verified
  2026-07-26: under LevityDash's config, `Hourly[Length]` now receives both
  `precision=2` and `digit_budget=2`, and renders `.04 in/hr`.

- **[human-friendly-time.md](human-friendly-time.md)** — durations should
  rescale on heuristics rather than digit budget (`33 hrs` is compact
  and useless). The heuristic formatter already exists in `Time.__format__`;
  its `timestamp` spec carries the magnitude-escalation logic and currently
  raises TypeError.

## Design

Decided direction, not yet built. Purpose: easy, automatic conversion for
normalising and humanising data from any API; units declared with a class,
everything else automatic.

Dependency order: [same-dimension-regressions.md](same-dimension-regressions.md)
(the minimal fix) -> conversion-core -> derived-units-and-algebra -> compound
parsing. [missing-values-and-locale.md](missing-values-and-locale.md) and
[small-fixes.md](small-fixes.md) are independent.

- **[conversion-core.md](conversion-core.md)** — four conversion paths become
  one: a reference (SI) unit per dimension, `to_reference` / `from_reference`
  per unit, declaration keywords, generated accessors. Phase 0 (physical-constant
  tests) is ready; the declaration spelling needs sign-off before phase 2.
- **[derived-units-and-algebra.md](derived-units-and-algebra.md)** — the
  denominator does two jobs (unit and window); split them. Then exponent-vector
  dimension algebra (`^3`), type-preserving operators. Depends on phase 1 above.
- **[unit-parsing.md](unit-parsing.md)** — strict `wu.parse`, scoped lookup,
  `UnknownUnit` / `AmbiguousUnit`, explicit `wu.suggest`. The strict half can
  start now; compound units wait on the algebra.

## Backlog

- **[ideas.md](ideas.md)** — knots, Beaufort, irradiance, PPFD/DLI, VPD, EC/TDS,
  Home Assistant normalisation, `to_dict`/`from_dict`, volume. Maintainer
  prioritises.
