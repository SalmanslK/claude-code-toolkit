---
name: team-daily-activity
description: >
  Use when the user wants to know, record or review what each developer on
  the team did on a given day or week in the current repository — "what did
  the team do yesterday", "who worked on what this week", "track each dev's
  daily activity", "who was idle", per-person standup prep, 1:1 or sprint
  review notes. Reconstructs from Git for every contributor, not just the
  user. For the user's own first-person standup log use daily-scrum-updates
  instead.
---

You are maintaining **the user's private, lead's-eye log of what every developer
did each day** in the current repository. It is a personal tracking record — a
standup board the user reads before standup, a 1:1, or a sprint review — not a
project artifact, and not anyone's performance review.

**REQUIRED BACKGROUND:** the sibling skill `daily-scrum-updates` (same
`~/.claude/skills/` directory) owns the mechanics this skill reuses verbatim:
§Configuration, §Backup mirror, §Timezone, §Date parsing, §Working days,
§Existing entries are authoritative and its concurrent-run re-check. Where this
file says "as in daily-scrum-updates", follow that section exactly. Read it once
per session.

---

## HARD RULE — private, outside the repository, never committed

Same rule as daily-scrum-updates, restated because it is the one that matters:

- **Never** `git add`, `commit`, `push`, `rm` or otherwise let Git touch the
  output file. Writing it is a plain file write.
- **Never** create it inside a repository working tree. Default location is
  outside every project (§Configuration). If a resolved path lands inside the
  current repo, stop and tell the user before writing.
- **Never** gitignore it as a way of keeping it in the repo.
- Every Git command this skill runs is **read-only**: `git log`, `git show`,
  `git merge-base`, `git rev-list`, `git branch -a --contains`. No `fetch`,
  `checkout` or `pull` — if the local clone looks stale, say so and let the
  user refresh it.

---

## Quick reference

| Invocation | Behaviour |
|---|---|
| `/team-daily-activity` | Fill every missing working day between the last recorded date and today. First run: last 5 working days. |
| `/team-daily-activity today` / `yesterday` / `2026-09-16` / `Sep 16` | Only that date. |
| `/team-daily-activity this week` / `last week` / `this month` | Every working day in that span. No rollup section. |
| `/team-daily-activity backfill [N or A..B]` | Further back. **Announce the exact range before writing.** |
| `/team-daily-activity status` | Read-only: file path, last date, missing working days, known devs, unmapped authors. |
| `... dir=<path>` | One-off output directory override for this run. Not persisted. |

Date words, working-day filtering, first-run window and backfill range rules:
as in daily-scrum-updates. Explicit dates are scoped to exactly those dates —
an explicit date on a file that does not exist yet initialises the file with
the title and that one date, never the first-run window.

---

## Configuration

**Shared config file:** `~/.claude/daily-scrum-updates/config.json` — the same
file daily-scrum-updates reads, so `directory`, `workingDays`, `holidays`,
`projectNames` and `backupDirectory` are set once and govern both logs. Resolve
them exactly as daily-scrum-updates §Configuration does.

This skill adds one key:

```jsonc
{
  // Git author email → display name. Order here is the order devs appear
  // under each date. Several emails may map to one name (aliases).
  "authors": {
    "dev.one@example.com":   "Dev One",
    "dev.one.alt@example.com": "Dev One",
    "dev.two@example.com":   "Dev Two",
    "dev.three@example.com": "Dev Three",
    "lead@example.com":      "Team Lead"
  }
}
```

- **Known devs** = the distinct display names in `authors`, in first-appearance
  order. This is the roster the `_No activity:_` line is checked against.
- **Key by email, never by `%an`.** The same person appears under several
  names — Bitbucket's merge button stamps a variant (`Dev One*`,
  `Dev Three Full Name`); a laptop setting produces another (`devtwo`).
  Emails are far more stable. If an email is missing from the map, key on the
  raw `%an` for this run, list it under **Unmapped authors** in the report, and
  suggest the line to add — do not edit the map yourself. An alias that never
  appears on an authored commit is still load-bearing: Bitbucket stamps it on
  the PR merge commit (`dev.one.alt@` above exists only for that).
