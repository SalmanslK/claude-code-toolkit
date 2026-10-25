# Measuring a new calibration set (Tier A)

Only needed when creating a new set from a team's repository. Saved sets (Tier S) need none of this. Everything below uses `scripts/` (Python 3 standard library, read-only `git log`).

**Spec availability (calibrate on spec-ready work only).** H must be the team's speed while it had specs to build from. Days spent waiting for specs, or on earlier modules because later specs were missing, are not build pace for the next project.
- **Ask** whether there were spec delays in the window. If yes, get the dates or the number of such days.
- **Cut the window** with `--until` to the last spec-ready date (as in an earlier set), or keep the window and compute **H spec-ready = (developer-days with a commit − spec-wait days) × hours per day ÷ modules**.
- **Per module, if available:** note the spec-ready date and the first code commit; use only modules whose spec existed before coding started for H and K.
- **Check K.** If K per size point is steady while H rose, the rise is non-module time (waiting, hardening), which supports excluding it.
- **Flag the set** `spec-wait` in `INDEX.md` when its window includes such days and they were not removed. Do not use a spec-wait set for H; its K may still be used.
- **For the new project,** never add waiting time to the hours. List spec delivery dates as a pointer and a blocker; the quote assumes specs arrive before each module starts.

**Per-module speed (the preferred way to measure H, for backend and web).** "Developer-days / modules started" (`measure_velocity.py --modules`) is a throughput figure. It mixes in shared and foundation work, modules still in progress, rework on other modules and days a ready spec sat unpicked, so it can be wrong in either direction (the reference web project: 45.2h by throughput, against a measured 21.4h median for a reference-data screen group once commit-days are capped at the declared team size, plus 22% shared work). Use `scripts/module_cycle.py` instead and treat the throughput H as a cross-check.
- **Spec-ready date** per module, from the requirements history (document versions, ticket dates), never guessed. For a front-end module it is the **latest** of the spec, the design and the backend API it needs.
- **Pick-up** = first commit on the module. **Pick-up lag** = pick-up − spec-ready is reported and **never charged** to build time.
- **Done** = the **last feature commit** (subject not fix, bug, defect, revert or hotfix). Merge dates are not used, because a late merge says nothing about build time.
- **Effort, not calendar time.** Each developer-day is split equally across the modules its commits touched; a day touching no module is **shared work** (foundation, design system, tooling). Calendar span is shown but not priced: parallel modules overlap.
- **Settled** = done at least 7 days before the window end. Unsettled modules are lower bounds; say so, and never average only the settled ones when they are the easy ones.
- **Team size.** Pass the declared team size over time (`--team-size 2026-08-27:3,2026-09-28:2,2026-10-12:1`). Each week's commit-days are capped at FTE × working days (weight = capacity ÷ commit-days, never above 1). The script prints a weekly table of authors, commit-days, declared FTE and weight; many more authors than FTE is the sign to ask. Parallel developers on parallel modules are already handled by splitting a day across the modules it touched.
- **Cap limits.** The cap gives every author of a week the same weight, so it cannot tell a part-timer who commits daily from a full-time developer, and it drops commit-days that may have been real work by people left off the declared team. It also sits beside the 15% overhead, which covers days with no commit; both are assumptions. So the capped figure is the base only when the user has declared the team, and **the uncapped figure always goes beside it** (§9).
- **Cap H on the same commit-days as H.** Run `measure_velocity.py --team-size ... --modules N` and price with the printed **H capped**. Never multiply an uncapped H by a cap factor measured on another day set: on the reference project the factor 0.7805 (98 all-path days) applied to 27.6h gave 21.5h, while the same cap on the 90 spec-ready days gives 75.5 days and H = 23.2h.
- **Fit K under the cap, never scale it.** Run `module_catalogue.py --team-size` with the same schedule so K, σ, min, max and α are fitted on the same capped hours. Multiplying K by the cap factor is wrong: on the reference project it gave CRUD 0.85 against a fitted 0.97.
- **Steady state.** `--steady-from <date>` also prints class medians for modules picked up after the shared component library existed. They are a **floor** for later screens of the same project (the reference web project: 8h per event/workflow group, 2h per report screen), not the base for a greenfield estimate, because early modules also build the library; the base is the all-module median plus the foundation row.
- **Spec-first modules** (picked up before the spec was ready) are excluded from the pace.
- **Rework** = fix commits and effort after done; keep it as its own number.
- **Price by class, not by one H.** Report the median and P20–P80 effort per class (reference-data CRUD, entity, event/workflow, report screen). Use those for rows of the same class; use the ratio × H table only for classes with no measured module.
- **Shared work** is measured once (and by week: the first weeks are the foundation) and priced as the foundation row, not spread over the modules.
- **Check the file mapping:** module code that lives outside the module folder (for example `packages/core/src/services/<module>`) must be mapped to the module in the config, or the module looks cheap and the shared work looks large.
- Save the result as a set (`<team>-<date>-per-module`) with the config and spec-date files kept in `references/measure-configs/`.

