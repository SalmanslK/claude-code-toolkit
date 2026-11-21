---
name: daily-scrum-updates
description: >
  Use when the user wants their own daily standup / Scrum update written or caught up — "standup for
  today", "what did I do yesterday", "fill in my scrum log", "my updates for this week", "backfill my
  standups", "scrum status" — as a first-person, PM-readable log rebuilt from Git and Claude Code
  transcripts, in one private file per project outside the repository, never committed. Covers today,
  yesterday, an explicit date, this/last week with a rollup, this month, backfill and status. Not for what
  every teammate did (team-daily-activity), delivery history (backend-development-history) or what is left
  (the repository's Book; pending-work-items for asks of people).
---

You keep **the user's personal daily Scrum log**: written in the user's voice as a Lead Software
Engineer, for reading out in standup and skimming by a PM and the dev team.

**Must hold (read first):**
- The log is private. The rules in
  [shared mechanics §1](references/shared-mechanics.md#1-the-private-file-rule) apply: never commit it,
  never put it in a repository, and stop on `BLOCK`.
- **Existing entries are authoritative.** Never duplicate a date, never rewrite a section, and run
  `has-entry` immediately before every write.
- **No fabrication.** Write only what the evidence supports. A gap stays visible.

## Quick reference

| Invocation | Behaviour |
|---|---|
| `/daily-scrum-updates` | Fill every missing day from the last entry to today. A first run covers the last 5 working days |
| `... today` / `yesterday` / `2026-09-08` / `09-08-2026` / `Sep 8` | That date only |
| `... tomorrow` | Only with a plan stated inline (`tomorrow: starting X`), written as planned work |
| `... this week` / `last week` | Those working days, then the weekly rollup (§Weekly rollup) |
| `... this month` | Every working day from the 1st |
| `... backfill` / `backfill N` / `backfill A..B` | Further back; the range is announced first |
| `... status` | Read-only report. Writes nothing |

## How a run goes

1. **Gather.** From the repository, run
   `python ~/.claude/skills/daily-scrum-updates/scripts/standup_evidence.py evidence --log scrum <SPEC>`
   (`status --log scrum` for status mode; `dates --log scrum backfill` first for a bare backfill).
   The script resolves the PKT dates, working days, holidays and existing entries. It gathers your commits,
   every PR merge that day, and your Claude Code sessions. What each line and each `ACTION` means:
   [shared mechanics §4–5](references/shared-mechanics.md#4-reading-the-action-on-each-day).
2. **Judge.** For each day marked `WRITE`, read what the evidence does not say on its own:
   `git show --stat <sha>`, or the diff when the message and the stat are not enough. Never claim work from a
   changed file whose purpose you cannot establish. Group related commits into one accomplishment. A day of
   only trivial commits is weak evidence: fold it into a related bullet or leave it out.
   - **Every PR merge listed is worth a bullet**, even one the user mostly did not write. Reviewing and merging
     is the user's work for that day.
   - **The verb follows the role.** For `your role: unknown`, say what you found and ask whether the user built,
     reviewed or only merged it.
   - **Sessions** surface work with no commit: investigation, design, planning, a review in a session, debugging
     that ended in "not a bug". Use only what the user landed on.
3. **Write** (§The entry). Right before each insert, run `has-entry --log scrum <date>`. If it is no longer
   `ABSENT`, a concurrent run won: do not overwrite, say so.
4. **Report** (§Output).

## The entry

File: `<Project>-Daily-Updates.md` in the configured directory, under one `# Daily Scrum Updates — <Project>`
title, most recent date first. A backfilled date goes where the order puts it.

```markdown
## 2026-09-09

* **Shipped**
  * **Warehouses and Bins closed out**: Fixed every issue found in review, including a gap that could have let deleted storage locations stay reachable.
  * **Another short heading**: One specific sentence.
* **Deployed**
  * **DEV deploy verified**: One specific sentence.

**Scrum summary:** Two to four spoken sentences for standup, leading with the same item the bullets lead with.
```

- One `## YYYY-MM-DD` per date, the unique key. **2–5 leaf bullets**; fewer when the evidence supports fewer.
- **Each leaf is `**Heading**: one sentence.`** The heading is 4–5 words naming *this day's thing*, with no
  colon, dash or semicolon inside it, and it does not repeat its tag. The sentence is one sentence, not two
  and not a semicolon run-on. A bullet that wants two sentences is two bullets.
- **Tags group the bullets.** Each item gets exactly one tag, and items sharing a tag sit under one bold
  parent. A day with exactly one item uses the flat form `[Tag] **Heading**: sentence.`

| Tag | Means | Order |
|---|---|---|
| `Shipped` | Merged into the shared branch: the product can now do it. A product feature leads over an internal tool | 1 |
| `Fixed` | A bug, defect or outage resolved | 2 |
| `Deployed` | An environment deployed or verified, or its status changed | 3 |
| `Requirements` | A spec or BA question settled, a decision or design agreed | 4 |
| `In Progress` | Reviewed, triaged, found or started, but not finished | 5 |
| `Process` | Tooling, CI, docs, conventions: helps the team, not the product directly | 6 |

- Groups go in tier order and items within a group by impact, never by commit time. Moving a group up is a
  rare judgement call; the tag still says what the item was.
- **Consolidate before tagging.** A bug found and fixed the same day is one `Fixed` item. A prep step and
  its merge are one item.
- **Plain language for a PM.** No class, interface, method or config names, and no mechanism jargon. Name the
  product area a non-engineer knows ("the invitation email", "Packing"). An id (`D53`, `Q6`, a PR number)
  may trail in a parenthetical for traceability, but it is never the subject or the heading. Frame internal
  tooling by what it now lets the team do.
- **Specific, not vague.** "Fixed some bugs" says nothing. Name what was broken and what now works.
- **Ongoing work** may read "Continued …" only with real progress that day. Never repeat a bullet verbatim
  across days.
- **`**Scrum summary:**`** ends every date: 2–4 sentences to read aloud as they are, in plain prose, and
  needing zero translation.
- **Thin evidence**: write what is supported. With nothing usable on a day the script marks `NO EVIDENCE`,
  write one bullet saying the record could not be reconstructed. Never skip the day silently.

## Weekly rollup

`this week` and `last week` also add a `## Week: <start> – <end>` section (en dash) directly above that
week's daily sections. It holds 3–6 highlight bullets and a `**Week summary:**` of 2–4 sentences, written
from the daily sections **as they stand after this run**, with same-theme days merged. The rollup is derived:
each run **replaces** that week's rollup. It is the only section this skill may rewrite. A week with no
daily sections gets no rollup. Other modes never build one.

## Output

```
Updated `<Project>-Daily-Updates.md` at <resolved path>
Added: 2026-09-08, 2026-09-09   (and "Week: … (rollup)" when built; say if only the rollup changed)
```

Then the full text of each new entry. For an explicit date, show only that date: existing or new. For
nothing to add, name the file and the range checked. For `status`, give the script's report and write
nothing. Name the path once. Name a known limit
([shared mechanics §6](references/shared-mechanics.md#6-known-limits)) only when it explains a thin result.

## What next

- For the team's view of the same days, use **team-daily-activity**.
- For module dates, deployments and the overall status, use **backend-development-history**.
- To track asks of people and open decisions, use **pending-work-items**.
