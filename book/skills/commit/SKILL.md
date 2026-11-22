---
name: commit
description: >
  Use when the user asks to commit their changes ("/book:commit", "commit this") on a work branch.
  Reviews the branch first, stops on blockers, then commits in logical groups with short human-style
  messages and no Claude/Anthropic attribution. Never on dev, qa, uat or main.
---

Follow these steps exactly.

*The Book's command is `book`: `python devtools/book.py <command>` from the project's root.*

## Step 0 — Where you are

`git branch --show-current`. On `dev`, `qa`, `uat` or `main`, **stop**: CLAUDE.md
forbids committing there. Say so and offer `git checkout -b <branch>`, which keeps
the changes.

## Step 1 — Code review

Take the fingerprint of what is about to be committed:

```bash
python devtools/book.py fingerprint
```

It fetches, then hashes the change against `origin/dev` — committed, uncommitted and
untracked — the same command `/book:self-review` prints its `Fingerprint:` from, stacked
branch or not. **It must print a hash**: a failed fetch or no merge base stops here, and
you say so. The READY review's `Fingerprint:` is what Step 5 records the verdict with. Never
hash the diff by hand. Committing in another worktree than the session started in, follow that
worktree's copy of this skill and of `book:self-review` where they differ: a skill loads from the
session's start folder, whose branch may hold an older copy.

**A `READY` verdict from a `/book:self-review` run in a fresh context — a subagent, or another
session — whose `Fingerprint:` line equals this hash stands** — a verdict with no such line does not — say so in one line and go to Step 2. Anything else —
no verdict, a different fingerprint, a `NOT READY`, or a review run inline in the session that
wrote the change — run the `book:self-review` skill **in a subagent** ([CLAUDE.md, *Working with AI
here*](CLAUDE.md#working-with-ai-here)) and wait for its full output.

- **"NOT READY – Fix blockers before submitting PR"**: show the blockers and
  **stop**. Do not commit.
- **"READY – Safe to submit PR"**: continue.
- **The review stopped without a verdict** (it was blocked — an FSD section it could not
  read, a fetch that failed): relay what blocked it and **stop**. No verdict is not a
  READY.

## Step 2 — Group by concern

`git status` and `git diff --stat`. **One logical concern → one commit.** Several
(an application fix + new tooling + docs) → several commits, each independently
meaningful, in this order:

1. **Application code** (`src/`), grouped by the fix or feature it belongs to
2. **Tests** (`tests/`) for that code
3. **Tooling / skills** (`.claude/`, `devtools/`, config)
4. **Documentation** (`CLAUDE.md`, `docs/`, README)

Two exceptions keep a group together: a behaviour change and **the doc that owns
it** go in the same commit ([CLAUDE.md, *Features*](CLAUDE.md#features)), and so do
a migration and its regenerated ERD.

**A general doc refresh is not this branch's** ([docs/CLAUDE.md, *Which branch a doc change goes on*](docs/CLAUDE.md#which-branch-a-doc-change-goes-on)).
If a doc group holds one, leave it uncommitted, name it in the Result, and offer
`git checkout --no-track -b chore/docs-<slug> origin/dev` for it.

For each group: `git add` only its files, write its message (Step 3), commit
(Step 4). The Step 1 review covered the whole change; it is not repeated per group.

**Tests, once, before the first commit** ([CLAUDE.md, *Building and testing*](CLAUDE.md#building-and-testing)).
`python devtools/book.py impact --ci` prints `tier=`, `filter=` and `reason=` — never
work a tier out by hand:

| Tier | Run |
|---|---|
| `checks` | no build or tests; say so |
| `build` | `[commands] build`, then `[commands] test` |
| `modules`, `full` | `build`, then `[commands] integration` with the printed filter |

Read the executed, passed and skipped counts ([`tests/CLAUDE.md`](tests/CLAUDE.md#choosing-what-to-run)):
a failure, an integration skip, or `0` executed **stops here** — nothing is committed. If
`book impact` fails, say so and stop.

## Step 3 — The message

`git diff --cached --stat`, then one line that:

- is under 72 characters, imperative, and says **what** changed, not how
- **matches the repository's style** — `git log -5 --format=%s`: a capitalised
  sentence with no type prefix
- on a `fix/*` branch, carries the `D`/`Q` id or the Jira key **in every commit** —
  tests, tooling and docs groups too; the commit-msg hook refuses one without
  (`… (D1)`, `… (PROJ-310)`). Elsewhere, the id when the commit fixes or answers one
- has **no** body, co-author line, trailer, or mention of Claude, Anthropic or AI
  tooling

```
Add UserPreference feature with API and DB migration
Fix timezone default in UserPreference entity (D1)
Keep a deleted user's email reusable by ordering the lookup (D2)
```

## Step 4 — Commit

Write the message (the Write tool) to a file **outside the repository** — the session's
scratchpad, else the system temp folder — check it with the commit-msg hook's own script, and
commit from that file only when it passes. Spell the path out literally in both commands; the
guard refuses a path held in a shell variable:

```bash
python devtools/checks/check-commit-msg.py <msg-file> && git commit -F <msg-file>
```

A refusal names the rule; fix the message and check again. No heredoc. If a **git hook** (`.githooks/pre-commit`) fails, fix what it names and
commit again — never `--no-verify`. A **guard** refusal is different: report it and stop
(CLAUDE.md — never route around it).

## Step 5 — Record the verdict

After the last commit, record the Step 1 review for it, so `book pr open` needs no
second review:

```bash
python devtools/book.py reviewed READY --fingerprint <the review's Fingerprint: hash>
```

It records READY for the head commit only when the tree is clean and the committed
content is exactly what was reviewed — the same fingerprint. Anything else refuses
with its reason: something left uncommitted (a doc refresh moved to its own branch),
an edit or a new file after the review. A refusal is not a failure of the commit;
say what it said, and that `/book:self-review` must run on the head commit before
`pr open`. Never record without the fingerprint here.

## Result

```
Review: READY (<reused | ran>) · <fingerprint short>
Tests: tier <tier> (<reason>) — <executed / passed / skipped per suite> | none (checks)
Committed: <sha> <message>   (one line per commit)
Recorded: READY for <sha> | not recorded — <the tool's reason>
Left uncommitted: <paths> | none
```

---

## What next

- **Committed with READY recorded:** `/book:ship` — it runs the local CI on the head commit, drafts the
  description, and pushes and opens the pull request only when the person asks (CLAUDE.md, Git).
- **Stopped on a blocker:** fix it, then run `/book:commit` again; nothing was committed.
- **Not recorded:** the tool said why — commit what is left, or review again, then record.
- **In a flow** (`/book:flow`): `build-task` → `/book:ship`; `fix-defect` → `/book:ship`; `upgrade-book` → `/book:ship`.