**Web pace (measured front-end sets).** A set may carry a web column. When the user gives a front-end repo, measure it the same way as a backend repo: `measure_velocity.py --repo <fe-path> --since <AI-first date> --modules <screen slices>`. A web "module" is one screen group with its own route, components and tests (list + detail + form for one entity counts as one). Record in a new set: web H (hours per module), simple-screen and complex-screen hours if the history allows, and the foundation share. Then:
- price web rows from the **measured** hours per simple and complex screen instead of the 0.10–0.20 and 0.25–0.40 × H ratios, and the measured foundation instead of 1.5–2.0 × H;
- the 30% "no measured pace" buffer on web rows drops to the known-pattern class (22%);
- if the measured screen cost is **higher** than the ratio table, use the measured cost (never below the measured unit cost);
- widen confidence by 10 points if the front-end team differs from the backend team in the set.
Until a web set exists, say so in the file and keep the ratios (on the backend H) and the 30% buffer. **Web cost has a large up-front foundation** (reference project: about 140h of shared work in the first two weeks after the team-size cap, 22% of all hours) and a high fix share (about 50% of commits), so a ratio × backend-H web column understates the cost; always prefer a measured per-module web set. For mobile with no set, use the web set as a labelled proxy (see the personal overrides).


**Counting modules (Tier A).** A module is one feature slice with its own data, endpoints or screens, and tests: about one epic or plan.
- Count it **from the code** as well, at the **lowest folder level that holds a whole slice** (e.g. `Features/<Area>/<Slice>`, not `Features/<Area>`). Count only slices **created inside the window**. A sub-folder counts only if it has its own data, its own endpoints or screens, and its own tests. Sync handlers or jobs that plug into one framework count as one slice.
- If the user's count and the code count differ by more than 20%, compute H for **both** (skip a count of 0). Price with the code count, and show the other as a range in the file.
- Count the same way when pricing: one priced "module" = one such slice.

**Window.** Set `--since` and `--until` to the period that produced the counted modules, starting no earlier than the AI-first date. Include the foundation built in that period; that is how the ratios were calibrated. Keep every human author.
- Read the script's per-month table.
- Months with almost no commits are gaps; say so.
- If the first months are mostly setup (more than about 30% of the window), say so.

**Team and freshness.**
- Ask who is on the team, and pass anyone else with `--exclude-author`. Shared repos inflate H. **Default if unanswered:** every author is on the team.
- If the last commit is more than 4 weeks before today, ask whether recent work lives elsewhere. Fetch only if the user allows it. **Default if unanswered:** assume none, and say so in the file.
- The script's window starts at the first commit on or after `--since`; that date is shown, not the `--since` date.

**Verify H before using it.** The reference AI-first team's H is about 25h, and Tier C gives 50 × factor.

**H passes the check** when it is within 12–60h **and** at most 1.5× the Tier C H for the team's stated AI use.

**If H fails:**
1. Recheck the window. Does it start before the AI-first date? Does it include gaps or other teams' authors?
2. Show the user the code count. If they confirm a corrected count, re-run with it. If they cannot answer, go to step 3.
3. **Still failing, or the code count of new slices is below 5** (a mature repo, where the window is mostly enhancements and fixes): do not price from the measured H. Use the **fallback H = the Tier C H one AI-use level lower** than stated: AI-first → 35, mixed → 42.5, light → 50.
   - The measured evidence says the team is slower than the stated level. Maintenance work dilutes per-module figures, so the fallback is the defensible middle.
   - Show the measured H values as a range, set confidence to ±40%, and recommend Tier B (actual hours for 3 recent items) to firm it up.
4. **H below 12:** use 12.

**If H passes,** widen the confidence by 10 points (once, not per reason) when any of these is true:
- the module count is unconfirmed;
- the fix share is above 25%;
- `references/calibration-log.md` has fewer than 3 shipped rows for this team. The tier's figure is the confidence in **H**. Most ratios are **A** (assumed), and until actuals are logged nothing has tested them against this team, so the estimate is less certain than H.

**What H counts (Tier A).** The script counts the days each developer made at least one commit, multiplies by `--hours-per-day` (default 8), and adds `--overhead` (default 15%) for days of design, review or QA rounds with no commit. A team that often goes days without committing is undercounted; raise `--overhead` and say so. Either way, state the assumption in the file.

**"Never cut the base below the measured unit cost" applies only to an H that passed.**

**Reference catalogue and K (Tier A, with 8 or more finished slices).** Run:

`python scripts/module_catalogue.py --repo <path> --since <AI-first date> [--config <file>]`

- **What it measures.** Hours per module come from git, rework included, split across the modules each developer-day touched. Size comes from the code. It prints K per class, the platform share α already inside K, the spread σ, the min and max multipliers, the 80% bid factor, and the first-of-kind factor F.
- **The config.** The defaults fit a .NET `Features/<Module>/` layout. For any other layout or stack, write a config (`--help-config`) that says where modules live and how to count their endpoints, entities, rules and links. It also names:
  - each module's class (`classes`);
  - infrastructure slices and unfinished work to leave out (`exclude`);
  - the module that set the team's patterns (`first_of_kind`). It usually costs 2–3× and would inflate K.
- **What to check.** Modules started within `--settle-days` (default 14) of the window's end are left out, because they haven't had their rework rounds.
  - A class with fewer than 3 finished modules has no K: price it from the ratio table.
  - If the catalogue's total hours differ from `measure_velocity.py` by more than 5%, the module mapping is missing files. Fix the config.
- **Spec-to-code factor c.** Size for new work is counted from the spec, but K was fitted on code. Take 2 or more modules whose plan or spec was written **before** their code, count S from that early version, and set c = median(code size ÷ spec size). **Default if unmeasured:** c = 1.1, and say so.

