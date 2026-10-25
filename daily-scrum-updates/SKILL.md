---
name: daily-scrum-updates
description: >
  Maintains a private, external Markdown history of daily Scrum/standup updates,
  reconstructed from Git history and Claude Code session transcripts — never a
  raw commit-message dump. The history file lives outside the current repository
  by default (a common personal directory, one file per project) and this skill
  never stages, commits or pushes it. Supports today, yesterday, an explicit
  date, this/last week, this month, backfill and status.
---

You are maintaining **the user's personal daily Scrum update log** — not a
project artifact. Everything in this file is written from the user's own
perspective as a Lead Software Engineer, for sharing with a PM and dev team.

---

## HARD RULE — this file is private and lives outside the repository

**The history file is user data, not project data.** Treat it the way you would
treat the user's shell history, never the way you treat a doc in `docs/`.

- **Never** run `git add`, `git commit`, `git push`, `git rm`, or any Git command
  that touches this file.
- **Never** add it to `.gitignore` as a way of "handling" it — that is a
  workaround for keeping it inside the repo, and the whole design here is that
  it never needs to be. If a resolved path ends up inside the current
  repository's working tree (see Configuration below), stop and tell the user
  before writing anything there — do not silently gitignore it and do not
  silently move it.
- **Never** create it inside the repository unless the user's own config
  (§Configuration) explicitly points there. The default is always a directory
  outside any project.
- Writing to this file is a plain file edit (Read/Edit/Write tools), never a Git
  operation.

If at any point you are unsure whether a path is inside the repository, check:

```bash
git -C "<repo-root>" rev-parse --is-inside-work-tree 2>/dev/null  # run with cwd = the resolved history-file directory
```

---

## Quick reference

| Invocation | Behaviour |
|---|---|
| `/daily-scrum-updates` | Default mode: fill in every missing working day between the last recorded entry and today (see §Default behaviour). |
| `/daily-scrum-updates today` | Only today's entry. |
| `/daily-scrum-updates yesterday` | Only yesterday's entry. |
| `/daily-scrum-updates tomorrow` | Only a "planned" entry — see §Date parsing. Almost always "insufficient evidence" unless the user states the plan inline. |
| `/daily-scrum-updates 2026-09-08` | Only that ISO date. |
| `/daily-scrum-updates 09-08-2026` | Only that date (MM-DD-YYYY — see disambiguation rule). |
| `/daily-scrum-updates September 8` / `Sep 8` | Only that date, year inferred. |
| `/daily-scrum-updates this week` | Every working day this week up to today (same missing/duplicate rules as default mode), plus a week-level rollup summary — see §Weekly rollup. |
| `/daily-scrum-updates last week` | Every working day of the previous Mon–Fri (or configured week), plus a rollup — see §Weekly rollup. |
| `/daily-scrum-updates this month` | Every working day from the 1st of the current month up to today. |
| `/daily-scrum-updates backfill` | Reconstructs further back than default mode. **Always announces the exact date range before writing anything.** See §Backfill. |
| `/daily-scrum-updates status` | Read-only. Reports last recorded date, missing working days, file location. Writes nothing. |

Any explicit date (single date, `this week`, `last week`, `this month`) is
**scoped to exactly those dates** — it never triggers the "fill everything
missing since the last entry" behaviour of no-args mode.

---

## Configuration

**Fixed config file** (always checked at this exact path, regardless of where
history files end up):

```
~/.claude/daily-scrum-updates/config.json
```

If it does not exist, use the defaults below and do not create it unless the
user asks to change a setting — at which point write only the keys being set.

```jsonc
{
  // Directory that holds every project's "<Project-Name>-Daily-Updates.md".
  // Default if this key is absent:
  "directory": "~/.claude/daily-scrum-updates",

  // Working days, three-letter abbreviations. Default: Mon–Fri.
  "workingDays": ["Mon", "Tue", "Wed", "Thu", "Fri"],

  // Non-working dates even if they fall on a working day (ISO format).
  "holidays": [],

  // Optional: override the auto-detected project name for a specific repo
  // path, keyed by the absolute path returned by `git rev-parse --show-toplevel`.
  "projectNames": {},

  // Second, independent copy of everything this skill writes — see
  // §Backup mirror. Deliberately NOT inside ~/.claude, so a Claude Code
  // reinstall/reset/uninstall can't take the only copy with it.
  "backupDirectory": "~/DailyScrumUpdates"
}
```

Resolve, in order:

1. Read `~/.claude/daily-scrum-updates/config.json` if present; merge over the
   defaults above (missing keys keep their default).
2. **Directory** — expand `~`, and replace a literal `{project}` with the
   project name from step 3 (so `D:/Claude-Local/{project}/scrum` gives each
   repo its own folder; create it if missing); this is where
   `<Project-Name>-Daily-Updates.md` is read from and written to. If the user passes `dir=<path>` on an
   invocation, treat that as a **one-off override for this run only** — do not
   persist it unless they say to.
