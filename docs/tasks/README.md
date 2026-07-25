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
| **`trailing_zero` vs `force_precision`** | Both declared, neither consumed, and they overlap. Probably one option rather than two — a single `trailing_zeros` taking `off \| precision \| fill \| <int>` was floated. Implementing it closes the width-drift gap where a live pressure readout oscillates between `29.9`, `30` and `30.1`. |
| ~~**`shorten=False` on `Direction`**~~ | **Resolved 2026-07-25.** The budget counts compass *components*; the atom is a letter when abbreviated and a word when spelled out. Both forms now read one shared index ladder, so they always name the same heading. Word forms are derived from the abbreviations rather than kept in a parallel list — the old list had `NE` spelling as the single word `Northeast`, so word count never matched the budget. |

## Ready to pick up

- **[format-playground.md](format-playground.md)** — interactive demo page
  with sliders for every formatting parameter. Runs the real library in the
  browser via Pyodide (the package has zero runtime dependencies), so it
  can't drift from actual behaviour the way hand-written examples did.
  Wants the naming decision settled first.

## Loose ends

Small, self-contained, no decisions needed.

- **The never-consumed parameters.** `slide`, `k_separator`,
  `combine_unit_and_suffix`, `size_hint`, `exp`, `grouping_char`,
  `degrees`. Intents are recorded in
  [parameter-audit.md](../parameter-audit.md) §3 — these are unfinished
  features, **not** debris, and should not be deleted on the strength of
  "nothing reads it".
- **`groupingCharacter` casing straggler.** `config/__init__.py:95` still
  reads a camelCase key. It appears in no shipped `.ini`, so the read always
  falls through to its default — harmless today, wrong after the snake_case
  rename.
- **Dead code in the formatting area.** `FormatSpec.limit` (compiled, never
  applied), `__format_class__` (never overridden, its only call site
  commented out), `defaultFormat` (superseded by `__format_template__`), and
  `SmartFloat._string` (its one remaining caller passes arguments it no
  longer accepts — it would `TypeError` if reached). Unlike the parameters
  above, this really is debris.
- **`digit_budget` caps but does not grant.** Raising it does not buy more
  decimals, because `precision` is separately capped by the class default
  and by the value's own decimal content. Documented in the README with a
  ⚠️; unclear whether that's the intent or a second gap.
- **`[UnitProperties]` only half-binds to derived unit classes.**
  `precision` reaches `Hourly[in/hr]`, `digit_budget` does not. Found from
  the LevityDash side; not yet diagnosed here.
