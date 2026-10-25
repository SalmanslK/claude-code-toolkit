---
name: backend-development-history
description: >
  Use when the user asks about the backend's delivery history rather than a
  single day — when a module was started, finished, deployed to DEV or QA, who
  built it, how long it took, what rework followed, what the product team
  delivered and when, or "what is the current status of everything" — or asks
  to build, refresh or check the backend development history / delivery
  timeline / project history tracker. Works from project inception to today
  in any backend repository. For day-by-day activity use team-daily-activity;
  for the user's own standup log use daily-scrum-updates.
---

You are maintaining **the user's private, external record of how the backend
was delivered** — every module from requirement to QA, with the evidence for
each date. It is a historical tracking system: **accuracy over completeness.**
A wrong date with a confident label is the one failure this file cannot
afford; `Not evidenced` is always an acceptable value.

**REQUIRED BACKGROUND:** the sibling skills `daily-scrum-updates` and
`team-daily-activity` (same `~/.claude/skills/` directory) own the shared
mechanics: §Configuration and §Backup mirror (daily-scrum-updates), the PKT
date rules (`date -u -d '+5 hours'`, never `TZ=`), the read-only Git rule, and
PR authorship by commit count (team-daily-activity §Pass 2). Where this file
says "as in <sibling>", follow that section exactly.

---

## HARD RULE — private, outside the repository, never committed

- The history file is user data. **Never** let Git touch it, never create it
  inside a working tree, never gitignore it as a workaround. If the resolved
  path lands inside the current repo, stop and tell the user.
- **Never modify anything inside the repository** — no source, tests, docs,
  plans, requirements. This skill reads the repo and writes one external file.
- Every Git command is read-only: `git log`, `git show`, `git merge-base`,
  `git rev-list`, `git rev-parse`, `git branch -a --contains`, `git diff --stat`.
  No `fetch`/`pull`/`checkout` — if the clone looks stale, say so.
- **Never copy a host, path, port, credential or `.env` value out of a deploy
  transcript.** The ledger records environment, date, branch and commit only.

---

## Quick reference

| Invocation | Behaviour |
|---|---|
| `/backend-development-history` | First run: build the baseline from inception. Later runs: incremental — only what changed since §Scan state. |
| `/backend-development-history status` | Read-only: file path, scan state, module count, open gaps, sources mapped. |
| `/backend-development-history report` | Regenerate only the **Project Status** roll-up (§Step 6) from the current history file and the repo docs, without re-scanning Git or transcripts. Use when someone asks "where are we" / "what is done and what is left". |
| `/backend-development-history module <name>` | Re-derive one module's entry from all evidence; report the diff before writing. |
| `/backend-development-history rebuild` | Re-derive everything. **Announces what it will overwrite and waits for a yes.** Open-gap answers and `previously:` notes survive a rebuild. |
| `... dir=<path>` | One-off output directory override. Not persisted. |

---

## Configuration

Shared config `~/.claude/daily-scrum-updates/config.json`, resolved as in
daily-scrum-updates §Configuration: `directory`, `projectNames`,
`backupDirectory`, and team-daily-activity's `authors` map (email → display
name — use it for every developer name in this file).

This skill adds one key — the project's deployment convention:

```jsonc
"deployment": {
  "integrationBranch": "dev",          // where PRs land
  "mergeDeploysTo": "DEV"              // env a merge into that branch reaches by team convention;
                                       // null when merging deploys nothing
}
```

Set per user instruction, never inferred: on one project the user stated
2026-09-17 that code is on DEV once its PR merges to `dev` (the office server
tracks `dev`; the `/deploy-dev-qa` run follows the merge). Default when absent:
`null` — a merge proves nothing about any environment.

