# finish-feature

**B3 · Features.** **Trigger:** a feature's last task merged.
**Packs:** fe-guides.

## Steps

1. `/book:fact-check` — on the module: requirement, plan, code, test.
2. `/book:check-guides`.
3. `/book:update-docs` — where the code is right and a doc lags.
4. `/book:publish-guides` — if a guide changed.
5. `/book:progress` — marks the feature Built, which the next `/book:release-notes` lists.

## Loops

- ⟲ steps 1–3 until fact-check finds no gap, at most 3 rounds; each gap becomes `/book:raise`.

## Done when

The module is traceable end to end, and its guide is current and published.
