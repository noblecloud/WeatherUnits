# Time should rescale on heuristics, not on digit budget

**Status:** noted 2026-07-26, not fixed.

`digit_budget` is the wrong lever for deciding when a duration changes unit.
It asks "how many characters", when the real question is "is this unit still
meaningful". Anything past ~18-36 hours should stop being hours regardless of
how many digits that takes — `33 hrs` is technically compact and practically
useless.

## What already exists

`Time.__format__` (`time_/time.py`) is already a per-class heuristic
formatter, overriding `__format__` outright rather than using a hook:

| spec | behaviour | state |
|---|---|---|
| `simple` | `shorten=True, plural=True` → `33 hrs` | ✅ works |
| `simple+` | same, full unit names → `33 Hours` | ✅ works |
| `ago` | relative, signed → `33 hrs ago` / `in 3 hrs` | ✅ works |
| `timestamp` | magnitude-escalating clock form | ❌ **raises TypeError** |

`timestamp` is the one carrying the intended heuristic:

```python
if self.hour > 100: format_spec = f'{{day}} {format_spec}'
if self.day > 100:  format_spec = f'{{year}} {format_spec}'
```

Magnitude-based escalation, exactly the right idea — and unreachable,
because the spec errors before it gets there.

## Two concrete jobs

1. **Fix `timestamp`.** It is the existing home for this logic.
2. **Give the graph tooltip a better spec.** `Graph.py` currently hand-rolls
   the sign:
   ```python
   t = Second(t).auto
   timestamp = f'{t:+:simple}' if abs(t.second.int) > 900 else 'now'
   ```
   `ago` already handles direction (`in 3 hrs` / `3 hrs ago`), so most of
   that line is reimplementing it.

## Relation to `__format_class__`

`__format_class__` is kept-but-unused (see
[dead-code-sweep.md](dead-code-sweep.md) §2), on the grounds that classes
should be able to apply their own formatting. `Time` proves the need — it
just does it by overriding `__format__` wholesale. If `__format_class__` is
revived, `Time` is the obvious first client, and moving it onto the hook
would show whether the hook's shape is right.

## Not a digit-budget fix

Worth stating plainly so nobody "fixes" this by tuning `digit_budget`: the
budget is a *width* constraint and should stay one. What is missing is a
notion of which units are sensible for a given magnitude — a per-dimension
ladder, not a character count.
