# weekly-sweep

**A1 · Requirements.** **Trigger:** the weekly check of every client source; "is everything current?".
**Packs:** none.

## Steps

1. `/book:check-sources all` — every source, one verdict.
2. For each source that moved: `new-fsd-revision`, `answers-arrived` or `qa-artifacts-changed`.
3. `/book:progress` — if a question or task moved.

## Done when

The verdict is UP TO DATE, or each moved source has gone through its flow.