3. **Project name** — check `projectNames` for the current repo's
   `git rev-parse --show-toplevel`. If absent, use the **basename of that
   top-level path** (e.g. `D:\repos\my-app` → `my-app`). If not inside a
   git repository, use the current directory's basename and say so in the
   report — commit-based evidence will be unavailable for that project.
4. **File path** — `<directory>/<Project-Name>-Daily-Updates.md`.
5. **Backup directory** — expand `~`; see §Backup mirror for what goes there
   and when.

Tell the user the resolved path once per session (in the report, §Output),
not on every internal step.

To change the storage location, the user edits or asks you to edit
`~/.claude/daily-scrum-updates/config.json` — e.g. "put my daily updates in
`D:\Users\<me>\Documents\ScrumUpdates`" → write
`{"directory": "D:\\Users\\<me>\\Documents\\ScrumUpdates"}` (merging with
any existing keys, never dropping them).

---

## Backup mirror

`~/.claude/` belongs to the Claude Code installation, not the user — an
uninstall, reset, or a bad update could take everything under it, including
the history file and this very skill definition. So every write also
maintains a second, independent copy under `backupDirectory`
(default `~/DailyScrumUpdates`, i.e. a plain, visible folder in the user's
Windows profile with no relationship to Claude Code).

**If `backupDirectory` is `null` in config.json, skip this whole section.**
That is the case when `directory` is already outside `~/.claude/` (since
2026-09-24 it is `D:/Claude-Local/{project}/scrum`, the user's single home
for Claude-written docs); the skill definitions are separately copied to
`<your skills folder>\`.

After any step that writes the history file (§Default behaviour, §Backfill,
an explicit-date write, an amendment under §Existing entries), also:

1. Ensure `backupDirectory` exists (create it if not).
2. Copy the **just-written history file** there, same filename
   (`<Project-Name>-Daily-Updates.md`), overwriting the previous mirror. This
   is a plain file copy — the working copy under `directory` is the one this
   skill reads on every run; the mirror is write-only from this skill's
   perspective.
3. Copy `~/.claude/daily-scrum-updates/config.json` there too, if it exists,
   so the directory/working-days/holidays configuration itself survives.
4. Once per invocation (not once per date written), check whether this
   skill's own `SKILL.md` differs from `<backupDirectory>/SKILL.md` (missing,
   or content differs) and if so copy it over. This is what makes the whole
   system — data and the logic that maintains it — recoverable from one plain
   folder: reinstalling the skill after a wipe is copying that file back to
   `~/.claude/skills/daily-scrum-updates/SKILL.md`.

`status` mode is read-only and does not touch the mirror.

This mirror is exactly as private as the primary copy — the same
§HARD RULE applies: never `git add`/`commit`/`push` it, never place it inside
a repository's working tree.

---

## History file format

```markdown
# Daily Scrum Updates — <Project Name>

## 2026-09-09

* **Shipped**
  * **Short Bullet Heading**: One punchy sentence, not a paragraph.
  * **Another Short Heading**: One punchy sentence, not a paragraph.
* **Deployed**
  * **A Third Heading**: One punchy sentence, not a paragraph.

**Scrum summary:** A tight, spoken-style recap of the day — read this one out
loud in standup instead of the bullets above, leading with the same item the
bullets lead with.

## 2026-09-08

* [Requirements] **Short Bullet Heading**: One punchy sentence, not a paragraph.

**Scrum summary:** ...
```

- **Sections are ordered most-recent-first**, matching the example above.
- A new date's section is inserted at the position that keeps the file sorted
  descending by date — not always at the very top (a backfilled gap can land
  in the middle) and not always at the very bottom.
- One `##` heading per date, ISO format (`YYYY-MM-DD`), used as the unique key.
  **Never two sections for the same date.**
- 2–5 leaf bullets per date, same budget as before — grouping doesn't raise
  it, it just removes the per-line tag repetition. No sub-sub-headings, no
  commit hashes, no file paths, unless one is genuinely load-bearing for
  understanding the update.
- **Bullets are grouped two levels deep: a bold tag name as the top-level
  bullet, its items nested underneath as sub-bullets.** This is the 2026-09-09
  example above — two `**Shipped**` items grouped under one `**Shipped**`
  parent instead of repeating `[Shipped]` on every line. Only tags that
  actually have an item that date appear; never an empty group. See
  §Priority ordering and category tags for the full rule (tier order, when to
  skip the grouping entirely for a single-bullet day).
