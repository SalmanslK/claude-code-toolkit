---
name: backend-development-history
description: >
  Use when the user asks about the backend's delivery history rather than a single day — when a module was
  started, finished, deployed to DEV or QA, who built it, how long it took, what rework followed, what the
  product team delivered and when — or asks to build, refresh or check the backend development history /
  delivery timeline / project history tracker or its Project Status roll-up. Works from project inception to
  today in any backend repository, into private files outside the repository. Not for day-by-day activity
  (use team-daily-activity), the user's own standup log (daily-scrum-updates), or "what is left" in the
  project: the repository's Book answers that (project-progress, the feature index and each plan's tasks),
  and pending-work-items holds asks of people.
---

You keep **the user's private, external record of how the backend was delivered**: every module from
requirement to QA, with the evidence for each date. **Accuracy over completeness.** A wrong date with a
confident label is the one failure this file cannot afford. `Not evidenced` is always an acceptable value.

**Must hold (read first):**
- The files are private. The rules in
  [shared mechanics §1](../daily-scrum-updates/references/shared-mechanics.md#1-the-private-file-rule)
  apply: never commit them, never put them in a repository, stop on `BLOCK`, and use read-only git.
- **Never modify anything inside the repository.** This skill reads the repository and writes two external
  files.
- **The ledger records environment, date, branch and commit only.** Never copy a host, port, path,
  credential or `.env` value.
- **A rebuild announces what it will overwrite and waits for a yes.**

## Quick reference

| Invocation | Behaviour |
|---|---|
| `/backend-development-history` | First run: the baseline from inception. Later: incremental from §Scan state |
| `... status` | Read-only: paths, scan state, module count, open gaps (`standup_evidence.py status --log history`) |
| `... report` | Regenerate only the Project Status roll-up (§Step 6) from the history file and the repository's docs |
| `... module <name>` | Re-derive one module; report the diff before writing |
| `... rebuild` | Re-derive everything, after a yes. Open-gap answers and `previously:` notes survive |
| `... dir=<path>` | `--dir <path>` for this run only |

The script is `python ~/.claude/skills/daily-scrum-updates/scripts/standup_evidence.py`. Its commands:
[shared mechanics §3](../daily-scrum-updates/references/shared-mechanics.md#3-the-script).

## Configuration

The keys are in [shared mechanics §2](../daily-scrum-updates/references/shared-mechanics.md#2-configuration-claudedaily-scrum-updatesconfigjson).
Names come from `authors`. The two `deployment` keys matter here, and both are **set by the user, never
inferred**:
- `integrationBranch` is where PRs land. Call it `<int>` below.
- `mergeDeploysTo` is the environment a merge into `<int>` reaches by team convention. `null` means a merge
  proves nothing about any environment.

Output files go in the configured directory:
- `<Project>-Backend-Development-History.md`: the ledger, §File structure.
- `<Project>-Project-Status.md`: the roll-up, §Step 6. It is **regenerated whole on every run** and never
  edited by hand.

## Step 1 — Map the project's evidence sources (first run; reused after)

Find this repository's equivalent of each source and record it in the file's **Evidence mapping** block.
Reuse that mapping later, and re-check it only when a mapped file is gone. A source that does not exist feeds
`Not evidenced`, and you say so once.

| Source | Feeds | How to find it |
|---|---|---|
| **Feature index**: one row per module with its status | Module list, status check, blockers | Status table in a project doc; `CLAUDE.md` or `README` usually names it |
| **Plans folder**: one design doc per feature | Module list, design start, dependencies | Per-feature `.md` files with a template (template excluded) |
| **Requirements history**: dated spec revisions | Product delivery dates | Changelog of FSD/spec versions; `V<n>` file names |
| **Defects log** | Rework; "verified on DEV/QA" corroboration | `defects.md`, `bugs.md`, an issue export |
| **Deploy runbook / test record** | Corroborating deploy dates | Deploy plan, e2e/smoke record, release notes, tags |
| **Deploy transcripts** (machine-local) | **The deployment ledger** (§Step 4) | `standup_evidence.py deploys` |
| **Git** | Start, completion, developers, PRs, active days | `standup_evidence.py merges`, `pr-authors` |

**Read docs from `origin/<int>`** (`git show origin/<int>:<path>`), not the working tree, whenever
`git status --porcelain` is non-empty or a merge is in progress. Record the revision in Scan state.

## Step 2 — Identify modules

There is one entry per **meaningful unit of backend delivery**: every plan except the template, plus anything
the feature index lists that has no plan. Infrastructure counts when it has a plan or a PR of its own. A
typo, doc fix, version bump or single small fix never gets an entry; it is a rework row on its module, or
nothing. Name entries by the plan's product-facing name and keep a `Plan:` pointer.

Infrastructure that grows without a plan (CI gates, tooling) gets one entry. Its completion is **the PR that
made it operational**. Later growth goes under Milestones, and you say which PR you took.

**Locating a module's work** means using all three of these, because they overlap:
- `merges --since <date>` gives PRs by branch name.
- `git log --branches --remotes --no-merges -- <module paths> <plan>` gives commits on its code and plan.
  Globs do not cross `/`, so name the project directories (list them once with `ls src tests`).
- `pr-authors <merge> <module paths>` gives authorship inside each PR, counting only that module's paths.

A PR belongs to a module when its branch name or at least half its changed files point at it. A PR spanning
modules is listed on each with `(shared)`.

## Step 3 — Derive each field

Every date carries a **typed evidence pointer** and a **confidence**. **All dates are PKT**, the offset
[shared mechanics](../daily-scrum-updates/references/shared-mechanics.md) sets once (`utcOffset`). A merge at 19:11 UTC is the next PKT day even when the plan copied the UTC day. That is the same
instant, not a conflict, so a later run must never "correct" it back.

| Field | Rule | Confidence |
|---|---|---|
| **Product delivery** | The spec revision whose changelog first specifies this module's section: `first seen in our snapshot V<n> (<date>)`. Delivered in pieces: the first revision specific enough to build, and the partial and later revisions on one line | Confirmed when the changelog names the section; Inferred when only the snapshot has it |
| **BE start** | Earliest of the plan's first commit (`design start`) and the first code commit (`code start`). Record both when they differ: the gap is often a BA wait | Confirmed |
| **BE complete** | The PR merge into `<int>` that made the module usable, corroborated by the plan's or index's "built" marker. **Never a commit date.** Unmerged has none | Confirmed |
| **Developer(s)** | Share of the module's commits in its PRs (`pr-authors ... <module paths>`): `listed (>=20%)` or a PR of their own. Doc-only commits do not count. The merger is listed separately as `Reviewed/merged by` | Confirmed |
| **Duration** | Always both: `calendar: <n> days (<start> → <complete>)`, counted inclusive, and `active: <m> days` (distinct PKT dates with a non-merge commit on it). **Never person-hours.** Open: `<n> days so far` | Confirmed |
| **DEV / QA deployment** | **Derived, never typed.** (a) Convention: if `mergeDeploysTo` names the environment, it was reached on BE complete, **or on that environment's first ledger row if later** (nothing deploys before the environment exists). (b) Ledger: the first row per environment whose commit has the completion merge as an ancestor (`git merge-base --is-ancestor <merge> <deployed>`). When both exist, show the ledger date and note any gap over a day. A row that deployed the module's own branch before merging: `<env> (branch build, pre-merge) <date>`. Other environments come from the ledger only. A SHA not in local history: `deployed <sha> — not in local history; cannot place` | **Confirmed** from a ledger row; **High Confidence** from the convention alone (`per convention: merge = <env>`); a doc saying "verified on …" corroborates but never stands alone; otherwise `Not evidenced` |
| **Rework** | A fix PR landing on the module after completion, or a top-severity defect. Doc-only corrections excluded. One row per fix PR | Confirmed |
| **Blockers / dependencies** | The plan's dependencies and the feature index; a blocking BA question with its answer date | Confirmed if a doc says so; else omit |
| **Status** | **Derived:** `Planned` → `In Progress` → `Completed` (merged) → `DEV` → `QA` (ledger proves) → `Released` (release evidence only). `Blocked` when the index or plan says so today | — |
| **Confidence** (entry) | The lowest among dates **that have a value**, written as e.g. `Confirmed (QA not evidenced)` | — |

**The confidence vocabulary has exactly four words:**
- `Confirmed`: a pointer a reader can open to see the fact.
- `High Confidence`: two independent sources agree, but neither is direct proof.
- `Inferred`: one indirect source, with the reasoning stated.
- `Unknown`: no evidence; the field reads `Not evidenced`.

**Conflicts are recorded, not resolved.** Write
`Conflict: <A per source> vs <B per source> — current reading: <which and why>` and set Inferred.

Evidence pointers are compact and grep-able, never prose:
- `PR #64 (82c749b, 2026-09-16)`
- `commit 98abd71 (2026-09-16)`
- `docs/defects.md D97`
- `docs/plans/<plan>.md §Status`
- `deploy 2026-09-14 DEV → f2981c3 (local session)`
- `Confirmed (user, 2026-09-18)`

## Step 4 — The Deployment ledger

Run `standup_evidence.py deploys` (or `deploys --since <transcript watermark>` on an incremental run). It
finds each deploy report in this repository's transcripts by its `Environment:` / `Branch:` / `Commit:`
block. The nearest verdict line above the block decides what the report says.

**Counted as deploys** (K16; old and new wording):
- `Deployment complete.` (old);
- `Deployment complete — smoke passed.`;
- `Deployed — …` (smoke skipped, did not run, failed, passed in part);
- `Reverted to <sha> after …`;
- the assistant's relayed `Deployed to <ENV> — …`.

**Discarded:**
- `NOT deployed — …` and `Deploy FAILED — …`;
- template echoes and line-numbered file reads.

Rows are deduplicated on (environment, commit), keeping the earliest. Each row prints as
`DEPLOY <PKT date> <time> <env> <branch|-> <commit> | <verdict> | session <id>`.

- A row with `smoke FAILED` or `did not run` still deployed that commit. Show the verdict in the Evidence
  cell; never upgrade it.
- **`CANDIDATE` lines** have the fields but no verdict above them. Read that session before using one. If it
  shows a healthy deploy, record it as `(relayed; Inferred)`.
- **Deploys run by hand** (a runbook followed step by step) print no block. Recover them from the session
  only when it shows a successful build followed by a healthy `/health/ready`. Record them as
  `(hand-run; SHA from checkout)` or `(hand-run; SHA not captured — Inferred)`.
- Corroborate with a doc where you can (the e2e record's last run, a defect's "verified on") and cite both.
- Ledger row: `| <PKT date> | DEV/QA | <branch> | <commit> | deploy … (local session) [+ doc] | modules first reaching this env |`.
- **This evidence is machine-local** (say so once in the Overview). A missing row means "no local run
  found", not "never deployed". The convention's environment falls back to the merge date at High
  Confidence. Any other environment reads `Not evidenced` and becomes an Open gaps question.

## File structure

```markdown
# <Project> — Backend Development History

## Project Overview
- Project / Backend / Source repository / Tracking started / Last updated / Purpose
- **Evidence mapping:** one line per source (`none` where absent); deploy transcripts are machine-local

## Delivery Timeline
| Module | Requirement | Product delivery | BE start | BE complete | Developer(s) | Duration (cal / active) | DEV | QA | Status | Confidence |

## Detailed History
### <Module>
- **Requirement / Product delivery / Backend start / Backend completion / DEV deployment / QA deployment / Confidence:** always present
- Developer(s) / Duration / Milestones / Rework / Dependencies / PRs / Key commits / Notes: only with content

## Deployment History
| Date | Env | Branch | Commit | Evidence | Modules first reaching this env |

## Significant Rework / Bug Fix History
| Date | Module | Fix | Developer(s) | PR | Defects | Notes |

## Open gaps
- [ ] <Module>: QA deployment — no local deploy run found. When did it first reach QA?
  <answer here>

## Update History
| Date | Changes |
**Scan state:** <int>=`<sha>` · transcripts≤`<ISO ts>` (the `WATERMARK` line) · docs=`<sha>` · open=`<branch>@<sha>`, …
```

- **Seven fields are always present per module**, so an absence is visible. Every other field appears only
  when it has content.
- **Empty values use exactly three words:** `Not evidenced` (looked, found nothing), `Not available` (no such
  source), `Not applicable`.
- One line per fact. Reference a plan, PR or FSD; never paste it. Timeline cells hold dates only, and the
  pointer lives in the section.
- **Milestones:** at most 5 turning points. Fixes never go there; they live once, in the Rework table.
  **Key commits:** at most 6.
- Developers under the 20 % line who made a material change go in Notes.
- `open=` lists every unmerged branch behind an `In Progress` module, with its tip. Drop it once the module
  completes.

## Step 5 — Update strategy (every run after the first)

1. Read the file, and parse Scan state, modules, ledger and open gaps.
2. **Consume answered gaps first.** Text under an open gap becomes the field's value, with
   `Confirmed (user, <today>)`. Remove the gap and log it.
3. **What changed since Scan state:**
   - `merges --since <scan date>` for new PRs.
   - `git log <sha>..origin/<branch>` for each `open=` branch.
   - Branches with commits after the watermark mean new in-progress modules.
   - `git diff --name-only <docs-sha>..origin/<int> -- <mapped docs>` lists the docs to re-read; re-read
     only those.
   - `deploys --since <watermark>` gives new ledger rows.
4. Re-derive the derived fields (status, DEV/QA, duration) for **every** module.
5. Change evidenced fields **only for stronger evidence**: Confirmed beats High Confidence, which beats
   Inferred. Keep the old value as `previously: <value> (per <pointer>)`.
6. Never delete a module. A vanished plan gets `Status: Withdrawn` and a note.
7. Append one Update History row and rewrite Scan state.
8. Re-read the file immediately before writing, in case a concurrent run wrote it.

On the first run, steps 1–2 do not apply. Say it was a baseline and which sources were found.

## Step 6 — The Project Status roll-up (every run, last; and `report`)

`<Project>-Project-Status.md` answers, for whoever owns the date: **how much is done, and what the
remaining work is waiting on.** It is derived from the history file and the repository's docs, and
regenerated whole. **It never becomes a second task list.** The repository's Book (the feature index and
each plan's Tasks, kept current by `/project-progress`, plus its generated *Open tasks* table) owns "what is
left". This file counts it and links there.

1. **Header:**
   - the as-of PKT time and the `origin/<int>` SHA;
   - where the roll-up is regenerated from;
   - the release plan's committed dates, with days to go-live.
2. **The numbers:** one table of `Done | Left | Total | Done %`, covering:
   - modules: on QA proven, on DEV only, tooling;
   - FSD sections built versus empty;
   - phases and release iterations;
   - PRs merged versus branches in flight;
   - defects by severity;
   - BA questions;
   - the test count, from its owning doc;
   - elapsed days versus days to go-live.

   Every number names its source. **When a heading's count disagrees with the rows under it, print both.**
3. **Done:** modules by phase, with the environment each has *proven* reaching and the last proven deploy.
   Say "by convention only" where that is the case.
4. **Left — blocked:** each `Blocked` row in the feature index, with its FSD section, the index's own reason
   (quoted) and its release slot.
5. **Left — unblocked:**
   - open defects by severity, from `defects.md` at `origin/<int>`;
   - branches in flight (unmerged, with commits): what each is for and who is on it;
   - for remaining tasks, **a link to the Book's Open tasks table**, not a copy.
6. **Reading it:** at most three sentences on what can start tomorrow and which decisions are not
   engineering's.
7. **Update history:** one row per regeneration, with the headline changes since the last one.

The numbers come only from sources the ledger trusts. **Blocked means the feature index says so today.** A
defect fixed on an unmerged branch is still open. Never move a row from Blocked yourself: the index changes
first.

## Output

```
Updated `<Project>-Backend-Development-History.md` at <path>   (baseline | incremental)
Regenerated `<Project>-Project-Status.md`: <done>/<total> modules · <open> defects open · <blocked> blocked
Discovered:  <n> modules (<k> new), <p> PRs, <d> deploy runs (<e> DEV, <q> QA), <c> candidates
Added / Updated (old → new, why) / Deployments / Uncertain (field — why) / Open gaps: <n>
Manual input needed: yes/no — <what>
```

`status` prints the script's status and the open gaps, and writes nothing. `report` rewrites only the
Project Status file and prints its numbers table.

## What next

- To see what is left, run **project-progress** in the repository first, so the Book's Open tasks are
  current, then `report` here.
- Use **team-daily-activity** for who did what on a given day.
- For an answer only a person can give (an open gap), use **pending-work-items** to track the ask.
