# Estimate file — sections, in order

**File name:** `<Project>-<Scope>-Estimates-<YYYY-MM-DD>.md`, written where the user said. If they did not say, use `~/Documents/estimates/` (Windows: `%USERPROFILE%\Documents\estimates\`) and tell them. Never write inside a repo that is not the project being estimated, or into any repo the user called read-only. Write one file per product. When a request covers two products, write two files, each with a scope note pointing to the other.

1. **Title and header line:** as-of date; "Averaged over N independent runs" with a Run spread section when the user asked for averaging (`averaged-runs.md`), otherwise nothing; calibration tier (A, B or C) with H and its source; confidence (the tier's confidence in H, widened per SKILL.md §2); "ballpark for planning, not a commitment".
2. **Scope note:** which product; sibling estimate files; what "Mobile" or "Web" means here if several apps exist.
3. **Estimates table:** the user's **exact columns and row text**, with each estimate column filled as `<min>–<max>h (<likely>h)` or `—`. The **Total** row gives the likely total only; never the sum of the minimums. Add a by-area subtotal table for long lists.
3b. **Reuse** (only when the user named a codebase to reuse from):
    - per task: the reuse %, which driver matched which class or file in the source, and `<min>–<max>h (<likely>h)` after reuse;
    - whether the figures assume copying (porting floor) or a direct call;
    - when reuse is unconfirmed, both scenarios and the question that decides between them.
4. **Implied work not in the list:** item, why it is needed, hours per column, and a conditional total. Mark items conditional if the code was not seen. Shared items say which estimate owns them.
4b. **Optional add-ons** (only when outcome-only rows were priced at their minimum version): item, add-on, hours per column, and a total. They are not in the estimate or the buffer; the client chooses which to buy.
5. **Buffers:** first, one line for the known-pattern items: their ΣE, n, σ and the pooled factor. Then a table of the other items: one row per item, a buffer per column, "shrinks if…", and totals.
6. **Summary:** the likely total (ΣE); the 80% bid (known-pattern ΣE × the pooled factor, plus the other items and their buffers); the worst case including implied work; optional add-ons shown separately. Say which figure is the bid. Then two lines: the **sensitivity** (likely and bid with no team-size cap) and the **assumed-ratio share** (base hours on assumed ratio rows against K or measured rows, SKILL.md §4).
7. **What the hours include and exclude,** plus the assumptions. At Tier A, always state how H was counted: days with a commit × hours per day, plus the overhead share for days with no commit.
8. **How the numbers were derived:**
   - the calibration (the script output, or the actuals used) and the H check: window start, AI-first date, module count from the user vs from the code, and the range if they differ;
   - the catalogue, when used: K per class, F, σ, the min and max multipliers, c and how it was measured, and the modules left out and why;
   - per K-priced item: S_spec with its counts, S, F if applied, and the closest finished module with its scaled hours (and the reason when they differ by more than 30%);
   - per ratio-priced item: the class and ratio (classification rule number, midpoint or quarter point), with the named reason for any quarter-point move;
   - the sanity check against the last phase;
   - the research cross-check;
   - the confidence for columns with no measured pace.
9. **Recommended build order:** a small ASCII dependency chart.
10. **Blockers, dependencies and uncertainties:** per item, or grouped as blockers / spec inconsistencies / decisions needed / dependencies. Mark items with no requirements as blocked.
11. **Recommendations:**
    - spikes;
    - items to obtain before kickoff, and the buffer each frees;
    - sequencing;
    - recalibrating after the first sprint;
    - logging actuals in `calibration-log.md`.
12. **Sources** for any research cited.
13. **Summary pack** (separate file, when more than one scope was priced or the user wants something to share): `<Project>-Summary-<YYYY-MM-DD>.md` and `.pdf`, from `summary-template.md` and `scripts/make_summary_pdf.py`. In the estimate file, the **Summary** section (6) shows the quote-minimum (likely) and the bid side by side, with the pointers (blockers, ambiguities, assumptions and what each could add) listed after the totals.
