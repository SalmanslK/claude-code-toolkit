---
name: estimating-ai-assisted-work
description: Use when asked for effort estimates, ballpark hours, buffers, or a phase, release or backlog sizing (backend, web, mobile) for a team that builds with AI coding tools — "estimate these features", "how many hours for phase 2", "add buffer", "are these too high", "verify against AI trends", "minimum hours to win the bid", "compare scopes in a summary" — for any project, stack or team, with or without git history.
---

# Estimating AI-Assisted Work

## Overview

Price every item from the team's own measured pace, in one of two ways:
- **K × S**, when the team has built at least 3 modules of the item's class. **S** is the item's size (endpoints, entities, rules, links to other modules). **K** is the hours one size point cost this team, measured from git with rework included.
- **Ratio × H** otherwise. **H** is the team's measured hours per module, and the **ratio** comes from a fixed table, by item class.

Report every item as **min–max (likely)**. The likely figure is that row's median outcome (the list total is the "middle estimate"; see §5 statistical status), so never call it "optimal" or "max".

Never start from a conventional estimate and take an "AI discount" off it; for an AI-first team that lands about 2× too high. Known-pattern work gets **one pooled factor** for the whole list. Risks that hit every item at once get **separate buffers**, each saying what shrinks it. The fixed rules below (midpoints, a decision order, counting rules) are what make two runs on the same input land close together.

## Pricing posture (read before intake)

**Default posture: competitive minimum.** The market for AI-first teams is won on the lowest realistic hours, so the figure to quote is the **likely (median) build hours of the minimum version of every requirement**, on the **newest spec-ready measured pace for the right team and column** (never an older, faster set swapped in only for a lower number; if the user names an older set, use it and show the figure at the newest set beside it). Uncertainty is never hidden in the base. It goes in the **buffers, assumptions and blockers**, shown separately, and they make up the bid.

**What legitimately lowers the base** (use all of these, and say which were used):
- Price each requirement at its minimum version (§3, outcome-only rows and conditional wording).
- Read-only is the default for any outside system. Write-back, de-duplication, export, per-source single sign-on and embedded content are **add-ons** with their own hours, unless the document says the product must do them.
- Price only the columns that will be built.
- Use the newest measured set for the team that will build it, per column: a backend set for backend rows, a web set for web rows (§2, *Web*; measuring one: `references/measuring-a-set.md`). A measured column pace replaces the assumed ratios and removes the no-pace buffer.
- Reuse, only when a codebase is named and verified (§3).
- Price scopes as tiers (for example Lean, Full, Complete) from the same set and rules, so the client can choose and the figures stay comparable.

**What never lowers the base:** an H below the measured one; a different AI-use level or set chosen only for a lower number; summing per-item minimums; dropping a buffer while its blocker stands; unverified reuse; hiding an exclusion.

**What to show:** the **quote-minimum** (likely total), the **bid** (likely plus buffers), and the **pointers**: each blocker, ambiguity and assumption with what it could add and what closes it. State plainly that the likely figure is the median, so about half of similar work runs over it, and recommend that the assumptions and change-request terms go into the quote.

**Price the document's scope, not your own guess.** When the user supplies a requirements document or SOW, its in-scope section is the scope. Do not invent an MVP. If a smaller cut is useful, price it as a separate named scope next to the full one.

## 1. Intake

Ask once, in a single message, for anything missing that has no default below, then proceed on stated assumptions. Record every default used in the file.

