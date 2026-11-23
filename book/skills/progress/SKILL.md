---
name: progress
description: >
  Use after a run of merges, before a status meeting, or when asked "what is left". Brings each plan's
  tasks and docs/project.md up to date with what merged into dev (Built with its PR, In progress for
  open branches), regenerates the task roll-up, and lands it through a pull request. Not for asks of
  people, or whether a plan matches the code (book:check-docs). Formerly /project-progress.
---

# /book:progress — the task lists, from what dev holds

**One question:** what has merged into `dev` since the last update, and which tasks did it
deliver? The answer goes into the plans' **Tasks** sections — the only place a task's status is
written — and `docs/project.md`'s three generated tables follow — *Task progress*, *Open tasks*
and *Delivery pace* (`devtools/checks/gen-task-rollup.py`).

**Only dev counts.** `Built` means merged into `dev`, nothing else: not a green branch, not a
deployed host, not a closed Jira issue. The evidence is read from `origin/dev`; the working tree
is never evidence.

**Dev takes no commits.** `CLAUDE.md`: `dev` requires a pull request. This skill works on a branch
cut from `origin/dev`, and its pull request into `dev` opens only when the person asks
(CLAUDE.md, *Git*).

---

## Steps

### 1. Start from dev

1. `git status --short` — **if the checkout has someone else's uncommitted work, stop and say
   so.** Never stash or carry it.
2. `git fetch origin`, then
   `git checkout --no-track -b chore/docs-project-progress-<YYYY-MM-DD> origin/dev` — a general
   refresh, so `chore/docs-<slug>` (docs/CLAUDE.md, *Which branch a doc change goes on*).
   **`--no-track`**, so a push cannot land on `dev`. Check with `git branch -vv`.

### 2. Read the evidence

```
python devtools/checks/task-evidence.py            # merged since dev last changed docs/project.md
python devtools/checks/task-evidence.py --since <ref>
```

It lists each pull request merged in that span — its branch, the plans it changed, the D, Q and
Jira ids it carries, the task rows already citing it — and the work branches not merged. It
reads git only and changes nothing.

### 3. Match each merged pull request to its tasks

For every pull request in the report, decide which task rows it delivered, from — in this order —
the plans it changed, the ids in its branch and commits, and its branch name against the task
text. Then:

| What the evidence shows | What to change |
|---|---|
| It delivered a task, completely | That row: `Built`, PR `#n`, **Merged** the day it merged (the report's *Merged* column) |
| It delivered part of a task | That row: `In progress`; say which part in the report, not the row |
| Feature work no task lists | A new row at the end of the table, with the next number, `Built`, PR `#n`, its Merged date — the plan's list should say what was delivered. **Never renumber a row**: every reference to a task number must keep landing (`_template.md` §9; `gen-task-rollup.py --check` wants 1, 2, 3 … in order) |
| A defect fix (a D id), docs, tooling, a sync | **Nothing** — a defect lives in `defects.md`, not a task list — unless the plan lists the fix as a task |
| A task row cites it but is not `Built` | Correct the row, or say why it stays |

**A task is `In progress` only with a work branch** in the report's second table carrying it.
A plan that exists only on a branch is not on `dev`: its `project.md` row says *on
`<branch>`, not merged*, and its tasks wait for its merge.

**`Blocked` stays blocked** until the plan's reason is gone — an FSD revision that writes the
section, an answered question, a merged dependency. Name the evidence when unblocking.

### 4. Regenerate — the statuses follow

```
python devtools/checks/gen-task-rollup.py
python devtools/checks/gen-task-rollup.py --check
```

It rewrites the generated tables **and sets each plan's status line and Part 1 Status from its
`BE` tasks** (the rule is in the script's header), printing each status it changed. **Never set
those, or edit the generated tables, by hand** — a status that reads wrong is a task row to
correct, then rerun. Yours, for each plan whose tasks changed: the Part 1 row's PR that completed
it and its open items — one line, current state, no build story (`docs/CLAUDE.md`).

### 5. Report, then land it — with agreement

Print one table: plan, task, old → new status, and the evidence (PR, branch or id), then the
feature statuses the script changed. List what
was **not** changed and why — a merge with no task, a branch too quiet to call progress, a
`Blocked` row left blocked. Then ask before committing. With agreement:

1. Commit: imperative, no tooling attribution — *"Record task progress through `<dev sha>`"*.
2. `/book:self-review` on that commit, which records its READY verdict.
3. `/book:ship` — the local CI, the description, and the push and pull request only when the person
   asks. A commit after step 2 needs both again.

---

## Never

- **Commit or push to `dev`**, or mark anything `Built` from a branch, a deploy or Jira alone.
- **Invent a PR number or a Jira key.** A Jira key goes in only when the issue itself says it
  tracks the task.
- **Change a plan's design text** — this skill moves task statuses and feature status lines only.
  A design that no longer matches the code is `/book:check-docs`'s finding.
- **Delete a task row.** A task dropped from scope stays, `Dropped`, with the decision named; one
  carried into another plan stays, `Moved`, linking to where it went.
- **Move a task on its own judgement.** `Moved` is the owner's decision, made in the change that
  writes the task into its new plan.

---

## What next

- Drift between a plan and the code found on the way: `/book:check-docs`.
- Asks of people and decisions awaited, which no task row holds: the person's private tracker,
  linking to the Book for the rest.
- **In a flow** (`/book:flow`): `weekly-sweep` → done; `new-fsd-revision` → done; `qa-artifacts-changed` → done; `finish-feature` → done; `after-merge` → `/book:publish-guides`; `qa-build` → `/book:fact-check`; `status-report` → `/book:write-for`.
