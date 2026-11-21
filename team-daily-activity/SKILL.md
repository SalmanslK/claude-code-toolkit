---
name: team-daily-activity
description: >
  Use when the user wants to know, record or review what each developer on the team did on a given day or
  week in the current repository — "what did the team do yesterday", "who worked on what this week",
  "track each dev's daily activity", "who was idle", per-person standup prep, 1:1 or sprint review notes.
  Rebuilt from Git for every contributor, the user included, into one private log per project outside the
  repository. Not for the user's own first-person standup log (use daily-scrum-updates), a module's delivery
  history or overall status (backend-development-history), or anyone's performance review.
---

You keep **the user's private, lead's-eye log of what every developer did each day** in the current
repository. It is a standup board for the user before standup, a 1:1 or a sprint review. It is not a project
document and not a performance review.

**Must hold (read first):**
- The log is private. The rules in
  [shared mechanics §1](../daily-scrum-updates/references/shared-mechanics.md#1-the-private-file-rule)
  apply: never commit it, never put it in a repository, stop on `BLOCK`, and run read-only git only.
- **Git only, for everyone.** Claude Code transcripts are the user's alone. Using them would make the user's
  row richer than everyone else's in a file whose point is to compare side by side.
- **Existing entries are authoritative**, except a provisional today (§Provisional today). Run `has-entry`
  immediately before every write.

## Quick reference

| Invocation | Behaviour |
|---|---|
| `/team-daily-activity` | Fill every missing day from the last entry to today; a first run covers the last 5 working days |
| `... today` / `yesterday` / `2026-09-16` / `Sep 16` | That date only. On a new file, that date only |
| `... this week` / `last week` / `this month` | Every working day in that span. No rollup |
| `... backfill [N or A..B]` | Further back; the range is announced first |
| `... status` | Read-only: path, last date, missing days, known devs, unmapped authors |
| `... dir=<path>` | `--dir <path>` for this run only |

## How a run goes

1. **Gather.** From the repository, run
   `python ~/.claude/skills/daily-scrum-updates/scripts/standup_evidence.py evidence --log team <SPEC>`
   (`status --log team` for status). For each day it prints one `DEV <name>` block per developer with
   evidence, in the `authors` order and unmapped people last. Each block holds:
   - `REVIEWED AND MERGED` lines;
   - `HEADLINE` PR lines (the PR's author by commit count; the merger);
   - `COMMIT` lines, with where each landed and whether it was merged by the end of that day.

   It also prints `NO ACTIVITY` and `UNMAPPED` lines. The meaning of each line and each `ACTION`:
   [shared mechanics §4–5](../daily-scrum-updates/references/shared-mechanics.md#4-reading-the-action-on-each-day).
   Developer emails live in the `authors` key of the private config. Never write one into this skill.
2. **Judge.** Read `git show --stat <sha>` when a message does not say what a commit did, and the diff only
   when the stat does not settle it. Describe a `D`/`Q` id from the citing commit's own revision
   (`git show <sha>:docs/defects.md`), never from the working tree. Cite an id only if it meant one thing
   that day.
3. **Write** (§Entry shape). Right before each insert, run `has-entry --log team <date>`.
4. **Report** (§Output).

## Entry shape

This is the whole contract: no preamble, no commit or line counts, no clock times, no closing notes.

```markdown
## 2026-09-16

### Developer A
* **Packing module merged**: Closed the front-end team's Packing gap report and made two simultaneous creates on one event safe, landing it in dev (PR #64, merged by Developer D).
* **Strict JSON numbers API-wide**: Quoted numbers are now rejected on every endpoint and the API description shows the real wire shape (D80).

### Developer B
* **Returns, Refunds & Exchanges built**: Planned the stage against the FSD, built it with its FE guide and smoke script, and put it up for review (`feature/order-fulfilment-returns`, not yet merged).

### Developer D
* **Reviewed and merged two modules**: Took Developer A's Packing PR and Developer C's Shipping PR through review and into dev (PRs #64 and #70).

_No activity: Developer C_
```

1. `## YYYY-MM-DD`: one per date, most recent first, under one `# Team Daily Activity — <Project>` title.
2. One `### <Display name>` per developer with evidence, in `authors` order, unmapped developers last. A
   developer with no evidence has no section.
3. **1–4 bullets** per developer, each `**Heading**: one sentence.`
   - **Heading:** 3–6 words naming this day's thing. A product name keeps its own punctuation. Otherwise,
     no colon, dash or comma.
   - **Sentence:** what changed for the product or the team, in words a PM reads without asking. Name the
     feature area, never a class, method or config key.
   - **One trailing parenthetical:** PR number(s), the branch in backticks, a defect id, `merged by <Name>`,
     or `direct to dev, no PR`. It is traceability, never the subject.
   - **Order within a developer:**
     - teammates' PRs they reviewed and merged;
     - their own merged PRs by impact: features, then fixes, then docs or process;
     - work still open at the end of the day.
   - **A merged PR is the author's headline** on the day it merged, even when its commits were earlier.
     Its `COMMIT` lines fold into it.
   - **Work open at the end of the day** is in progress ("started", "continued", "not yet merged"), even if it
     merged later. Never write "no PR yet": Git cannot see an open PR.
   - **Budget:** same-theme commits make one bullet, review fixes make one bullet, and a day of trivial
     commits gets one short bullet. Over four, fold by area until it fits: all reviews into one, all
     docs/process into one, then fixes on one screen or module. List every folded PR in the parenthetical.
4. `_No activity: A, B_`: the known developers with no section, in `authors` order. Write
   `_No activity: —_` when everyone was active. The line is always present.

Nothing from a neighbouring date goes in. A PR merged at 00:11 belongs to the next date.

## Provisional today

A section for the current date starts with the `MARKER` line the script prints
(`_Provisional — as of HH:MM PKT_`). The next run that covers that date replaces the section whole and
drops the marker once the day is over. Otherwise a run at 19:40 would freeze a day with hours still left.

## Output

```
Updated `<Project>-Team-Daily-Activity.md` at <resolved path>
Added: 2026-09-15, 2026-09-16
Unmapped authors: <name> <email> → add "email": "Name" to authors   (omit if none)
```

Then the full text of each added section. `status` prints the script's report and writes nothing. Name the
path once. Report unmapped authors to the user; never add them to the map yourself.

## What next

- For the user's own first-person standup line, use **daily-scrum-updates**.
- For module dates and deployments across the project's life, use **backend-development-history**.
- When the log shows work waiting on someone, add the ask with **pending-work-items**.
