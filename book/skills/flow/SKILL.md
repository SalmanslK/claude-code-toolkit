---
name: flow
description: >
  Use when someone asks what to run for a situation — "a new FSD came in", "fix this bug end to end",
  "what do I do for a QA build" — or names a recipe. Lists the 18 ready-made recipes, or walks one
  step by step: the skills in order, the loops, a stop at each approval, and a prompt to resume in the
  next session. Holds no rules of its own.
argument-hint: "[flow name] [from step N]"
allowed-tools: Read, Glob, Grep
---

# /book:flow [name] — the Book's recipes, one step at a time

A **flow** is a ready-made recipe for a common situation: which skills run, in what order, where to loop
and where a person decides. Each recipe is a short file in `${CLAUDE_SKILL_DIR}/flows/<name>.md`. The
skills it names stay the only owners of their rules; this skill holds only the order, the loops and the
stops.

## Marks

- **✋** — a stop for a person. Never pass it on your own: approving a plan, posting to the FSD or a PR,
  opening a PR (only when the person asks), deploying, merging, sending a message.
- **⏸** — a session boundary before the step. One unit of work per session, and `/book:self-review` and
  `/book:peer-review` always run in a fresh session or a subagent, never the one that wrote the change.
- **⟲** — a loop. At most **3 rounds**, then hand to the person with what is still open.

## With no name: list them

Read the recipe files' first lines and print the 18 flows grouped as below, each with its trigger. When
the request is plain words ("the BA answered our questions"), name the flow that fits and offer to run it.

| Group | Flows |
|---|---|
| A. Requirements | `weekly-sweep`, `new-fsd-revision`, `answers-arrived`, `qa-artifacts-changed` |
| B. Features | `new-feature`, `build-task`, `finish-feature` |
| C. Defects and questions | `fix-defect`, `spec-says-x` |
| D. Reviews and merges | `review-teammate-pr`, `after-merge` |
| E. Docs health | `docs-health`, `guides-drift` |
| F. Releases and status | `qa-build`, `dev-deploy`, `status-report` |
| G. Book upkeep | `new-project`, `upgrade-book` |

## With a name: walk it

1. **Read the recipe** and show its steps, loops and *done when*, so the person sees the whole path.
2. **Check the packs.** A recipe's **Packs** line names the packs its steps need (`fe-guides`: `/book:check-guides`,
   `/book:publish-guides`, `/book:release-notes`; `deploy`: `/book:deploy`). A pack is installed when `[book] packs`
   in `devtools/factory/factory.toml` names it (each of those skills checks this too, and stops). A step whose pack is absent is **skipped, said in one line**
   ("step 5 skipped: no fe-guides pack"); a recipe never fails for a missing pack.
3. **Run each step** by invoking its skill with the arguments the recipe gives, in order. A step with no
   skill is the session's own work or the person's, as the step says.
   - At **✋**, stop and wait for the person.
   - At **⏸**, end the session's work here and print the resume prompt below.
   - At a **⟲**, count the rounds; after the third, stop with what is open.
   - A step that says "if …" runs only when that holds; say which way it went.
4. **Blocked means stop.** A step that cannot run (a source unreachable, the guard refuses, a check that
   could not be made) stops the flow there: say what was blocked and what would unblock it. Never mark a
   step done that did not run.
5. **"What is left" stays in the Book.** Keep no task list of your own; `/book:progress` updates the
   plans and `project.md`.
6. **Heavy runs one at a time.** `/book:ship` runs the local CI; never start a second full run beside it.

## The resume prompt

At each ⏸, and whenever the session stops before *done when*, print one prompt the next session can
start from — no state file; the branch, the plan and the Book hold the state:

```
/book:flow <name> from step <N> — branch <branch>; <the plan, defect or files in play>
```

`/book:flow <name> from step <N>` starts at that step, after checking the steps before it left what it
needs (the plan approved, the review READY).

## What next

- **The flow reached *done when*:** say so, and name the flow it hands to, if any (`build-task` →
  `after-merge`).
- **Stopped at ✋, ⏸ or a block:** the resume prompt above.