| Input | Rule |
|---|---|
| **Feature list or requirements document** | **Always required from the user.** If the user gives a table of rows, keep its exact columns and row text. If the document has **no module or work breakdown**, the skill identifies it itself (§3, *Deriving the breakdown*). If there is no document and no list at all, stop and ask. |
| **Spec availability** | Ask whether specs were ever missing or late for the team being calibrated. If so, remove those days from H (§2, *Spec availability*; `references/measuring-a-set.md`). For the new project, state the assumption that specs are available when each module starts, and list spec delivery as a pointer; **delays waiting for specs are never priced into the hours.** |
| **Estimate columns** (BE, web, mobile) | User may state them. Otherwise infer them from the requirements (screens imply web, "app" or field use implies mobile, APIs imply BE), **propose them and ask the user to confirm** before pricing. |
| **Greenfield or existing code** | **Default greenfield.** Brownfield only if the user says so; then ask for the repo so the code can be searched. |
| **Calibration set** (§2) | Take from the user if named. If not, list the sets in `references/calibration-sets/INDEX.md` with their speed, recommend the closest by team, stack and AI use, and ask the user to confirm. The last option is to use no set (Tier C). |
| **Output location** | Default as in §9 and the personal overrides. |
| **Reuse source** | **Default none.** Do not ask. After pricing, add a short "How reuse could help" note (§3, *Reuse*): which rows are most likely to benefit (auth, audit, project foundation, CRUD scaffolding, design system), and the rough saving if a codebase were named. |
| **Mobile details** | Only if mobile is a column. Recommend one cross-platform app unless the requirements need native-only features; recommend store-compliance items (Apple sign-in alongside Google, in-app account deletion, privacy labels) if the app has accounts. Ask the user to confirm. |
| **Known blockers and decisions** | Take from the user if given. **After reviewing the requirements, also propose a multi-select list** of likely blockers, open decisions and missing prerequisites found in them (unknown APIs, undecided hosting, unwritten rules, unstated platform, data migration, and so on), so the user can tick, add or remove before pricing. Confirmed items go in §10 of the file. |
| **Level of AI use** | Required for Tier C. If no set is chosen, recommend AI-first (0.5) when the user says agents write most drafts, otherwise ask. |
| **Repo, window, module count** (Tier A) | Only when the user wants to measure a team or create a new set. Recommend a window that starts at the AI-first date, ends at the last commit, and holds at least 8 finished modules. |
| **AI-first date** | Needed only to measure a repo (Tier A) or create a set. Recommend the date of the first agent-written commit if the repo shows it. |
| **Team members and team size over time** | **Ask for the team size per period** (for example 3 developers, then 2, then 1) and for who is not on the team. Commit-days overstate effort when more people commit than are on the team full time (part-timers, reviewers, people from other products), so with a declared size, cap each week's commit-days at FTE × working days (`module_cycle.py --team-size`). **Default if unanswered:** every commit author is on the team full time, and say so; the estimate then carries a pointer that a smaller real team would lower the hours. |
| **Recent work elsewhere** | **Default: assume none**, and say so. |
| **Module classes and first-of-kind** | Default: classify from the code by §3; the earliest-commit module is first of its kind. |
| **Pricing posture** | **Default competitive minimum** (see above). If the user wants a safer quote, price the same rows and quote the bid instead; do not change the base. |
| **Source document** | If the requirements arrive as PDF or Word, extract the full text (`pdftotext -layout` for PDF) and read **all** of it: the in-scope section, the out-of-scope list, assumptions, dependencies, milestones and any stated price or timeline. The document's out-of-scope list is the exclusions list. A price quoted in the document is not used and not checked unless the user asks. |
| **Runs** | **Default 1.** Only if the user asks to estimate several times and average (maximum 3), follow `references/averaged-runs.md`: independent runs, reconcile by source section, average, show the run spread. Averaging removes random differences between runs, not shared errors, so it never narrows the confidence. |
| **Scopes to price** | One scope by default: the document's in-scope list at minimum versions. If the user names more (Lean, Full, Complete, phases), price each with the same set and rules in the same run, and write the summary pack (§9) so they sit side by side. |
| **Web (front-end) repo** | If the user has a front-end repo for the team, ask for a **local clone path** (the skill cannot authenticate to a remote host). With it, measure web pace (§2, *Web*; measuring one: `references/measuring-a-set.md`) and save it as a set. Without it, web uses the ratio table and a 30% no-pace buffer. |
| **Per-item requirements** | If a row has only a goal sentence, price it at the minimum version (§3) and list the missing detail in the blockers multi-select. |

## 2. Calibrate H

Pick the highest tier available and record it in the file.