- **Each leaf item is a bold 4–5 word heading**, `**Heading**:`, then
  **exactly one sentence** — see §One-liner bullets. The heading is a
  compressed label for the item ("FSD revisions tracked", "PR reviews
  followed up"), not a restatement of the whole sentence, and not a repeat of
  its parent tag's word (a heading of "Shipped feature" nested under
  **Shipped** says nothing the parent didn't already say) — the heading
  should name *this day's specific thing*.
  **The heading itself carries no internal punctuation** — no colon, dash or
  semicolon inside the bold text — since the item already has one immediately
  after it (`**Heading**: detail`); a colon inside the heading reads as a
  second, competing label right next to the real one.
- **Items within a tag group are ordered by actual impact, highest first**
  (a headline feature before a smaller one, an outage before a cosmetic fix).
  **Tag groups themselves are ordered by tier, most important first** — never
  by commit order or discovery order. See §Priority ordering and category
  tags for the tag vocabulary and the tier order that drives both.
- **Every date section ends with a `**Scrum summary:**` line** — see
  §Synthesizing updates for what goes in it. This line is not a bullet and
  carries no heading of its own.

---

## Timezone

All date math in this skill — "today", "yesterday", working-day walks, commit
grouping, and session-evidence bucketing — is anchored to **Pakistan Time
(PKT, UTC+5, no DST)**, never the machine's local timezone. Git author dates
carry their own offset and session timestamps are stored in UTC; without a
pinned zone, "today" could resolve differently depending on what machine or
timezone the tool happens to run under.

- **Resolving `today`/`yesterday`/`tomorrow`** — add the fixed `+5h` offset
  to UTC. **Never `TZ=Asia/Karachi`**: Git Bash on this machine has no IANA
  tz database, so `TZ=` is silently ignored and the command returns UTC —
  between 19:00 and midnight PKT that is *yesterday's* date (found
  2026-09-17: `TZ=Asia/Karachi date` printed 14:49 against a 19:49 clock).
  ```bash
  date -u -d '+5 hours' +%Y-%m-%d            # today, PKT
  date -u -d '+5 hours -1 day' +%Y-%m-%d     # yesterday, PKT
  date -u -d '+5 hours +1 day' +%Y-%m-%d     # tomorrow, PKT
  ```
  The same arithmetic in PowerShell, which likewise must not trust
  `Get-Date`'s local zone:
  ```powershell
  (Get-Date).ToUniversalTime().AddHours(5).ToString('yyyy-MM-dd')
  ```
  Sanity check once per run: the resolved time should be within minutes of a
  commit authored just now (`git log -1 --format=%ad --date=format:'%H:%M %z'`).
- **Git commits** — group by PKT date, not the machine's local date. Prefer an
  explicit offset over `--date=format-local`, which silently trusts whatever
  zone the machine happens to be set to (see the updated command in
  §Evidence gathering). A commit landing right at a day boundary is worth a
  glance at its own `%z` — someone committing at 23:50 PKT from a machine set
  to a different zone can otherwise land on the wrong side of midnight.
- **Session transcripts** — timestamps are UTC (`"timestamp":"...Z"`). Add 5
  hours before taking the date to bucket by PKT day, not by however the
  machine renders it locally.
- **`holidays` and any date in `config.json`** are plain ISO dates with no
  time component — interpreted as PKT calendar dates.

If the working timezone ever changes, this is the one place to update it —
don't scatter a second timezone assumption into another command elsewhere in
this file.

---

## Date parsing