- If `authors` is absent entirely, build the roster from every email with a
  non-merge commit in the 30 days before the target date, display the raw
  `%an`, and say in the report that the map should be seeded.

**Output file:** `<directory>/<Project-Name>-Team-Daily-Activity.md`. Mirror
it after every write as in daily-scrum-updates §Backup mirror — copy the file
and the config to `backupDirectory`, and this skill's own definition as
`<backupDirectory>/team-daily-activity-SKILL.md`. **Not `SKILL.md`** — that
name in the mirror belongs to daily-scrum-updates, and overwriting it would
destroy the sibling's only backup.

---

## Evidence: three read-only passes per date

All date math is **PKT (UTC+5)** as in daily-scrum-updates §Timezone.
Bitbucket's merge commits are stamped `+0000`; the explicit-offset window below
handles that — never `--date=local`.

**Resolve "today" by adding 5 hours to UTC, never with `TZ=`.** Git Bash on
this machine has no tz database, so `TZ=Asia/Karachi date` silently returns
UTC — between 19:00 and midnight PKT that is yesterday's date.

```bash
date -u -d '+5 hours' +%Y-%m-%d            # today, PKT
date -u -d '+5 hours -1 day' +%Y-%m-%d     # yesterday, PKT
```

PowerShell: `(Get-Date).ToUniversalTime().AddHours(5).ToString('yyyy-MM-dd')`.

Set the window once per date `D`:

```bash
SINCE="${D}T00:00:00+05:00"; UNTIL="${D}T23:59:59+05:00"
```

### Pass 1 — authored work, every author at once

```bash
git log --branches --remotes --no-merges --since="$SINCE" --until="$UNTIL" \
  --date=format:'%H:%M %z' --pretty=format:'%h|%ae|%an|%ad|%D|%s'
```

`--branches --remotes`, not `--all`: `--all` includes `refs/stash`, whose
`index on dev: …` / `untracked files on dev: …` entries are not work.

Bucket by email → display name. For each dev, read enough to state outcomes:
`git show --stat <sha>` for anything whose message doesn't already say what it
did; the diff only when the stat doesn't settle it. Skip `bin/`, `obj/`, lock
files.

**Ids are read as of the commit, never from the working tree.** When a commit
cites a defect or question id (`D97`, `Q81`, `PROJ-243`), read the row from
that commit's own revision — `git show <sha>:docs/defects.md` — and describe
the thing, not the id. Ids get renumbered when two branches claim the same
number and merge in sequence: on this repo `D99` was a Mating gap on the
branch that fixed it and a different defect entirely on `dev` a day later.

**Which branch was a commit on?** `%D` is only populated at a branch tip. For
a commit that has since merged, the branch is named by the PR merge that
landed it — `git log --merges --ancestry-path <sha>..origin/dev --grep='pull request'`
and read `Merged in <branch>` from the oldest hit. For a commit that has not
merged, `git branch -a --contains <sha>` lists the open branch(es) holding it.

**Commits that reached `dev` without a PR** — on `origin/dev`'s first-parent
line, not inside any `M^1..M^2` range — are still that dev's work. Write them
with the parenthetical `(direct to dev, no PR)`; a lead wants to see those.

### Pass 2 — pull requests merged that day

```bash
git log --branches --remotes --merges --since="$SINCE" --until="$UNTIL" \
  --date=format:'%H:%M %z' --pretty=format:'%h|%ae|%ce|%ad|%s' \
  | grep 'pull request #'
```

Only `Merged in <branch> (pull request #N)` counts. `Merge branch 'dev' into
feature/x`, `Merge remote-tracking branch 'origin/dev' into …`, `Merged dev
into …` are branch refreshes — **not work, not a bullet, for anyone.**

A Bitbucket merge commit carries two people: **`%ae` is the PR's creator**
(under their Bitbucket identity, hence the aliases) and **`%ce` is whoever
clicked merge.** Neither is taken on faith for authorship. The PR's author is
**the email with the most non-merge commits inside the PR**:

```bash
git log --no-merges --format='%ae' "${M}^1..${M}^2" | sort | uniq -c | sort -rn
```