**Saved sets (Tier S).** `references/calibration-sets/INDEX.md` lists frozen measurements, each with its speed (H in hours per module, dev-days per module). Choose one as the base; **no repo is needed.** Use its H and, if it has one, its catalogue (K, F, σ, c). Record the set name in the file.
- Same team and stack: confidence ±25%. Different team or stack: ±35% (assumed; refine after logging actuals). **Same team** means the people who will build it also built the set; a different client on the same team and stack is still the same team, but a different team, even on the same stack, is not. When unsure, use ±35% and say so.
- To retrain, measure a repo (Tier A) and save the result as a new set from `_template.md`. Never edit an old set.
- Tier A and B below are how a new set gets created; Tier C is the fallback when no set fits.

**Spec availability.** H must be the team's speed while it had specs to build from. Days spent waiting for specs are not build pace. For the **new project**, never add waiting time to the hours: list spec delivery dates as a pointer and a blocker, and assume specs arrive before each module starts. A set whose window includes unremoved spec-wait days is flagged `spec-wait` in `INDEX.md`; do not use it for H (its K may still be used).

**Rules that hold for every set (the mechanics of measuring one are in `references/measuring-a-set.md`):**
- **Per-module speed beats throughput.** "Developer-days / modules started" mixes in shared work, unfinished modules and rework, so it is a cross-check only. Prefer a set measured per module (`module_cycle.py`): effort not calendar time, shared work counted once, pick-up lag never charged, done = last feature commit, spec-first modules excluded.
- **Cap by the declared team size, on the same commit-days as H.** Commit-days are capped at FTE × working days per week. Price with the printed capped H (`measure_velocity.py --team-size`); never multiply an uncapped H by a cap factor measured on another day set. Fit K under the same cap (`module_catalogue.py --team-size`), never scale it. The cap treats every author of a week alike and sits beside the 15% overhead, so the capped figure is the base only when the user declared the team, and **the uncapped figure always goes beside it** (§9).
- **Price by class** (median and P20–P80 effort per class) where a set has them; use ratio × H only for classes with no measured module.
- **Web.** Price web rows from the set's **measured** hours per simple and complex screen and its measured foundation, not the 0.10–0.20 / 0.25–0.40 / 1.5–2.0 × H ratios; the 30% no-pace buffer then drops to the known-pattern class (22%). If the measured cost is higher than the ratio, use the measured cost. Widen confidence by 10 points if the front-end team differs from the backend team in the set. With no web set, keep the ratios (on the backend H) and the 30% buffer, and say that web understates the cost (a measured set shows a large up-front foundation and a high fix share). For mobile with no set, use the web set as a labelled proxy (see the personal overrides).

| Tier | Source | Confidence in H |
|---|---|---|
| **A** | Same team's git history: `python scripts/measure_velocity.py --repo <path> --modules <n>` | ±20% |
| **B** | Actual hours the user gives for 3+ past modules, or 3+ rows in `references/calibration-log.md` | ±25% |
| **C** | No data: **H = 50 × AI factor**. The factor is 0.5 for an AI-first team, 0.7 for mixed use, 0.85 for light use; see `references/conventional-baselines.md` | ±40% |

**Measuring a new set (Tier A or B).** Follow `references/measuring-a-set.md`: how to count modules, choose the window and team, what H counts, and how to build the catalogue (K, F, σ, c) from a repo. Tier S needs none of this and no repository.

**Verify H before using it.** The reference AI-first team's H is about 25h, and Tier C gives 50 × factor.

**H passes the check** when it is within 12–60h **and** at most 1.5× the Tier C H for the team's stated AI use.

**If H fails:**
1. Recheck the window. Does it start before the AI-first date? Does it include gaps or other teams' authors?
2. Show the user the code count. If they confirm a corrected count, re-run with it. If they cannot answer, go to step 3.
3. **Still failing, or the code count of new slices is below 5** (a mature repo, where the window is mostly enhancements and fixes): do not price from the measured H. Use the **fallback H = the Tier C H one AI-use level lower** than stated: AI-first → 35, mixed → 42.5, light → 50.
   - The measured evidence says the team is slower than the stated level. Maintenance work dilutes per-module figures, so the fallback is the defensible middle.
   - Show the measured H values as a range, set confidence to ±40%, and recommend Tier B (actual hours for 3 recent items) to firm it up.
