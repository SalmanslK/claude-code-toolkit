# Tier C — conventional baselines and AI factors

Use only when the team has **no measured pace** (no usable git history, no past actuals). Every figure here is **assumed**. Recalibrate after the first sprint and switch to Tier A or B.

**How Tier C works:**
- **H = 50h × AI factor:** AI-first 0.5 (H = 25), mixed 0.7 (H = 35), light 0.85 (H = 42.5).
- Price every row with the SKILL.md ratio table, like any other tier.
- The table below is the **cross-check:** conventional hours × the class factor should land within about ±30% of the ratio-table result. If it does not, recheck the class.

Conventional hours assume a mid-level developer without AI tools, and include tests and fixing QA defects.

| Class | Conventional BE hours | AI factor, AI-first team | AI factor, light AI use |
|---|---|---|---|
| Screen-level sub-feature | 3–8 | 0.5 | 0.85 |
| Read-only aggregate: one KPI or report | 16–24 each | 0.5 | 0.85 |
| CRUD module, known pattern | 40–60 | 0.5 | 0.85 |
| Single read-only external lookup | 30–50, plus 16 foundation | 0.7 | 0.9 |
| Workflow module | 80–140 | 0.6 | 0.9 |
| New identity or data-scoping dimension | 120–200 | 0.7 | 0.95 |
| Two-way external integration | 120–200 | 0.8 | 0.95 |
| Legacy data migration | 120–200 | 0.8 | 0.95 |
| Offline sync | 160 BE + 240 mobile | 0.85 | 1.0 |
| Greenfield mobile app, about 4 workflows | 400–600 mobile | 0.7 | 0.9 |

**AI-first** means agents or assistants write most first drafts, with tests generated alongside. **Light AI use** means autocomplete and occasional chat.

**Why the factors differ by class.** Published measurements put the best team-level throughput gain at about 1.4×, roughly a 0.7 factor on average. The gain concentrates in routine code; there is no proven speedup on complex work in mature codebases. See `research.md`.

**Expect Tier C to run high for a strong AI-first team.** In the worked example, the measured CRUD cost was about half of the Tier C figure. That is why it is labelled ±40%, and why the first sprint's actuals should replace it.