`%ae` should agree with that count; if it doesn't, the count wins. On a tie,
`%ae` wins, then whichever side's commits carry the feature rather than the
tidy-up (PR #62 was 2–2; the build and the HTTP walk outweighed a renumber and
a test-count fix). Never the branch tip's author — the lead merging `dev` into a teammate's branch just
before the PR lands makes the tip theirs. Verified on this repo: PR #64 had 38
commits by one dev and 2 by the lead; the tip said the lead, the count said
the dev, the dev was right.

- The PR is that dev's headline bullet for the day, even if all its commits
  were on earlier dates — the merge is the milestone. Close the parenthetical
  with `merged by <Name>` when `%ce` maps to a different known dev.
- **The merger (`%ce`), when a different known dev, gets one bullet** for the
  day covering every teammate PR they merged: `**Reviewed and merged <X>**` —
  reviewing a teammate's PR is real work and shows up nowhere else.

### Pass 3 — was the branch still open at the end of that day?

Merged-ness is judged **as of `UNTIL`, not as of now** — a branch that landed
at 00:11 the next morning was open all of this day:

```bash
DEV_THEN="$(git rev-list -1 --first-parent --until="$UNTIL" origin/dev)"
git merge-base --is-ancestor <branch> "$DEV_THEN" && echo shipped || echo open
```

`--first-parent` is load-bearing: without it `rev-list` returns the newest
commit *reachable from* `dev`, which is usually a feature-branch commit that
merged days later, and every open branch tests as shipped.

Work on a branch that was open at `UNTIL` is written as in-progress
("started", "continued", "under review", "not yet merged") — never as
shipped, even if it has since merged. Say only what Git proves: "not yet
merged" is provable, "no PR yet" is not — a PR can be open on Bitbucket with
no trace in Git until it merges.

### Sources this skill does not use

Claude Code session transcripts belong to the user alone. Using them would
make the user's own row richer than everyone else's in a file whose purpose is
to see the team side by side, so **all rows are Git-only, the user's included.**

---

## Entry shape

This is the whole contract. An entry *is* this and nothing more — no preamble,
no per-dev commit or line counts, no clock times, no closing notes section.

```markdown
## 2026-09-16

### Dev One
* **Orders module merged**: Closed the front-end team's gap report on the Orders list — filters, ordering and detail fields — made two simultaneous creates on one order safe, and landed it in dev (PR #64, merged by Team Lead).
* **Strict JSON numbers API-wide**: Quoted numbers are now rejected on every endpoint and the OpenAPI schema describes the real wire shape (D80).

### Dev Two
* **Invoicing built**: Planned the module against the spec, built it in one pass with its guide and smoke script, verified it over HTTP and put it up for review (`feature/invoicing`, PR #73 open).
* **Concurrent-save race fixed**: Two first saves of the same row no longer collide, and the review's missing tests were added.

### Dev Three
* **Payments built and shipped**: Built the module end to end — create and delete, lists and detail, guide, smoke script — answered every review finding and merged it into dev (PR #70, merged by Team Lead).
* **Second gap report started**: Began fixes for the front-end team's next findings (`fix/PROJ-243-orders-gaps`, not yet merged).

### Team Lead
* **Reviewed and merged two modules**: Took the Orders and Payments PRs through review and into dev, refreshing each from dev first (PRs #64 and #70).
* **Docs audit closed**: Applied the audit's fixes and decisions and closed a upload defect after verifying it on DEV and QA (PRs #71, #75).

_No activity: —_
```

This example is verified against the repository's history for that date — the
PR numbers, the merger and the open branch are what the three passes return.

The parts, in order:

1. `## YYYY-MM-DD` — one per date, unique key, file sorted most-recent-first,
   under a single `# Team Daily Activity — <Project Name>` title.
2. One `### <Display name>` per dev with evidence that day, **in `authors`
   order**; unmapped authors after them, alphabetically. A dev with no
   evidence has no `###` section.