4. **H below 12:** use 12.

**If H passes,** widen the confidence by **10 points once** (a single +10 for all three reasons below, however many are true) when any of these is true. The assumed-ratio share in §4 is a **separate** +10, so the most H-level widening is +20:
- the module count is unconfirmed;
- the fix share is above 25%;
- `references/calibration-log.md` has fewer than 3 shipped rows for this team. The tier's figure is the confidence in **H**. Most ratios are **A** (assumed), and until actuals are logged nothing has tested them against this team, so the estimate is less certain than H.

**"Never cut the base below the measured unit cost" applies only to an H that passed.**

## 3. Classify and price

**Deriving the breakdown (when the document has no module or work breakdown).** The skill builds the rows itself, in this order:
1. Read the whole document: scope, requirements, features, user stories, screens, integrations, assumptions and out-of-scope lists.
2. List each distinct capability the document asks for, with its section number.
3. Group capabilities into **slices** (one module = its own data, endpoints or screens, and tests); parts that share one mechanism are one slice.
4. Give each row an id, a short name, the source section, and a class by the first-match rule below.
5. Treat the document's out-of-scope list as exclusions, and conditional wording ("where supported", "if agreed") as add-ons.
6. Mark every row **derived from §x**, list the derived rows for the user to confirm or change, and **proceed on them as stated assumptions** unless the user stops it. Keep the table so a later run can reuse it.
Never invent a capability the document does not mention.

Classify every item by the **first** rule that matches:
1. Holds or moves money, or depends on a third-party service's behaviour (payments, push provider, OAuth: its webhooks, callbacks and failures) → **third-party SDK integration**. A cloud key, secret or storage service used through a standard library is **cross-cutting infrastructure**, not this class.
2. Syncs data both ways with an outside system → **two-way integration**.
3. Reads from an outside system only → **read-only external lookup**.
4. Moves legacy data in → **migration**.
5. Adds a new kind of user or a new data-ownership boundary to existing code → **new identity or scoping dimension**. **Greenfield counts too:** when the document requires data to be visible by role, hierarchy or ownership across several modules (for example "a manager sees only their reporting line"), that rule is this class, priced once as its own row, even though no existing code is being changed. It is not cross-cutting infrastructure.
6. **Writes** state with transitions, locks or cross-module business rules → **workflow**.
7. Only reads, aggregates, traces or exports existing data, even across modules → **read-only aggregate**. Count one per **distinct measure named in the description** (a scorecard "from inspections, rejections and late deliveries" = 3), per report, or per trace direction. Storing a derived snapshot (monthly scores) is still this class. If it runs on a schedule, add **0.2 H** for the job. The job, aggregates and screens are composite parts of the same row. In a BE column, "list and detail views" are screen sub-features: their endpoints. **Counting rule (fixed, so two runs agree):** (a) list every distinct measure the document names, once each; (b) split the list into **simple counts** (one number or list of one entity with at most one filter, for example "assigned leads", "pending training") and **real aggregates** (combines two or more sources, a ratio, a time window, a trend or a score, for example "readiness summary"); (c) when unsure, a measure is a simple count; (d) a measure shown on several screens counts once; (e) write both lists in the file. Price a simple count at **0.1 x H, minimum 1h**, and a real aggregate at the ratio table rate. Simple counts that read the same entity share one endpoint: after the first, each further one is 0.05 x H.
8. Otherwise → **CRUD module** (a slice), or **screen sub-feature** (a single list, form or dialog).

**Row grouping (so two runs give the same rows).** When deriving rows from a document:
- One row per distinct **screen group or capability named in its own sub-section** (for example one per §2.2.x); never split one sub-section into several rows unless it names separate data sources.
- **Read-only measures that share one data source and one screen are one row** (classed by rule 7, one count per measure). Lists, search, filters and details over the same data are one row, not three.
- A row that has its own stored data and a create or edit action is a CRUD module; a row that only lists or views a stored log is a **screen sub-feature** (1h minimum, as in the table).
- Keep the pre-split text in the row so a later run can regroup the same way. A re-run that lands on a different row count by more than 15% should be compared by total, not by row.