| Input | Resolves to |
|---|---|
| `today` | The current date. |
| `yesterday` | The most recent calendar day before today (not the most recent *working* day — if it's Monday, "yesterday" is Sunday; report if Sunday has no evidence rather than silently substituting Friday). |
| `tomorrow` | The next calendar day. See note below. |
| `YYYY-MM-DD` | Literal, unambiguous. |
| `MM-DD-YYYY` | US convention. If both segments are ≤12 and genuinely ambiguous, state your interpretation back to the user in the report rather than silently guessing (e.g. "interpreted `09-08-2026` as September 8, 2026"). |
| `Month D` / `Mon D` (no year) | Current year, unless that date is in the future relative to today, in which case assume the most recent past year. |
| `this week` | Monday (or the configured week's first working day) through today. |
| `last week` | The full previous Mon–Fri (or configured working days). |
| `this month` | The 1st of the current month through today. |
| `backfill` | See §Backfill — not a single date, a mode. |
| `status` | Not a date — see §Status mode. |

**`tomorrow` note:** this skill reconstructs evidence of work already done; it
has no evidence for a day that hasn't happened. Only write a `tomorrow` entry
when the user states the plan inline in the same invocation (e.g.
`/daily-scrum-updates tomorrow: starting the outbox migration`) — record what
they said, prefixed clearly as planned work, not as something already
accomplished. Otherwise report "no evidence for a future date" and write
nothing.

---

## Working days

- Default Mon–Fri, from `config.json`'s `workingDays` (§Configuration).
- A date in `holidays`, or falling outside `workingDays`, is skipped in
  **default / this-week / last-week / this-month / backfill** modes **unless**:
  - there is clear Git or session evidence of work on that date, or
  - the user explicitly named that exact date (explicit dates always run,
    working day or not).
- When skipping a non-working day with no evidence, do not create an empty
  section for it and do not mention it in the report — it simply isn't a gap.

---

## Default behaviour (no arguments)

1. Resolve today's date and the file path (§Configuration).
2. Read the existing history file, if any. Parse its `##` date headings.
3. If the file doesn't exist: initialize it with the H1 title only, and treat
   this as a first run — do **not** attempt to reconstruct a large history.
   Look back a conservative window (default: the last 5 working days,
   including today) for evidence, and generate entries only where the
   evidence genuinely supports one. Say plainly in the report that this was a
   first run and the window you used.
4. If the file exists: find the most recent `##` date. Walk forward one
   calendar day at a time from the day after it, up to and including today.
5. For each date in that walk: skip it per §Working days unless evidence says
   otherwise; skip it if a section for that date **already exists** (should
   not happen given step 4, but never overwrite if it somehow does — see
   §Existing entries).
6. For each remaining date, gather evidence (§Evidence gathering) and, only
   where it supports a real entry, synthesize bullets (§Synthesizing updates).
7. **Today is included only if there is sufficient evidence.** A today with no
   commits and no session activity yet in the day is left ungenerated — say so
   in the report rather than inventing a placeholder.
8. Insert all new sections, correctly ordered (§History file format) — after
   the concurrency re-check in §Existing entries.
9. Report per §Output.

---

## Weekly rollup

`this week` and `last week` do everything §Default behaviour does — scoped to
that week's working days — **and then** add or refresh one extra section: a
week-level rollup, for a sprint review or a "what did you do last week"
standup.

```markdown
## Week: 2026-09-07 – 2026-09-11

* **Highlight heading**: one-liner, coarser-grained than a daily bullet —
  merge same-theme work across days rather than repeating each day's bullet
  verbatim.

**Week summary:** 2–4 sentences, spoken-style, for reading out in a sprint
review — the week's version of the daily `Scrum summary` line.

## 2026-09-11
...
## 2026-09-08
...
```

- **Heading is `## Week: <start ISO> – <end ISO>`** (en dash), spanning that
  week's configured working days (Monday–Friday by default). This format
  never collides with a daily `## YYYY-MM-DD` heading — every other mode's
  "does this date already have a section" and "what's the most recent date"
  logic matches only a bare `## YYYY-MM-DD` line, so a `## Week: ...` heading
  is invisible to it, by design.
- **Positioned directly above that week's daily sections.** §History file
  format's descending-date ordering still governs where the whole block — the
  rollup plus its days — sits relative to other weeks.
- **3–6 highlight bullets**, one-liners (§One-liner bullets), synthesized
  from that week's daily sections **as they stand after this run** — this is
  a synthesis pass over already-written entries, not a fresh
  evidence-gathering pass over Git/sessions. If two days touch the same
  theme, merge them into one highlight instead of repeating.
- **The rollup is derived, not primary evidence, so it is exempt from
  §Existing entries** — the daily sections underneath it stay authoritative
  and untouched, but the rollup itself is today's best synthesis of them and
  is meant to be replaced. Every `this week`/`last week` run **overwrites**
  the prior rollup for that week (if one exists) rather than appending a
  second one — stale synthesis is worse than no synthesis once new daily
  evidence has landed. This is the one section in the whole file this skill
  is allowed to rewrite outright.
- Built only by `this week` / `last week`. Not by `backfill`, default mode, or
  an explicit single date — and not automatically for `this month`, even
  though the same idea would apply; extend it there only if asked.
- If the week has no daily sections at all (nothing generated, no evidence
  anywhere), skip the rollup entirely rather than writing an empty one.
- Report it the same way as a daily entry (§Output) — show its full text
  alongside whichever daily sections were added or already existed for that
  week.

---

## Backfill mode

`/daily-scrum-updates backfill` (optionally `backfill <N>` for N working days,
or `backfill 2026-08-01..2026-08-15` for an explicit range).

1. Determine the range:
   - Explicit range given → use it verbatim.
   - `<N>` given → the N working days immediately before the earliest existing
     entry (or before today, if the file is empty).
   - Bare `backfill` → from the earliest date with any discoverable Git or
     session evidence for this project, up to (but not including) the earliest
     existing entry — or up to today if the file is empty. **Do not blindly
     walk back to the first commit ever** if that produces a huge, low-evidence
     span; if the evidence thins out, stop and say where you stopped rather
     than padding the rest with weak entries.
2. **State the exact date range you are about to process before writing
   anything**, and let the user stop you if it's wrong.
3. Then follow the same evidence-gathering, working-day filtering, dedup and
   quality rules as default mode, for every date in the range — including the
   concurrency re-check in §Existing entries immediately before each insert.
4. Report per §Output, listing every date added (this list can be long for a
   backfill — that's fine, it's the point of the mode).

---

## Status mode

`/daily-scrum-updates status` — **read-only, never writes.**

Report:

- Resolved file path.
- Whether the file exists yet.
- The most recent recorded date, and how many calendar/working days ago that was.
- The list of missing working days between that date and today (applying
  §Working days filtering, but note it as "missing — not yet checked for
  evidence" since status mode does not gather evidence).
- Total number of recorded dates in the file.
- Whether `~/.claude/projects/<slug>/` exists for this project (§Claude Code
  session evidence) — if not, say plainly that session-based evidence is
  unavailable here (see §Known limitations) and every future run will rely on
  Git alone, rather than letting that surface as a surprise later.

---

## Evidence gathering

Two sources. Use both where available; never fabricate from neither.

### Git evidence

Scope to the **current repository** and the **configured Git identity**:

```bash
GIT_NAME="$(git config user.name)"
GIT_EMAIL="$(git config user.email)"
```

For a given date `D` (PKT — see §Timezone, never the machine's local zone):

```bash
git log --all --no-merges \
  --author="$GIT_NAME" \
  --since="${D}T00:00:00+05:00" --until="${D}T23:59:59+05:00" \
  --date=format:'%Y-%m-%d %H:%M %z' \
  --pretty=format:'%H|%ad|%s'
```

If nothing comes back by name, retry with `--author="$GIT_EMAIL"` — commit
author strings don't always match `user.name` exactly (case, aliasing).

Rules:

- `--no-merges` here is deliberate: it isolates the user's **own** authored
  commits, which is what this first pass is for. A routine merge commit
  ("Merge branch 'dev' into feature/x", keeping a branch current) is not its
  own accomplishment and stays excluded. **A PR landing into a shared branch
  is a different thing and is never caught by this pass — see the required
  second pass just below.**
- `--all` — catch commits made on feature/fix/chore branches, not just
  whatever's checked out right now.
- For each commit that looks non-trivial, or whose message alone doesn't
  explain the work, read more:
  ```bash
  git show --stat <sha>
  git show <sha> -- <path>   # only when the message and stat aren't enough
  ```
- **Ignore build/generated paths**: `bin/`, `obj/`, `node_modules/`, lock
  files, and anything else that isn't a meaningful source, doc, test, or
  config change.
- **Group related commits into one accomplishment.** Several commits against
  the same feature slice, same day, same theme → one bullet. Do not enumerate
  every commit. Do not treat "3 commits" as "3 pieces of work."
- **Never expose raw commit hashes or a commit-per-bullet listing** in the
  Scrum update itself. A hash is fine only if you're separately debugging with
  the user, not in the file.
- **Do not claim work from a changed file alone** if you can't establish its
  purpose from the message/diff — read the diff before asserting.
- A day with only trivial commits (formatting, a typo fix, a version bump) is
  weak evidence — don't inflate it into a full bullet; either fold it into an
  adjacent real bullet if it's genuinely related, or leave it out.

### PR merges — a required second pass

**The `--no-merges` author-scoped scan above silently misses every PR that
landed on the target date.** A PR merge commit is a merge commit by
definition, so it's excluded by `--no-merges` — and its author is often
whoever clicked "merge" on Bitbucket, which doesn't reliably match the user's
Git identity even when the work was entirely theirs. Three whole feature
merges (two of them substantial: a 39-file, 6,675-insertion feature) were
missed this way on 2026-09-09 before this rule existed — don't repeat that.

Run this **every time**, not just when something feels missing:

```bash
git log --all --merges \
  --since="${D}T00:00:00+05:00" --until="${D}T23:59:59+05:00" \
  --date=format:'%Y-%m-%d %H:%M %z' \
  --pretty=format:'%H|%ad|%s'
```

No `--author` filter — a PR's merge-commit author is unreliable, so filtering
by it would reintroduce the exact gap this pass exists to close.

- **Only a real PR merge counts** — Bitbucket's merge-commit message has the
  distinctive shape `Merged in <branch> (pull request #N)`. Discard anything
  else this command returns: `Merge branch 'dev' into feature/x` or
  `Merge remote-tracking branch 'origin/dev' into feature/x` just means a
  feature branch was refreshed with the latest shared code — the feature
  itself hasn't shipped. Confirm the direction: `dev` merging *into* a
  feature branch is routine upkeep; a feature branch merging *into* `dev` (or
  `main`) is the milestone. If it's ambiguous which way a merge went, check
  with `git merge-base --is-ancestor <branch> origin/dev` rather than
  guessing from the message alone.
- **Every PR-merge match found is worth a bullet**, even if the user didn't
  author most of the underlying commits — reviewing and merging someone
  else's PR (or a PR built mostly by the front-end/pairing partner) is still
  the user's accomplishment for the day and won't show up any other way.
- **Don't assume the user's role in a PR you can't otherwise place.** If nothing
  else in the day's evidence (their own commits on that branch, session
  transcripts, prior days' bullets) tells you whether they authored it,
  reviewed it, or just happened to be the one who merged it — say what you
  found and ask, rather than writing "built" when it was "reviewed and
  merged" or vice versa. Getting the verb wrong misrepresents the day.
- **Don't assume a PR merged on this date is actually finished work** — a
  feature branch that only has `dev` merged *into* it (never the reverse) is
  still open. If the user mentions reviewing something and you can't find its
  PR-merge commit, check directly
  (`git merge-base --is-ancestor origin/<branch> origin/dev`) before writing
  "merged" — report what the check actually shows and let the user correct it
  if their recollection differs, rather than taking either side on faith.

### Claude Code session evidence

Session transcripts are stored per-project, one JSONL file per session, at:

```
~/.claude/projects/<slug>/*.jsonl
```

`<slug>` is the repo's absolute path with `:` and path separators replaced by
`-` (e.g. `D:\repos\my-app` → `D--repos-my-app`). If that exact directory
doesn't exist, don't guess further — say session history is unavailable for
this project and rely on Git alone.

Each line is one JSON object. The fields that matter:

- `"timestamp"` — ISO 8601 UTC. Add 5 hours and take the date to bucket by
  PKT day (§Timezone) — never the machine's own local rendering.
- `"type"` — `"user"` or `"assistant"` (also some non-message control lines —
  skip anything without a `"message"` object).
- `"message":{"role":..., "content":...}` — the actual turn content.
- `"gitBranch"` — useful corroboration, not required.

Process, per target date:

1. Grep for the date substring first rather than loading whole files — these
   files can be tens of MB:
   ```bash
   grep -l '"timestamp":"2026-09-08' ~/.claude/projects/<slug>/*.jsonl
   ```
2. From matching files, read only the matching lines/regions (not the whole
   file) — extract `user`-role message text, which is the actual task the user
   asked for that day, and look for clear signal in nearby `assistant` text
   (a stated conclusion, decision, or summary) rather than reading every tool
   call in between.
3. Use this to surface work that never produced a commit: investigation,
   architecture discussion, planning, a code review conducted in-session,
   debugging that ended in "not a bug" or is still open, requirements
   analysis, documentation written directly (skills, docs) without necessarily
   committing that session.
4. **Do not fabricate session activity you can't find.** If no transcript
   exists for a date, that source simply contributes nothing for that date —
   say so in your own reasoning, not necessarily in the output, unless it's
   the *only* evidence source that was available and came up empty (then say
   so in the report, similar to how `status` reports what it couldn't check).
5. Session content can include drafts, dead ends, and abandoned approaches —
   only surface what the user actually landed on or a conclusion actually
   reached. A question raised and later abandoned isn't a Scrum update.

**This is machine- and install-local — see §Known limitations** for how and
when to disclose it in a report.

---

## Synthesizing updates

Write each date's bullets as **outcomes**, not a changelog:

> Instead of:
> - Modified `X.cs`
> - Added migration
> - Updated repository
> - Fixed handler
>
> Write:
> - Implemented the required feature flow and completed the related
>   persistence changes.

...and then compress that into one line — see §One-liner bullets. The
example above is the *content* to aim for; the actual bullet is shorter than
that sentence, not longer.

Rules:

- 2–5 bullets. Fewer if the evidence only supports fewer — don't pad.
- Each bullet is a complete accomplishment or a clearly-scoped piece of
  ongoing work ("Continued work on ..." is fine when a multi-day effort is
  still in progress — but only write it again the next day if there was
  actual progress, not as a filler restatement).
- Written from a **Lead Software Engineer** voice: technically accurate,
  outcome-focused, shareable with a PM and the dev team without translation.
- Organize around these categories only where they add clarity — do not force
  every category to appear: Feature development, Bug fixes,
  Architecture/design, Code reviews, Testing, Documentation, CI/CD/DevOps,
  Meetings/discussions, Investigation/research, Planning.
- **No fabrication.** If a date has some evidence but it's too thin or
  ambiguous to state confidently, write the entry with what's actually
  supported, or — if truly nothing usable — write a single bullet stating the
  date's record could not be reliably reconstructed (do not skip the date
  silently in default/backfill mode; the gap should be visible, not invisible).
- **Do not repeat an ongoing task verbatim across days.** "Continued work on
  the order checkout flow" two days running with no distinguishing detail
  is a sign you don't have enough evidence for the second day — say so instead
  of repeating.

### Bullet headings

Each leaf item is `**4–5 word heading**: one-liner`, nested under its tag
group (§Priority ordering and category tags). The heading is a short label,
not a summary of the summary — it should let the user recognize the item at
a glance while skimming the file, and double as a natural standup phrase
(e.g. **PR reviews followed up**, **DEV deploy verified**, **Permissions
defect fixed**). Keep it to a noun phrase or short past-tense clause; skip
articles where you can ("Investigated permissions defect", not "Investigated
the permissions defect").

### Priority ordering and category tags

Three rules that work together: every item gets exactly one tag from a fixed
vocabulary; items sharing a tag are grouped under it instead of repeating the
tag on every line; and the tag's tier decides where its whole group sits in
the list. **Neither items nor groups are ever ordered by commit time,
discovery order, or the order evidence happened to surface — both are ordered
by importance, highest first.** This is what makes the file skimmable at a
glance: the first group of any date tells you what mattered most without
reading the rest.

**The tag vocabulary** (pick the single best fit per item — an item spanning
two doesn't get two tags, pick the more important one and let the sentence
carry the rest):

| Tag | Means | Tier (1 = read first) |
|---|---|---|
| `Shipped` | A feature or capability merged into the shared branch — something the product can now actually do. | 1 |
| `Fixed` | A bug, defect or outage resolved. | 2 |
| `Deployed` | An environment deployed, verified, or its operational status changed. | 3 |
| `Requirements` | A spec/BA question settled, a decision made, a plan or design agreed. | 4 |
| `In Progress` | Reviewed, triaged, found, or started — but not yet finished, merged, or fixed. | 5 |
| `Process` | Internal engineering process, tooling, CI, docs, conventions, housekeeping — work that helps the team, not the product directly. | 6 |

**Grouping:** every item that shares a tag on a given date becomes one
sub-bullet under a single `**Tag**` parent bullet — the tag is written once,
not once per item. A date's list is therefore a list of tag-groups, each
containing 1+ items, never a flat list repeating the same tag. **Skip the
grouping wrapper only when the entire date has exactly one item total** — a
parent bullet with a single child adds a nesting level for nothing, so that
one case falls back to the flat form: `[Tag] **Heading**: sentence` with no
indentation (see the 2026-09-08 line in the §History file format example).
The instant a date has two or more items, even under different tags, every
item goes into a group, including a group of one.

**Ordering rule:** order tag-groups by tier, 1 first. **This tier order is a
default scaffold, not a substitute for judgment** — if a `Process` item was
unusually consequential that day (it caused or prevented an outage, say),
that's a judgment call worth making, but the tag still reflects what the item
actually *was*, and moving its group up should be the exception, not the
norm. Within a group, order items by actual scale/impact (a headline feature
before a smaller one, an outage before a cosmetic fix) rather than
alphabetically or by commit time.

**`Shipped` itself has an internal order**: a product-facing feature or
capability outranks an internal tool the user built for their own workflow,
even though both count as "shipped" — a PM cares about the former far more
than the latter. If a day has both, the product feature leads within the
group.

**Consolidate before you tag, group, and order — not after.** Two items
describing the same shipped thing from different angles (a prep step and its
resulting merge, a bug found and that same bug fixed later the same day)
dilute the list and fight the whole point of grouping by importance — merge
them into one item under the tag that reflects the *outcome* (a bug found
**and** fixed that day is one `Fixed` item, not two split across
`In Progress` and `Fixed`).

**The `Scrum summary` line leads with the same thing the top group leads
with** — if a `Shipped` group exists, the summary's first clause is about it,
not whatever happened to be discussed last.

### One-liner bullets

**Exactly one sentence after the heading — not two, not a semicolon chaining
two clauses into a run-on.** This is what keeps the file skimmable and keeps
each bullet usable as a standup line on its own; a paragraph per bullet is
what this rule replaced. If the evidence naturally wants two sentences,
that's a sign the bullet is really two accomplishments — split it into two
bullets (within the 2–5 budget) rather than writing a longer one.

Make the one line count: **specific and outcome-focused, not vague.**
"Fixed some bugs" is short but says nothing; "Closed out every review finding
on the Warehouses and Bins feature, including a data-safety gap in the delete
flow" is one line and actually communicates the work. Favor a concrete noun
(the feature or module name, what was broken, what now works) over a generic
one ("an issue", "some tests") — but the concrete noun must be something a
**non-engineer recognizes**, not an internal id or a code identifier (see
§Plain language for a PM audience, just below).

> Too long (a paragraph, not a one-liner):
> **PR #34 review findings resolved**: Ran a full code review on PR #34
> (Warehouses and Bins) and resolved every finding — renumbered a defect-id
> collision (D50 → D52), added the missing test proving the site-scoped
> delete guard actually works, and fixed a misattributed XML doc comment
> plus two incomplete sort-order cases. 1,110 tests passing, none skipped.
>
> Still jargon (raw ids and mechanism names carry the sentence instead of the
> outcome):
> **PR #34 review findings resolved**: Closed out every PR #34 review
> finding — a defect-id renumber and a missing delete-guard test — with all
> 1,110 tests passing.
>
> One-liner, plain language, tagged and ready to place at the top of the list:
> [Shipped] **Warehouses and Bins review closed out**: Fixed every issue
> found in review — including a gap that could have let deleted warehouse bins
> stay reachable — and the feature is now fully tested and merged.

### Plain language for a PM audience

This log gets read aloud in standup and skimmed by a PM — **every bullet must
stand on its own for someone who has never opened the code.** Before writing a
bullet, ask: would a PM need to ask "what does that mean?" If yes, translate
it, don't gloss it.

- **No code identifiers.** Class names, interface names (`IFileStore`,
  `IUnitOfWork`), config keys (`Email:FrontendBaseUrl`), method names
  (`MigrateAsync`), SQL/mechanism jargon (dollar-quoting, query filters,
  interceptors) — these describe *how*, and *how* is for the PR, not the
  standup. State *what changed for the product or the team* instead.
- **No bare internal ids as the subject of a bullet.** A defect id (`D50`), a
  BA-question id (`Q6`), an FSD revision number, a raw PR number — none of
  these mean anything to someone who doesn't have the tracker open. Say what
  the thing actually was in plain words. An id may still trail in a light
  parenthetical if it adds real traceability for the dev team, e.g. "...a bug
  in the company-logo upload (D53)" — but the parenthetical is a footnote, never
  the only description, and never the heading.
- **Name the product feature or user-facing area, not the internal module.**
  "Warehouses and Bins", "the password-reset email", "the login screen" —
  yes. "`UserEmailNotifier`", "the repository layer" — no. It's fine to keep
  one technical specific **only** when it's genuinely load-bearing for a PM to
  understand impact (e.g. it blocked a deploy, changed a timeline, or is why
  something is still in progress) — otherwise leave it out.
- Internal tooling work (skills, doc audits, infra plumbing the user built for
  *themselves*) still gets a bullet, but frame it by what it now lets the team
  do or check, not by the tool's internal name — "set up an automated check
  that catches stale requirements documents" beats "added the
  `requirements-check` skill."
- This rule applies to **every bullet in every section** — daily, weekly
  rollup, backfill — and to the `Scrum summary` line, which should need zero
  translation read verbatim in a standup.

If a day genuinely produced enough distinct work that one sentence per item
still runs long, that argues for **more bullets**, each tighter — not longer
bullets. The 2–5 budget (§Synthesizing updates) is the release valve.

### Day summary

After the bullets, add one `**Scrum summary:**` line: a compact, spoken-style
recap of the whole day, 2–4 sentences, meant to be **read aloud in standup**
as-is — not a restatement of every bullet, just the highlights a teammate
actually needs to hear. Prefer plain prose over another list. This is the
"compact and sweet" version; the bullets above it are the detailed record.

---

## Existing entries are authoritative

- Never duplicate a `##` date heading.
- Never silently rewrite or replace an existing section, in any mode,
  including backfill and explicit-date re-runs.
- If new evidence contradicts or meaningfully extends an existing entry (it
  looks incomplete, or something in it looks wrong), **do not touch it.**
  Report the discrepancy separately and ask the user whether to amend it. Only
  edit an existing section after they say yes.
- Explicit-date mode on a date that already has a section: report that it
  already exists (show it), do not regenerate, and only proceed if the user
  asks you to revise it.

### Guard against a concurrent run

Evidence-gathering can take a while (grepping large session transcripts,
reading diffs); the file could change under you while that's happening if a
second invocation runs at the same time.

**Immediately before writing** — right before the Edit/Write call that
inserts a new section, not earlier when the run started — re-read the history
file fresh from disk and re-check that the target date (or, for a rollup, the
`## Week: ...` heading) still has no section. If one now exists, a concurrent
run won the race: treat it exactly like any other pre-existing entry — do not
overwrite it, and say so in the report rather than silently discarding what
you generated. This costs one extra read per write and is cheap insurance —
the file is small and this is the only realistic way two runs could collide.

---

## Known limitations

State these plainly when they actually bear on a run's result — not as
boilerplate on every invocation, but don't let a thin result pass without
naming the reason if one of these is it.

- **Session evidence is machine- and install-local, not synced.** It comes
  from `~/.claude/projects/<slug>/*.jsonl` on **this** machine, under **this**
  Claude Code install, against **this exact** repo path (§Claude Code session
  evidence). A session run from another machine, a cloud/remote session, or a
  differently-pathed clone of the same repo is invisible to this skill — there
  is no synced transcript store, and this is not a bug to fix, just a
  boundary to disclose. **Git evidence has no such gap** — it reads the same
  history regardless of which machine ran this skill — so a thin entry
  reconstructed only from Git on a day the user knows involved a lot of
  discussion-only work is the signature of this limitation, and worth saying
  so rather than presenting the entry as complete.
- **First run on a new project starts from a conservative window**, not full
  history (§Default behaviour step 3) — by design, not an oversight.
- **`tomorrow` has no evidence to reconstruct** (§Date parsing) — it only ever
  records what the user states inline.

---

## Output

**Default / this-week / last-week / this-month / backfill (something was added):**

```
Updated `<Project-Name>-Daily-Updates.md` at <resolved path>

Added:
- 2026-09-08
- 2026-09-09
```

For `this week`/`last week`, list the rollup alongside the days it covers,
marked as such (e.g. `- Week: 2026-09-07 – 2026-09-11 (rollup)`) — and if only
the rollup changed (every day already existed, but the synthesis was
refreshed), say that explicitly rather than implying new days were added.

Then show the full text of each generated entry, headed bullets and Scrum
summary included — the rollup's own highlight bullets and Week summary line,
too, when one was built.

**Nothing to add** (already up to date, or no evidence for any missing date):
say so plainly, name the file and the date range checked, write nothing.

**Explicit single date:** show only that date's entry (existing or newly
generated) — no mention of other dates.

**`backfill`:** state the date range before processing (§Backfill step 2),
then the same "Added:" list on completion, which may be long.

**`status`:** the report described in §Status mode. Never followed by a write.

Always name the resolved file path at least once so the user can find it
directly outside of this skill.
