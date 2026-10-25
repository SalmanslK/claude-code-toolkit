# Averaged runs (on demand)

**Default is 1 run. Use this only when the user asks** ("estimate this 3 times", "average it", "runs: 2"). The maximum is 3; if the user asks for more, use 3 and say so. A single run can land 15-25% away from another on a document with no module breakdown (judgement calls: how many measures to count, how to group rows). The average of independent runs removes that random difference. **It does not remove errors every run shares** (assumed ratios, the measured pace), so it never narrows the stated confidence.

## 1. Before starting
Tell the user, in one line, that N runs take about N times the time and tokens. Do intake once (columns, set, team, blockers, defaults) and record the answers; every run gets the same answers.

## 2. Run N independent estimates
- Start each run as its own subagent (the Agent tool) so runs cannot see each other. Give each: the skill path, the requirements document path, and the recorded intake answers. Tell it to follow the skill from scratch, write only to `<folder>/runs/run-<k>/`, and not to open earlier estimates of the same scope or the other runs.
- If subagents are not available, do the runs one after another yourself, and state in the file that the runs were **not independent** (the average is then less trustworthy).
- Do not change any rule between runs.

## 3. Reconcile
Line the runs up **by source section**, not by row id.
- **Row present in every run:** final likely = the mean of the runs' likely; min = mean of mins; max = mean of maxes.
- **Row present in 2 of 3 runs:** included, at the mean of the runs that have it, and listed as *disputed row*.
- **Row present in 1 run only:** not in the base. Listed as an add-on or pointer with its hours, and named as a *disputed row*.
- **Add-ons and implied work:** treated the same way (a majority of runs includes it, or it is listed as disputed).
- **Flag disagreement:** any row whose highest run is more than 30% above its lowest, and any measure list or class that differs between runs. These are the places where the requirements are ambiguous; add each to the pointers and blockers with what would settle it.

## 4. Totals
- **Likely** = the sum of the reconciled rows (not the mean of run totals; the two should be close, and a gap over 3% means disputed rows matter).
- **Bid** = the mean of the runs' bids; **buffers** = bid minus likely. **Sensitivity (no cap)** = the mean of the runs' figures.
- **Run spread:** show each run's likely and bid, and (highest - lowest) / mean. If the spread of the likely total is above 25%, say so, name the biggest disagreeing rows, and recommend settling them with the user before quoting.
- **Confidence:** unchanged from the single-run rules. Say that averaging narrows the random part only.

## 5. Output
One estimate file as in `output-template.md`, with the header line "Averaged over N independent runs" and a **Run spread** section (a table of the runs' totals, the disputed rows and the flagged disagreements). Keep each run's file under `runs/`. Register one row in `estimates-register.md` with the number of runs.