**Composite items:** when the description names several parts, price the **sum of its parts**, each classified by the rules above. Never pick one class for the whole item. **Parts that share one mechanism are one part:** e.g. field encryption and its key service, or an outbox and its sender. Never price the same plumbing twice.

**Outcome-only rows** have only a goal or benefit sentence ("enable…", "improve…", "give customers…") and no spec. Price them at the **minimum version that delivers the outcome**, and show everything else as optional add-ons:
- **Every named thing gets its simplest form:** a record (CRUD) or a read-only view or report.
- **Workflow words** (schedule, calibrate, approve, assign, monitor, track completion, version, prorate) and **vague catch-alls** ("other records", "and more") become **optional add-ons**, each priced with the normal rules.
  - **Exception:** when that workflow *is* the outcome (e.g. "proactively notify about upcoming events" needs the scheduler), keep it in the base.
- **A count range** ("4–5 reports") is priced at the lower number; the rest is an add-on.
- **A capability that is the outcome itself** (a migration, an integration, offline sync, a new data-scoping rule, a named list of workflows) is priced in full.
- Rows with a real spec (fields, rules, screens) are priced as written. This rule does not apply to them.

**Missing prerequisites** (data, tables or infrastructure the item needs but the code lacks, such as an audit trail behind an "audit export") always go under **implied work**. Price the row as if the prerequisite exists. List a prerequisite only after searching the code for it, and name what you searched for in the file.

**Minimum-version rules for requirement documents (learned from a client SOW):**
- **Conditional wording is an add-on.** "Where supported", "if authorised", "where the source accepts it", "where agreed" and "as permitted" make the feature optional: the base is the version that works without it, the feature is an add-on with its own hours.
- **Outside systems are read-only unless the document requires writing.** A row that updates a record in an outside system and says "where the source accepts it" is a read-only lookup in the base and a two-way integration add-on (price the difference).
- **Hand-offs are screen pieces.** "Open in the source system" and "start or resume in X" are a link or a screen sub-feature, not an integration, unless the document specifies passing context both ways.
- **Shared measures count once.** Summary cards and a team overview over the same measures are one set of aggregates plus a filter.
- **Rules that nobody has written** (exception rules, matching rules, amendment windows) are priced at the simplest fixed version and listed as blockers; the buffer carries the risk.
- **K below the measured range.** If a slice's size is below the smallest module in the catalogue, K is being extrapolated. Price with K (it is the minimum), show the ratio-table figure beside it, and list it in the pointers. The pooled factor with n = 1 or 2 slices is wide (1.29 at n = 1); say so.
- **Same set across scopes.** If a scope was priced earlier on a different H, re-price it on the same set or state the same-basis comparison in the summary (hours scale by H ratio).