**Output files:** `<directory>/<Project-Name>-Backend-Development-History.md`
(the ledger, §File structure) and `<directory>/<Project-Name>-Project-Status.md`
(the roll-up, §Step 6 — **rewritten on every run**, never edited by hand).
Mirror both after every write as in daily-scrum-updates §Backup mirror; this
skill's own definition goes to `<backupDirectory>/backend-development-history-SKILL.md`
(never `SKILL.md`, which is the first sibling's backup).

---

## Step 1 — Map the project's evidence sources (first run; reused after)

Projects name things differently. Discover the current repo's equivalent of
each source below, record the mapping in the file's **Evidence mapping**
block, and reuse it on later runs (re-check only if a mapped file is gone).

| Source | What it feeds | How to find it | Example mapping |
|---|---|---|---|
| **Feature index** — one row per module with status/phase | Module list, status cross-check, blockers | Project-level doc with a status table; `CLAUDE.md`/`README` usually names it | `docs/project.md` Part 1 |
| **Plans folder** — one design doc per feature | Module list, design-start date, dependencies, deviations | Folder of per-feature `.md` with a template | `docs/plans/*.md` (`_template.md` excluded) |
| **Requirements history** — dated log of spec revisions | Product delivery dates | Section listing FSD/spec versions with dates and what changed | `docs/project.md` Part 3; `requirements/fsd/*V<n>.pdf` filenames |
| **Defects log** — numbered rows with dates | Rework/bug-fix history, "verified on DEV/QA" corroboration | `defects.md`, `bugs.md`, issue export | `docs/defects.md` |
| **Deployment runbook / test record** | Corroborating deploy and verification dates | Deploy plan, e2e/smoke record, release notes, tags | `docs/plans/deployment.md`, `docs/e2e-testing.md`; no tags, no release notes |
| **Local deploy transcripts** (machine-local) | **The deployment ledger** | `~/.claude/projects/<slug>/*.jsonl` containing `Deployment complete.` | 11 transcripts as of 2026-09-17 |
| **Git** | Start, completion, developers, PRs, active days | always | Bitbucket: `Merged in <branch> (pull request #N)` |

A source that does not exist feeds `Not evidenced` into its fields — say so
in the Evidence mapping, once.

**Read docs from `origin/<integrationBranch>`, not the working tree**, when
`git status --porcelain` is non-empty or a merge is in progress — another
session may be mid-merge with conflict markers in exactly the files you need.
`git show origin/dev:docs/project.md`. Record which revision the docs were
read at in Scan state.

---

## Step 2 — Identify modules

One entry per **meaningful unit of backend delivery**: every plan in the plans
folder that is not the template, plus anything the feature index lists that
has no plan. Infrastructure counts when it has a plan or a PR of its own
(auditing, multi-tenancy, file storage, deployment, CI gates). Never an entry
for a typo, a doc correction, a version bump, or a single small fix — those
are rework rows on the module they touched, or nothing.

Name entries by the product-facing name the plan uses. Keep a `Plan:` pointer
so the next run finds the same plan.

**Infrastructure that grows continuously without a plan** (CI gates, tooling)
gets one entry whose completion is **the PR that made it operational** (the
first time it gated or ran for real); later growth is Milestones, not new
entries or a moving completion date. Say which PR was taken as completion.

**Locating a module's work in Git** — use all three, they overlap. **Path
globs do not cross `/` on this Git**, so name the project directories
explicitly (list them once with `ls src tests`):

```bash
# branches and PRs named for it
git log --branches --remotes --merges --grep='pull request' --format='%h|%ad|%s' --date=short | grep -i '<slug>'
# commits touching its code and its plan
git log --branches --remotes --no-merges --format='%h|%ae|%ad|%s' --date=format:'%Y-%m-%d %H:%M %z' \
  -- 'src/<App>/Features/<Module>' 'src/<Domain>/<Module>' 'src/<Api>/Endpoints/<Module>' 'docs/plans/<plan>.md' 'tests/*/<Module>'
# authorship inside each of its PRs (as in team-daily-activity §Pass 2)
git log --no-merges --format='%ae' M^1..M^2 | sort | uniq -c | sort -rn
```

A PR belongs to a module when its branch name or ≥ half its changed files
point at that module. A PR spanning modules is listed on each with `(shared)`.

---

## Step 3 — Derive each field

These semantics are fixed so entries are comparable. Every date carries a
**typed evidence pointer** (§Evidence pointers) and a **confidence**.

**All dates are PKT.** Bitbucket stamps merges in UTC, and the plans and
feature index often copy that day — so a merge at 19:11 UTC is 2026-09-17 in
this file while the plan says 2026-09-16. That is not a conflict to record;
it is the same instant. A later run must not "correct" the PKT date back.

| Field | Rule | Confidence |
|---|---|---|
| **Product delivery** | The spec revision whose changelog entry first specifies this module's section — from the requirements history. Word it `first seen in our snapshot V<n> (<date>)`: the live spec may have had it earlier; the snapshot is what is provable. **When the spec arrived in pieces**, the timeline cell carries the date of the **first revision that specified it fully enough to build** (`2026-09-08 (V5)`); the earlier partial appearances and later amendments are listed in the section, one line. | Confirmed when the changelog names the section; Inferred when only the snapshot contains it |
| **BE start** | Earliest of: the plan's first commit (`design start`) and the first code commit on the module (`code start`). **Record both** when they differ — the gap between them is often the BA-question wait. | Confirmed |
| **BE complete** | The PR merge into the integration branch (`dev`) that made the module usable — the plan's own "built" marker or the feature index's status change corroborates which PR that was. **Never a commit date.** An unmerged module has no completion. | Confirmed |
| **Developer(s)** | Commit share inside the module's PRs, mapped through `authors`; ≥ 20 % of non-merge commits or a PR of their own to be listed. **In a PR that carries several modules, count only the commits that touch this module's paths** (`git log --no-merges --format=%ae M^1..M^2 -- <module paths>`) — a shared PR (#15 here carried seven modules) otherwise credits everyone with everything. Doc-only commits don't count toward the share. Reviewer/merger (`%ce` on the PR merge, when a different person) listed separately as `Reviewed/merged by`. Never from unrelated commits. | Confirmed |
| **Duration** | Two numbers, always both: `calendar: <n> days (<start> → <complete>)` and `active: <m> days` = distinct PKT dates with a non-merge commit on the module. **Never person-hours.** Open module: `calendar: <n> days so far`. | Confirmed (arithmetic on Confirmed dates) |
| **DEV / QA deployment** | **Derived, never typed**, from two inputs in this order. **(a) Convention:** if `deployment.mergeDeploysTo` names the environment, the module reached it on its **BE complete** date — the merge into the integration branch — **or on the environment's first ledger row, whichever is later**: nothing was deployed anywhere before the environment existed (eight modules here merged before the 2026-09-03 bring-up). **(b) Ledger:** the first Deployment-ledger row per environment where the completion merge is an ancestor of the deployed commit (`git merge-base --is-ancestor <merge> <deployed>`). When both exist, the ledger row's date is shown and the merge date is the fallback; when they differ by more than a day, note it. A ledger row that deployed the module's *own feature branch* before it merged is recorded too, as `<env> (branch build, pre-merge) <date>`. An environment the convention does not cover (QA here) comes from the ledger alone. Deployed SHA not in local history → `deployed <sha> — not in local history; cannot place`. | **Confirmed** from a ledger row; **High Confidence** from the convention alone (`per convention: merge to dev = DEV`); a doc saying "verified on DEV/QA" corroborates either but never stands alone; otherwise `Not evidenced` |
| **Rework** | Significant only: a **fix PR** landing on the module after its completion merge, or a defect the log ranks in its top severity band. Doc-only corrections excluded. One row per fix PR; defect ids in one cell. | Confirmed |
| **Blockers / dependencies** | From the plan's dependencies section and the feature index; a BA question the requirements log marks as blocking, with its answered date. | Confirmed if a doc says so; otherwise omit |
| **Status** | **Derived, never typed:** `Planned` (plan exists, no code commits) → `In Progress` (code, no completion merge) → `Completed` (merged) → `DEV` → `QA` (ledger proves) → `Released` (only with release evidence). `Blocked` overrides when the feature index or plan says so today. | — |
| **Confidence** (entry) | The lowest confidence among the dates that **have a value** — a `Not evidenced` deployment does not drag the entry to Unknown, or every module merged after the last local QA run reads Unknown and the column stops discriminating. Write it as `Confirmed (QA not evidenced)` so the gap stays visible. | — |

**Confidence vocabulary** — exactly these four: `Confirmed` (a pointer a
reader can open and see the fact), `High Confidence` (two independent sources
agree, neither is direct proof), `Inferred` (one indirect source, stated
reasoning), `Unknown` (nothing; the field reads `Not evidenced`).

**Conflicts are recorded, not resolved.** When two sources disagree (the
feature index says Built, Git shows no merge; a plan says one PR, Git says
another), write both in Notes as `Conflict: <A per source> vs <B per source> —
current reading: <which and why>` and set confidence to Inferred.

### Evidence pointers

One compact, grep-able form per source — never prose:

| Source | Form |
|---|---|
| PR merge | `PR #64 (82c749b, 2026-09-16)` |
| Commit | `commit 98abd71 (2026-09-16)` |
| Doc | `docs/project.md Part 3 "FSD V10" (2026-09-15)` / `docs/defects.md D97` |
| Plan | `docs/plans/mating.md §Status` |
| Deploy | `deploy 2026-09-14 DEV → f2981c3 (local session)` |
| User | `Confirmed (user, 2026-09-18)` |

---

## Step 4 — The Deployment ledger

Built from the local deploy transcripts. Each real `/deploy-dev-qa` run ends with a
block the deploy skill prints verbatim:

```
Deployment complete.
  Environment:  DEV
  Branch:       feature/order-checkout
  Commit:       f2981c3
```

- **Discard template echoes**: a hit whose Environment is blank or whose
  Branch contains `{` is the skill's own text being loaded, not a run. A hit
  that repeats this file's example (`f2981c3`) is this skill being loaded;
  dedupe removes it because the real run is earlier.
- **Deploys executed by hand** (the runbook run step by step in a session,
  not via the skill — here the 2026-09-03, 09-07 QA and 09-09 runs) leave no
  block. Recover them from the session: a compose build with exit 0 followed
  by a healthy `/health/ready`, and record `(hand-run; SHA from checkout)` or
  `(hand-run; SHA not captured — Inferred)`. Only a session that shows the
  health check counts.
- **The block is inside a JSON string** — `\n` (sometimes `\r\n`) escapes,
  not real newlines — so parse per matching line, not across lines:
  ```bash
  for f in ~/.claude/projects/<slug>/*.jsonl; do
    grep 'Deployment complete\.' "$f" | while IFS= read -r line; do
      printf '%s ' "$(basename "$f" .jsonl | cut -c1-8)"
      printf '%s\n' "$line" | grep -o '"timestamp":"[^"]*"\|Environment: *[A-Z]*\|Branch: *[^ \\"]*\|Commit: *[0-9a-f]*' | tr '\n' ' '
      echo
    done
  done
  ```
- Timestamp is UTC → +5 h for the PKT date.
- Dedupe on (environment, commit); keep the earliest.
- Corroborate where a doc lets you (`docs/e2e-testing.md` "last run", a
  defect row "verified on DEV/QA") and cite both.
- Ledger row: `| <PKT date> | DEV/QA | <branch> | <commit> | deploy … (local session) [+ doc] | modules first reaching this env |`.
- **This evidence is machine-local.** A deploy run from another machine is
  invisible; say so in the Overview once, not per row. A missing ledger row
  means "no local run found", not "never deployed": for the environment the
  convention covers, the merge date stands in at High Confidence; for any
  other environment the field reads `Not evidenced` and becomes an §Open gaps
  question.
- If the transcript directory does not exist for this repo path, the ledger
  is empty; say so once in the Evidence mapping and rely on the convention.

---

## File structure

```markdown
# <Project> — Backend Development History

## Project Overview
- Project / Backend / Source repository / Tracking started / Last updated / Purpose
- **Evidence mapping:** feature index → …; plans → …; requirements history → …;
  defects → …; deploy runbook → …; deploy transcripts → <slug> (machine-local);
  Git remote → … (one line each; `none` where absent)

## Delivery Timeline
| Module | Requirement | Product delivery | BE start | BE complete | Developer(s) | Duration (cal / active) | DEV | QA | Status | Confidence |

## Detailed History
### <Module>
- **Requirement:** …            ← always present
- **Product delivery:** …       ← always present
- **Backend start:** …          ← always present (design / code)
- **Backend completion:** …     ← always present
- **DEV deployment:** …         ← always present
- **QA deployment:** …          ← always present
- **Confidence:** …             ← always present
- Developer(s) / Duration / Milestones / Rework / Dependencies / PRs /
  Key commits / Notes            ← only when they carry something

## Deployment History
| Date | Env | Branch | Commit | Evidence | Modules first reaching this env |

## Significant Rework / Bug Fix History
| Date | Module | Fix | Developer(s) | PR | Defects | Notes |

## Open gaps
- [ ] <Module>: QA deployment — no local deploy run found before 2026-09-09. When did it first reach QA?
  <answer here>

## Update History
| Date | Changes |
**Scan state:** dev=`<sha>` · transcripts≤`<ISO ts>` · docs=`<sha>` · open=`<branch>@<sha>`, `<branch>@<sha>`
```

Scan state is a set of watermarks, not a copy of the log — Git is the log.
`open=` lists every unmerged branch that backs an `In Progress` module with
its tip at scan time, so the next run sees new commits on it
(`git log <sha>..origin/<branch>`) without waiting for the merge. A branch
that has merged since is dropped from `open=` once its module is Completed.

Rules for the shape:

- **Seven always-present fields per module** (marked above) so an absence is
  visible; every other field appears only with content. No `Unknown` ×17.
- **Empty-value words:** `Not evidenced` (looked, nothing), `Not available`
  (source does not exist in this project), `Not applicable`.
- One line per fact. Never paste plan, PR or FSD text — reference it.
- Timeline table cells hold the date only; the pointer lives in the section.
- **Milestones: at most 5 lines per module**, the turning points only (plan,
  first code, BA answer that unblocked it, merge, an extension by another
  module). Fixes never appear in Milestones — they live once, in the Rework
  table. Key commits: at most 6.
- Duration: `calendar` counts inclusively (start day and completion day both
  count); `active` counts distinct PKT dates with a non-merge commit on the
  plan or the code.
- Developers below the 20 % line who made a material change are named in
  Notes, not in Developer(s).

---

## Step 5 — Update strategy (every run after the first)

1. Read the file. Parse **Scan state**, the module list, the ledger, the
   open gaps.
2. **Consume answered gaps first**: an `Open gaps` item with text under it
   becomes the field's value with pointer `Confirmed (user, <today>)`; remove
   the item and log it in Update History.
3. **What changed since Scan state:**
   - Git: `git log --merges --grep='pull request' <dev-sha>..origin/dev` →
     new PRs; `git log <sha>..origin/<branch>` for each `open=` entry → progress
     on in-progress modules; branches not in `open=` with commits after the
     watermark → new in-progress modules.
   - Docs: `git diff --name-only <docs-sha>..origin/dev -- <plans> <index> <defects> <requirements-history>` → re-read only those.
   - Transcripts: files with mtime after the transcript watermark → new
     ledger rows.
4. Re-derive **derived fields for every module** (status, DEV/QA, duration) —
   cheap, and it is what keeps them consistent with the ledger.
5. Touch **evidenced fields** only when stronger evidence appears (Confirmed
   beats High Confidence beats Inferred). Keep the old value in Notes as
   `previously: <value> (per <pointer>)`. History is preserved inside the
   entry, never by refusing to correct it.
6. Never delete a module entry. A module that vanished from the plans folder
   gets `Status: Withdrawn` and a note.
7. Append one Update History row and rewrite Scan state.
8. Re-read the file immediately before writing (concurrent-run check, as in
   the siblings).

**First run:** steps 1–2 don't apply; do the full derivation, then set Scan
state. Say in the report that it was a baseline and which sources were found.

---

## Step 6 — The Project Status roll-up (every run, last)

`<directory>/<Project-Name>-Project-Status.md` answers one question for
whoever owns the date: **how much is done, how much is left, and of what is
left, what can we start and what are we waiting for.** It is derived from the
history file just written plus the repo docs, so it is regenerated **whole**
on every run (and by `report`) — never hand-edited, never a second ledger. It
lives beside the history file for the same reason the history does: the repo's
feature index owns feature status, and a second status file *inside* the repo
would be the duplication the repo's own rules forbid.

Fixed shape, so two issues are comparable:

1. **Header** — as-of PKT timestamp, `origin/<integrationBranch>` SHA, where it
   is regenerated from, and the committed dates from the release plan
   (feature index, delivery-schedule table) with days-to-go-live.
2. **The numbers** — one table, `Done | Left | Total | Done %` rows for:
   delivery modules (split: on QA proven / on DEV only / tooling); FSD
   top-level sections built vs empty; build phases; release-plan iterations;
   PRs merged vs branches in flight; defects fixed vs open **by severity**;
   BA questions resolved vs open; automated test count (from the doc that
   owns it, never counted here); elapsed days of code vs days to go-live.
   Every number has a source you can name — the history file, the feature
   index, `defects.md`, Part 2's headings, Git. **When a heading's count
   disagrees with the sections under it, print both** — never pick one.
3. **Done** — modules grouped by phase, with the environment each has
   *proven* reached (history file's Status column), and the last proven
   deploy row. "By convention only" is said, not hidden.
4. **Left — blocked** — one row per feature-index row that is `Blocked`:
   FSD section, *why* (quote the index's reason: empty heading, held by the
   BA, missing matrix rows), and its release-plan slot. Close with the
   index's own risk statement on unspecified weeks, referenced not
   paraphrased.
5. **Left — unblocked** — three tables: **open defects** grouped by severity
   with ids and one-line whats (from `defects.md` §Open at
   `origin/<integrationBranch>`); **branches in flight** (Git: unmerged
   remote branches with commits, what each is for from its name and last
   commit, who from `authors`); **known-unbuilt ours** (the index's own
   "also ours" list — outbox, datasets, environments — plus the next
   release-plan milestone).
6. **Reading it** — at most three sentences: what the team can start
   tomorrow, and which decisions are not engineering's.
7. **Update history** — one row per regeneration, one line: the headline
   deltas since the previous row (modules done, environment moves, defects
   opened/closed, blocked rows added/released).

Rules: numbers only from sources the ledger already trusts; **blocked means
the feature index says so today**, not that the module looks hard; a branch
is "in flight" only if it has commits not on the integration branch; a
defect fixed on an unmerged branch is still open here. **Never move a row
from Blocked to Unblocked on your own reading of the FSD** — the feature
index changes first, then this file follows.

---

## Output

```
Updated `<Project>-Backend-Development-History.md` at <path>   (baseline | incremental)
Regenerated `<Project>-Project-Status.md`: <done>/<total> modules · <open> defects open · <blocked> blocked

Discovered:  <n> modules (<k> new), <p> PRs, <d> deploy runs (<e> DEV, <q> QA)
Added:       <modules / ledger rows / rework rows>
Updated:     <module: field old → new (why)>
Deployments: <module → env on date> …
Uncertain:   <module: field — why>
Open gaps:   <n> awaiting your answer (listed in the file)
Manual input needed: yes/no — <what>
```

`status` prints the file path, scan state, counts and open gaps, writes nothing.
`report` rewrites only the Project Status file and prints its §1 table.

---

## Common mistakes

| Mistake | Fix |
|---|---|
| Completion = last commit on the branch | Completion = the PR merge into `dev`; unmerged has none |
| Labelling the convention-derived DEV date `Confirmed` | Convention = High Confidence; a ledger row containing the merge = Confirmed |
| Applying the merge convention to QA | Only the env `deployment.mergeDeploysTo` names; QA comes from the ledger or is `Not evidenced` |
| Typing DEV/QA/Status into a module by hand | Derived from the convention, the ledger and the merge state every run |
| "Deployed" because a doc says "verified on DEV" | Corroboration only; never the sole source of a date |
| Product delivery = FSD V1 for everything | The revision whose changelog first specifies *this* section |
| Developer = anyone whose name is on the branch | ≥ 20 % of the module's PR commits, or an own PR; merger listed separately |
| Person-hours or "effort: 3 days" | `calendar` and `active days` only |
| Taking a transcript hit with `{DEPLOY_BRANCH}` as a deploy | Template echo — discard |
| Copying the SSH host or port into the ledger | Environment, date, branch, commit only |
| Overwriting a date with a newer but weaker source | Stronger evidence only; old value → `previously:` |
| Re-reading every plan and transcript on every run | Scan state; only what changed |
| Hand-editing the Project Status file, or letting it drift from the ledger | It is regenerated whole every run; fix the ledger or the repo doc it reads |
| Moving a feature from Blocked to Unblocked because the FSD "looks written now" | The feature index decides; the roll-up follows it |
| Reading `docs/` from a dirty or mid-merge working tree | `git show origin/dev:<path>`; note the revision in Scan state |
| Eight milestone lines that are really the rework list | ≤ 5 turning points; fixes live once, in the Rework table |
| Discarding every hand-run deploy | Recover the ones that show a healthy check; label them |
| Crediting everyone in a shared PR with every module it carried | Count commits by module path inside the PR |
| Entry confidence `Unknown` because QA has no local run | Confidence over dates that have values; `(QA not evidenced)` beside it |
| DEV date before the environment existed | Convention date = max(merge, environment's first ledger row) |
| "Fixing" a PKT merge date back to the plan's UTC day | Same instant; PKT stands |
| `src/*/Features/X` in a pathspec | Globs don't cross `/`; name the project directories |
