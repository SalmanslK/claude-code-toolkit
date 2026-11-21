# new-fsd-revision

**A2 · Requirements.** **Trigger:** a new FSD version landed.
**Packs:** fe-guides.

## Steps

1. `/book:check-sources fsd` — captures the new snapshot.
2. `/book:impact` — on each changed section.
3. ✋ `/book:sync-sources` — plans, FE guides, QA suite, overview, Part 3; the person approves the plan changes.
4. ⏸ `/book:fact-check` — on the modules the change reaches.
5. `/book:check-guides` — the FE guides against the change.
6. `/book:publish-guides` — if a guide changed.
7. `/book:progress`.

## Loops

- ⟲ steps 4–5 until no new gap, at most 3 rounds; each gap becomes `/book:raise` (defect or question).

## Done when

Every changed section is in its plan, guide and tests, or raised.