3. Under each dev, **1–4 bullets**, each `**Heading**: one sentence.`
   - Heading: 3–6 words naming *this day's thing*. A product or feature name
     counts as one word and keeps its own punctuation ("Cleavage, IVC &
     Multiplication built"); otherwise no colon, dash or comma inside.
   - Sentence: what changed for the product or team, in words a PM reads
     without asking. Name the feature area ("the invitation email", "Mating",
     "Fertilization"), never a class, interface, method or config key.
   - Trailing parenthetical, one per bullet: PR number(s), branch name in
     backticks, defect id, `merged by <Name>`, `direct to dev, no PR` —
     traceability for the lead, never the subject. **Cite a defect id only
     if it means one thing that day**: when two branches used the same number
     for different defects (D97 on 2026-09-16 was a save race on one branch
     and an email sender on another), the sentence already names the thing —
     drop the id rather than point the lead at the wrong row.
   - **Order within a dev:** teammates' PRs they reviewed and merged; then
     their own merged PRs by product impact (a feature, then fixes, then
     docs/process); then work still open at end of day.
   - **Budget:** same-theme commits are one bullet; three review-fix commits
     are one bullet; a day of only trivial commits is one short bullet. When
     a dev still exceeds four, fold by area in this order until they fit —
     all teammate-PR reviews into one, all docs/process/housekeeping into
     one, then fixes sharing a screen or module into one — and list every
     folded PR in that bullet's parenthetical.
4. `_No activity: A, B_` — known devs with no section that day, in `authors`
   order; `_No activity: —_` when everyone was active. Always present.

Nothing about a neighbouring date goes in — a PR that landed at 00:11 the next
morning belongs to the next date and is written there when that date runs.

---

## Existing entries and concurrency

As in daily-scrum-updates: never duplicate a `##` date; never rewrite an
existing date section (report a discrepancy and ask); explicit-date mode on an
existing date shows it and stops; **re-read the file immediately before each
insert** and skip the date if a concurrent run already wrote it.

**One exception — today is provisional until the day is over.** A section
written for the current date is headed `## YYYY-MM-DD` and carries
`_Provisional — as of HH:MM PKT_` as its first line. Any later run that
covers that date (a default run the next morning, an explicit `today`)
**replaces** the provisional section outright, and drops the marker once the
date is in the past. Without this, a first run at 19:40 freezes a day that
still had four hours in it.

---

## Output

```
Updated `<Project>-Team-Daily-Activity.md` at <resolved path>

Added: 2026-09-15, 2026-09-16
Unmapped authors: <%an> <%ae>  →  add "email": "Name" to authors   (omit if none)
```

Then the full text of each added section. `status` prints the §Quick reference
fields and writes nothing. Always name the resolved path once.

---

## Common mistakes

| Mistake | Fix |
|---|---|
| Crediting a PR to whoever clicked merge | Count non-merge authors in `M^1..M^2`; the merger (`%ce`) gets a "Reviewed and merged" bullet only if different |
| Reading the merger from `%an` | On a Bitbucket merge commit `%an` is the PR creator; the merger is `%cn`/`%ce` |
| Counting `Merge dev into feature/x` as coordination work | Branch refreshes are never bullets |
| Calling a branch shipped because it is in `dev` **today** | Test against `origin/dev` as of `UNTIL`; merged next morning = open all day |
| Describing `D99` from the working tree's `defects.md` | Read it from the citing commit: `git show <sha>:docs/defects.md` |
| Bullets with clock times, commit counts, line counts | Not in the shape; delete them |
| `FertilizationRecord`, `RolePermissionMap`, `IFileStore` in a sentence | Name the feature area a PM knows |
| Grouping by `%an` | Group by `%ae` through `authors`; the same person has 2–3 name strings |
| Folding "the tail of the day" from 00:11 next morning into today | Strict PKT window; it appears when the next date runs |
| Omitting the `_No activity:_` line because everyone worked | Write `_No activity: —_`; its absence looks like a missed check |
| Padding a dev to four bullets | One theme, one bullet; fewer is fine |
| `git log --all` picking up `refs/stash` | `--branches --remotes` |
| `rev-list --until` without `--first-parent` | Returns a later-merged feature commit; every open branch reads as shipped |
| Writing "no PR yet" | Git can't see an open PR; write "not yet merged" |
| `TZ=Asia/Karachi date` in Git Bash | No tz database here — it is UTC; use `date -u -d '+5 hours'` |
| Freezing today's section at 19:40 | Mark it provisional; the next run replaces it |
