# Interactive formatting playground

**Status:** ready to build. Previously parked behind the naming decision,
which is now weeks out — and the dependency ran the wrong way anyway: the
name appears only in the title, while the page itself is the most useful
thing to put in front of someone who is being asked about the name.

## What

A small demo page: pick a measurement, then drive every formatting
parameter with sliders and toggles and watch the rendered string update
live. The point is that `precision`, `digit_budget`, `leading_zero` and
`shorten` interact in ways that are genuinely hard to hold in your head —
a slider teaches that in about four seconds, where the reference doc takes
a careful read.

It doubles as the landing-page demo. "Here is what this library does" is
much better answered by a live widget than by a code block.

## Why it can be a static page

The library has **zero runtime dependencies** and no compiled extensions
(`pyproject.toml` declares only `python = ">=3.10,<3.15"`). So it runs
under **Pyodide** directly — the page can `micropip.install` the real
wheel and call the real `format()`.

That matters more than convenience: this session established that
hand-written examples drift silently. The README shipped four wrong output
tables and four examples that failed on their first import line, because
nothing executed them. A playground that reimplements the formatting rules
in JavaScript would become the fifth thing that drifts. One running the
actual wheel cannot be wrong — and it doubles as a smoke test that the
published artifact imports and works.

Hosting is then GitHub Pages with no backend, no cost, no ops.

## Rough shape

**Left: inputs**

- measurement picker — a representative set, not everything: `Temperature`,
  `Length`, `Wind`, `Pressure`, `Light`, `Direction`, and a derived
  (`PrecipitationRate`) since derived units behave differently
- a value slider, plus a text field for exact entry (the interesting
  values are the awkward ones — `0.01`, `30.0`, `1013.25`, `22.5`)
- unit selector, populated from the chosen dimension

**Right: parameters**

| control | parameter | notes |
|---|---|---|
| slider 0–6 | `precision` | |
| slider 1–8 | `digit_budget` | the one most worth playing with |
| tri-state | `leading_zero` | `True` / `False` / `auto` — the three-state is the whole point |
| toggle | `shorten` | |
| toggle | `show_unit` | |
| text | `unit_spacer` | a string, not a flag — let people discover `90°Truef` |
| toggle | `cardinal` | only shown for `Direction` |

**Output**

- the rendered string, large
- the equivalent format spec, copyable: `f'{value:precision=2, digit_budget=3}'`
- the equivalent `[UnitProperties]` config line — this is the bridge from
  "I played with sliders" to "I configured my install"

## Worth showing deliberately

The cases that cost real debugging time make the best demos:

- `precision=2, digit_budget=2` on `0.01` — self-contradictory config;
  watch `leading_zero='auto'` rescue it as `.01`
- `30.0` at any setting — renders `30`, the trailing-zero gap
- `Length.Foot(5120)` with `shorten` — the unit changes to miles outright
- `Direction` with `digit_budget` 1 → 2 → 3 — `N` → `NE` → `NNE`
- `unit_spacer=True` → `90°Truef`

A "surprising cases" preset row that loads each of these would carry a lot
of the reference doc's weight without anyone reading it.

## Verification

- the page loads with no network calls beyond the Pyodide CDN and the wheel
- every control round-trips: setting it produces a spec string that, pasted
  into a REPL, gives the same output
- the generated config line, written into a real `.ini`, reproduces the
  same rendering — worth an actual test, since this is the claim most
  likely to quietly rot

## Suggested branch

`docs/format-playground`

## Related

- `docs/formatting.md` — the reference this is the interactive version of
- `docs/parameter-audit.md` §4 — the naming decision this waits on