**Base with K (the item's class has a K from §2):**
- **Size:** count from the spec, plan or wireframes: S_spec = endpoints + entities + ½ × rules + ½ × links to other modules. The rules are the distinct validation and business-rule failures a request can return. Then S = c × S_spec.
- **E = K_class × S × F.** F = 1, except for an item that brings in a pattern the codebase doesn't have: then F is the catalogue's first-of-kind factor, or 2 if none was measured. F replaces the upper-quarter move below.
- **Check against the closest module.** Name the closest finished module of the same class and its scaled hours: hours_ref × S ÷ S_ref. If the two figures differ by more than 30%, find out why (a driver the spec doesn't list, a different class) and write it down. Price with E either way.
- **K includes the platform share α** (shared work divided over the modules). If the estimate also prices the foundation as its own row, K-priced rows carry some shared work twice, up to α ÷ (1 + α) of their hours. Say so in the file and give the size of it; it is small when few rows are K-priced.
- **Never apply a quarter-point move to E.** The size already carries the item's complexity.
- **Lists of sub-features (rows smaller than a module):**
  - group the rows into the slices they would be built as, and give each slice one class;
  - count S per row and sum per slice; E for a row is K × c × its S;
  - a row with no size of its own (a count label, filter parameters on a list endpoint) shows `in #<row>`;
  - say in the file that K vouches for the slice totals, not for single rows. A row with almost no drivers (an email send, a status) can price under 1h because its work is averaged into the slice.

**Base without K = ratio midpoint × H.** The one permitted adjustment is to the **quarter point** (midpoint ± a quarter of the range), never to the end:
- **Lower quarter** only when you can name existing **feature-specific** code that does part of the job (an external client, a sync framework, an export service), **or an established library that does most of it** (a cloud provider's encryption SDK, a mature job scheduler). Generic base classes every slice uses (base handlers, repositories) do not count: H already includes them. **The foundation row of the same estimate is not "existing code":** a gateway, SSO or project-foundation row priced in this list is already paid for by the "0.3 foundation counted once" in the lookup ratio, so it does not justify a lower-quarter move on later lookups. Only code that exists outside this estimate qualifies.
- **Upper quarter** only when you can name a pattern the codebase does not yet have.
- **Arguments both ways → midpoint.**

Write the reason in the file. Integration rows include their own foundation; take the lower quarter when that foundation already exists.

| Class | BE ratio × H | Basis |
|---|---|---|
| Screen sub-feature (list, search, filter, form, dialog) | 0.04–0.16, minimum 1h | M |
| Simple count (one entity, at most one filter; see rule 7) | 0.1 each (0.05 for each further count on the same entity), minimum 1h | A |
| Read-only aggregate: one KPI or one report on an existing framework | 0.3–0.5 each | A |
| CRUD module, known pattern | 0.5–1.0 | M |
| Cross-cutting infrastructure (interceptor + table, outbox, scheduler, audit trail, field encryption, cloud key service) | 0.5–1.0 | A |
| Read-only external lookup | 0.7–1.3, plus 0.3 foundation counted once | A |
| Greenfield auth (sign-up, login, reset, one social provider) | 1.0–1.5 | A |
| Greenfield project foundation (repo, DB, CI/CD, environments, logging) | 1.0–1.5 | A |
| Backend release hardening and one regression pass (implied work; not in the likely or the bid, shown as a conditional total) | 0.5-1.0 | A |
| Third-party SDK integration (payments, push provider, extra OAuth provider) | 1.0–2.0 | A |
| Workflow module | 1.3–2.2 | M |
| New identity or scoping dimension | 2.5–4.0 | A |
| Two-way external integration | 2.5–4.0 | A |
| Legacy data migration | 2.5–4.0 | A |
| Offline sync | 3.0 BE + 5.5 mobile | A |

**M** = a measured instance behind it, **A** = assumed. Replace A rows from the calibration log once one ships.

**Web and mobile are priced from their own screens,** never as a multiple of BE.

| Mobile or web class | Ratio × H |
|---|---|
| Simple screen (list, detail, form, settings) | 0.10–0.20 |
| Complex screen (slot or date picker, camera or scanner, chart, native SDK UI, offline-aware form) | 0.25–0.40 |
| Greenfield app foundation (navigation, theme, API client with token refresh, error states, crash reporting, environments) | 1.5–2.0 |
| Store release and one regression pass | 0.5–1.0 |
| Piece of a screen (label, dialog, action, filter) | the BE screen sub-feature rate, 0.04–0.16, minimum 1h |

A 4-workflow greenfield mobile app usually totals **8–12 H** including its foundation. If your screen sum is far outside that, recheck it.

**Range for every row: min–max (likely).**
- **Likely:** the base, E. It is the median outcome: half of similar items take longer.
- **With a catalogue:** min = the catalogue's P20 multiplier × E and max = its P80 multiplier × E. (Measured on one team: 0.75 and 1.37.)
- **Without one:** min = the ratio range's low end × H and max = its high end × H. Scale both by the same quarter-point move as the base. A ratio with a single value (for example the simple count, 0.1) takes the catalogue's multipliers when a catalogue exists (0.67 and 1.33 on the reference project), otherwise 0.75 and 1.35, and the minimum 1h still applies.
- **Never sum the minimums into a project minimum.** The chance that every item comes in low together is close to zero: for 8 items it was 2% on the reference team. The total's range comes from §5.

**Reuse from an existing codebase: only when the user names one.** Otherwise skip it. The scoring method (drivers scored against the named codebase, reuse %, the 25% porting floor, never averaging with and without reuse) is in `references/reuse.md`.

## 4. Sanity check

Run every check that applies:
- **Per row:** no row above 4 H unless its class ratio is itself above 4 H at your H (migration, two-way integration, new scoping dimension, offline sync, foundation, auth, read-only external lookup). A CRUD-sounding row above 1 H means it is really a composite; split it.
- **Phase-sized lists (8+ items):** compare the total with the team's last phase (active days × hours). More than 2× for similar scope is almost always the "conventional minus AI" error.
- **Tier A or B with a passing H:** also price the list at Tier C. Landing above C means the H check was skipped. This does not apply when the fallback H was used.
- **Capacity:** base ÷ (people × productive hours per day) = working days. Say it, and flag it if it is implausible for the team.
- **Assumed-ratio share:** (separate from the +10 above) state how many base hours are priced from **assumed** ratio rows (basis A in the table, no measured module of that class) and how many from K or measured rows (basis M). Ratio × H scales with H by design, so the open question is whether the multiple holds for this team. If more than half of the base is on assumed rows, widen the confidence by 10 points (once), say so in the file, and put it first in the pointers.
- **Tier C:** compare with the conventional total × factor from `references/conventional-baselines.md`.
- **K pricing:** also price the K-priced rows with the ratio table. If the totals are more than 25% apart, a class or a size count is off; find it before writing the file. **Closest-module check:** compare each K-priced row with the nearest-size finished module of the same class from the set's catalogue (hours x S / S_ref). If the slice is smaller than the smallest measured module, the nearest comparators are bigger, so scaling down is extrapolation: price with K for the minimum, show the comparator figures, and list the row in the pointers. If a re-run of `module_catalogue.py` is possible (repo on the machine), use it; otherwise use the set file.

## 5. Buffers

**Known-pattern items share one pooled factor; every other item gets its own buffer.**

**Pooled factor for known-pattern items.** Their errors are independent and partly cancel, so the total's spread shrinks as 1/√n. With a catalogue, the 80% total is:

**ΣE_known × (1 + 0.84 × σ / √n)**

where σ comes from the catalogue. The factor is 1.10 for 8 items on the reference team.
- **n counts K-priced slices, not rows.** σ was measured per module, so 30 sub-feature rows in 3 slices give n = 3.
- **The pooled factor applies only to known-pattern work priced with K.** Known-pattern items priced from the ratio table keep a 22% per-item buffer: their error is larger and was not measured. Without a catalogue, every known-pattern item gets 22%.

**Per-item buffers for every other item.** Set them in a separate table, at the **midpoint** of the risk class, each with a "shrinks if…" condition. These risks hit every item at once, so pooling does not shrink them.

| Risk class | Range (midpoint) |
|---|---|
| Known pattern, the team's own code, **without a catalogue** | 15–30% (22%) |
| Requirements or permissions not yet written | 50–70% (60%) |
| External party (data owner, third-party API or SDK, partner team) | 50–75% (62%) |
| Novel design (offline, security model) | 50%; re-estimate after a spike |
| No measured pace for that column | The upper end of its other class |

- **Choosing the class:**
  - Any outside party it waits on → **external party**.
  - Otherwise, the item needs a rule, formula, attribution or conflict policy that nobody has written down → **requirements not written**.
  - Otherwise, its behaviour is obvious from the description and an existing pattern (e.g. "export X to Excel" where exports exist), even if the description is one line → **known pattern**.
  - Depending on another item in the same estimate is a dependency, not an outside party. List it in build order; it does not change the class.
  - A missing prerequisite does not set the row's class or block a lower-quarter move; it carries its own price and buffer under implied work.
- **One buffer per row**, even for composites, at the highest class among its parts. **K-priced parts stay in the pooled known-pattern factor**; only the ratio-priced parts of a mixed row take the row's higher class. This puts the risk margin on the part that carries it, not on the whole row.
- When an item fits several classes, take the **highest; never add them together**.
- **The bid:** known-pattern ΣE × the pooled factor, plus every other item's E and buffer. Show it next to the likely total (ΣE) and call it the **80% planning level, not a calculated probability** for the whole list.
- **Statistical status (state it in every file).** Only the K-priced slice has a measured spread (σ from n finished modules; σ = 0.41 from n = 18 is itself uncertain by about ±17%, and F rests on one module). The pooled factor 1 + 0.84σ/√n assumes independent, equal-sized errors; correlated errors would raise it. The other buffers (22%, 50%, 60%, 62%) are judgement bands. Each row's min–max is the P20–P80 of one module, not best and worst case. The sum of row medians equals the median of the sum only if spreads are symmetric (true for K rows, assumed for ratio rows). Call the middle figure the **middle estimate**, not the median, unless every row is K-priced. Rows are rounded to the hour, so columns can differ from totals by a few hours. Track draw-down weekly against both.
- **Implied work shared with another estimate:** count it once, and name the owner.

## 6. Research cross-check

Use `references/research.md`. If it is more than 6 months old, refresh it with a web search first. A team measured above the research gains keeps its measured costs. **Never cut the base below the measured unit cost.** The research supports buffers, not a smaller base.

## 7. Hidden work

List implied work the item list omits:
- tenancy or data-ownership retrofit;
- data migration;
- email or notification infrastructure;
- an integration foundation;
- greenfield foundation;
- store compliance;
- release and regression: price the backend pass at 0.5-1.0 x H and the web pass at the web set's measured regression hours (about 21h on the the reference web project set). Both are **implied work**, shown with a conditional total and not included in the likely or the bid.

Also list spec inconsistencies, blockers, decisions needed, and dependencies with build order. Mark items with no requirements as blocked. If the code was not visible, mark implied work as conditional.

## 8. Trimming (when asked to cut)

| Can trim | Never trim |
|---|---|
| Known-pattern buffers (no catalogue) once their dependency is done | The base, below the measured unit cost |
| External buffers by about half once the item is in hand (data, sandbox, API docs) | The pooled factor, below 1 + 0.84σ/√n |
| | External, security or novel-design buffers while the blocker stands |
| | Any buffer with no measured pace behind it |
| | A bid at the sum of the per-item minimums |

## Personal overrides (this copy only)

Project-specific paths, team declarations, set choices and the output folder come from the user.

## 9. Write the file


Where to write: a folder the user names wins, then the rule in `output-template.md`. Follow `references/output-template.md`. Reply with the path, the headline totals and the biggest blockers. **Every estimate file carries a sensitivity line** in its summary: the likely and bid totals again with no team-size cap (and any other assumed adjustment), beside the base, so a reader can see how much of the figure rests on the cap.

**Summary pack (one document for sharing).** Always write it when more than one scope was priced, or when the user asks for a summary, a comparison or "something for my manager". Copy `references/summary-template.md` to `<Project>-Summary-<YYYY-MM-DD>.md` in the same folder, fill every placeholder from the estimate files (do not invent figures), and delete the comments. The summary shows likely hours only: leave out the 80% bid and put buffers, blockers and ambiguities in the pointers section. **The figure never travels alone:** its scope note must say that the likely hours are medians (about half of similar work runs over them), name the file that holds the 80% bid, and, when a team-size cap was used, give the uncapped totals. Then run `python scripts/make_summary_pdf.py <file>.md` to make the PDF (needs the `markdown` package and Edge or Chrome). **Open every page of the PDF as an image and check it** before saying it is done: lists must not run together, tables must not split awkwardly, and no page should be nearly empty. `references/summary-template.md` and `.pdf` show the finished shape; **never price from its hours.**

`references/worked-example.md` shows one real team's numbers, for shape only. **Do not price another team from its hours.**
