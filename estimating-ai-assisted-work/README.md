# estimating-ai-assisted-work

A Claude Code skill for effort estimates for teams that build with AI coding tools. It covers backend, web and mobile, buffers, blockers and build order, and works for any project or stack.

> **In short:** paste a feature list and Claude returns a full estimate file in minutes: a min–max (likely) range per item (backend, web, mobile), an 80% bid, separate buffers, blockers, dependencies and build order. It starts from your team's real speed, measured from your git history. Where you have built similar modules before, it prices a new one by its size against what yours actually cost per size point. In the reference project (a past project) that was about 1.0 hour per point for CRUD and 1.3 for workflow modules, rework included, with the measured hours limited to the declared team size (1.1 and 1.6 without that limit). Otherwise each item is scaled by its type, because AI speeds up routine work much more than integrations, data migrations or new designs. The result is then checked two ways. Against traditional, pre-AI estimates, which are used outright only when there is no history to measure. And against current worldwide research on AI-assisted development (Cursor/University of Chicago, McKinsey, METR, DORA), so the numbers are neither padded nor wishful. Every figure shows how it was derived and how confident it is (±20–30% with measured history, ±40% without), and the method gets sharper as you log actual hours after delivery.

It prices work from **your team's measured pace** (hours per module, read from git), not from industry-norm hours with an "AI discount". It keeps buffers separate, with the condition that shrinks each, and writes one Markdown estimate file per product.

## Install

Copy this folder to your personal skills directory:

- macOS / Linux: `~/.claude/skills/estimating-ai-assisted-work/`
- Windows: `%USERPROFILE%\.claude\skills\estimating-ai-assisted-work\`

Restart Claude Code. The skill loads on its own when you ask for estimates.

**Requires** nothing to price from a saved calibration set. Python 3 and git are needed only to measure a new team's repository (the measurement scripts); Python 3 with `markdown` and Edge or Chrome are needed only for the summary PDF.

## Use

Paste your feature table and ask, for example: *"Estimate these, BE and mobile, with buffers. Our recent work is in ~/code/our-app; we shipped about 20 modules since March."*

To check your pace yourself first:

```bash
python ~/.claude/skills/estimating-ai-assisted-work/scripts/measure_velocity.py --repo ~/code/our-app --modules 20
python ~/.claude/skills/estimating-ai-assisted-work/scripts/module_catalogue.py --repo ~/code/our-app --since 2026-03-01
```

The second script lists each finished module's hours and size, and the constant K that turns size into hours. Its defaults fit a .NET `Features/<Module>/` layout. For another stack, give it a small JSON config that says where your modules live and what to count: `module_catalogue.py --help-config`. The skill reads nothing from any particular project. Every path comes from the arguments.

## Averaging (optional)

By default one estimate is produced. Ask for "estimate this 3 times and average" (2 or 3 runs, never more) to get independent runs, reconciled row by row, with the average and the spread between runs. It removes random differences between runs; it does not remove shared assumptions. Details: `references/averaged-runs.md`.

## Competitive minimum and the summary pack

By default the skill quotes the **lowest realistic build hours**: the median outcome of the minimum version of every requirement, on the team's fastest measured pace. Optional, conditional and unwritten items become add-ons, buffers, assumptions and blockers, shown separately, and they make up the bid. The skill never lowers a measured H or sums per-item minimums to get there.

When several scopes are priced (for example Lean, Full, Complete), or you ask for something to share, it fills `references/summary-template.md` and makes a PDF with `scripts/make_summary_pdf.py` (needs Python, `pip install markdown`, and Edge or Chrome). `references/summary-template.md` shows the finished shape.

Web pace can be measured from a front-end repo the same way as backend pace; until then web rows use assumed ratios and a 30% buffer.

## Accuracy

Accuracy depends on how much it can measure about your team:

| Tier | What you provide | Confidence in H |
|---|---|---|
| A | A repo of the same team's recent work, plus the module count | ±20% |
| B | Actual hours for 3+ past modules | ±25% |
| C | Nothing measured | ±40%; runs high for strong AI-first teams |

These figures are how sure the skill is of **H**, your team's hours per module. Most class ratios are still assumed. **Until `references/calibration-log.md` holds 3 shipped items for your team, the estimate is widened by 10 points**, e.g. ±30% at Tier A.

**Ranges and the bid.** Each item comes back as min–max (likely). The likely figure is the median outcome. On the reference team, one item in five finished under the minimum and one in five over the maximum. Per-item minimums can't be added up into a bid: the chance that every item comes in low together is close to zero. The skill gives an 80% bid instead. Known-pattern items share one pooled factor (about 1.1× for 8 items on the reference team), and risks that hit every item at once keep their own buffers.

**Repeatability.** Two people estimating the same list for the same team should land within about 10% of each other. The fixed rules make that possible:
- K × size where the team has reference modules, otherwise a fixed ratio table priced at midpoints;
- one permitted adjustment, to a quarter point, with a named reason;
- a fixed order for classifying items;
- midpoint buffers.

**The biggest lever on accuracy is H**, the team's hours per module. Give the window's dates, the date the team went AI-first, and a module count that matches the code. The skill checks H against a plausible range before using it.

**Make it sharper over time:** after each item ships, add a row to `references/calibration-log.md`.

**Keep the research current:** `references/research.md` is dated; the skill refreshes it when it is more than 6 months old.
