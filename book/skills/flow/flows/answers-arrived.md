# answers-arrived

**A3 · Requirements.** **Trigger:** the BA or the client answered our questions, in FSD comments or the Product Q&A.
**Packs:** fe-guides.

## Steps

1. `/book:check-sources` — reads the threads and the Q&A.
2. `/book:sync-sources` — moves each answer to *Resolved* and carries it into the plans.
3. `/book:raise defect` — if an answer contradicts built code; then `fix-defect`.
4. ✋ `/book:impact` — if an answer changes a plan; the person approves the plan change.
5. `/book:check-guides` — if a guide shows the question as open.

## Done when

No answered question is still listed open.
