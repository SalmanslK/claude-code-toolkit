---
name: plan
description: >
  Use before a feature gets code — "plan the Invoices module", "start the plan for §7", "write the
  design for this feature". Starts its plan from docs/plans/_template.md: the FSD sections it claims,
  read and quoted; its row in project.md Part 1; its Tasks in build order with role and status. A gap
  becomes a question, never a guess. Not for a feature already planned (edit its plan). Formerly
  /plan-feature.
argument-hint: <feature or FSD section>
allowed-tools: Read, Grep, Glob, Bash(git status*), Bash(git log*), Bash(git show*), Bash(git fetch*), Bash(git branch*), Bash(python devtools/checks/gen-task-rollup.py*), Bash(python3 devtools/checks/gen-task-rollup.py*), Bash(python devtools/checks/check-book.py*), Bash(python3 devtools/checks/check-book.py*)
---

# /book:plan — a plan before the code

**Every feature gets a plan before it gets code**, and the FSD wins every conflict (`CLAUDE.md`,
*Features*). This skill writes the plan's first draft from the specification — never from what seems
likely — and stops for the person to approve it before any code is written.

## Must never

- guess a requirement. What the FSD does not settle is `[PROPOSED]` in the plan and a question in
  `docs/open-questions.md` (`/book:raise question`), with a recommendation;
- copy what the code or a generated doc will own: routes and request shapes are `api-contracts.md`,
  columns `database-erd.md`, error codes the FE guide (`docs/CLAUDE.md`, *Plans*);
- write code, or start a plan that already exists: look in `docs/plans/` and `project.md` Part 1 first,
  and edit the existing plan instead.

## 1. Find what the feature is

- **The FSD sections it claims**, from the highest revision in `requirements/fsd/` (`V15` is above `V9`).
  Read every one in full, with the tables and the wireframe notes, and list the ones it touches but does
  not own.
- **What is decided already:** *Resolved* in `open-questions.md`, the questions still open in its area,
  and the plans it depends on (their status lines and Tasks).
- **What is built that it should use:** `docs/system-overview.md`, `docs/architecture.md`, and the code
  where those name it.
- `/book:check-sources` first if the FSD may have moved since the last snapshot: a plan from a stale
  revision is wrong on day one.

## 2. Write the plan

Copy `docs/plans/_template.md` to `docs/plans/<feature-slug>.md` and fill it, deleting what does not
apply (an empty heading reads as an omission):

- **The status line:** `Not started`, the owner (ask), `FSD: §<n>`, `Checked against: FSD V<n>`, the FE
  guide (— until there is one), and what it depends on.
- **§1 What the FSD says:** cited by section, the constraining words quoted (limits, defaults, exact
  messages). Anything unsettled marked `[PROPOSED]`.
- **§2–§7:** only what the FSD and the architecture already decide; a load-bearing choice gets its case
  and what was rejected. **§6 API surface:** for a feature with screens, hand it to `/book:outline-api`.
- **§8 Open questions:** each gap with its Q id, raised with `/book:raise question`.
- **§9 Tasks:** every task in build order, each with its role (`BE`, `FE`, `QA`, `BA`, `DevOps`), status
  `Not started`, and its Jira key if the project uses Jira; small enough that one pull request lands one.

Then **its row in `docs/project.md` Part 1**, in the right phase table, and regenerate the roll-up:

```
python devtools/checks/gen-task-rollup.py
python devtools/checks/check-book.py
```

## 3. Show it, then stop

Lead with: the FSD sections it covers, the questions it raised (with recommendations), the tasks, and
what it depends on. **The plan is a proposal until the person approves it.** Commit only when asked, on
the feature's own branch (`docs/CLAUDE.md`, *Which branch a doc change goes on*); departing from it later
is discussed first, and the plan changes in the same commit as the code.

## What next

- Screens to build: **`/book:outline-api`** for §6.
- Questions raised: chase them; **`/book:sync-sources`** when answers land.
- Approved: build task by task; **`/book:impact`** before the first pull request.
- **In a flow** (`/book:flow`): `new-feature` → `/book:outline-api`.
