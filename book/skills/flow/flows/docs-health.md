# docs-health

**E1 · Docs health.** **Trigger:** periodic, or the docs feel wrong.
**Packs:** fe-guides.

## Steps

1. `/book:check-consistency` — docs against docs.
2. `/book:check-docs` — docs against code; reports.
3. `/book:update-docs` — where the code is trusted; applies.
4. `/book:check-permissions all` — the FSD's role rules against authorization §2 and the code; reports.
5. `/book:trim`.
6. `/check-guides`.

## Loops

- ⟲ steps 1–3 until both checks are clean, at most 3 rounds.

## Done when

Both checks are clean, and no document is over its size.
