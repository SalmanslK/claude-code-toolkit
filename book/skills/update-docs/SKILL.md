---
name: update-docs
description: >
  Use when, and only when, the code is already known to be right and the docs have lagged: brings the documentation, FE guides included, in line with what the code does. Code wins on behaviour, never on intent.
  Applies changes and reports them. Not for when it is not certain which side is wrong
  (book:check-docs), nor docs against each other (book:check-consistency). Formerly
  /docs-update-from-code.
---

You are bringing this repository's documentation back in line with its code.

**Code is the source of truth for what the system *does*. It is never the source of
truth for what the system *should* do.** That distinction is the whole skill. Get
it wrong and you will faithfully document a bug as a design.

*The Book's command is `book`: `python devtools/book.py <command>` from the project's root.*

---

## Which skill is this

One-way, for a change **you performed**; the siblings, by what each compares, are
the AI guide's *Which docs skill* (the project's `AI-DEVELOPMENT-GUIDE.md`) table. Run `book:check-sources` first if the docs cite an FSD
section you are about to rewrite.

**If you find yourself unsure whether the code is correct, stop and run
`book:check-docs`.** This skill has no mechanism for being wrong safely.

**Scope is the change.** `git diff --name-only <base>` gives the code you changed;
`python3 devtools/book.py impact <paths>` names the guides, plans and
generated docs it reaches. Those documents, at the sections that describe the
changed code, are the pass — not the whole set.

**The window this skill is for is narrower than it looks.** It is not "faster" in
the sense of skipping analysis — the stop conditions below and the "what must
survive" table demand most of the same reading. What it saves is the
report-and-approve round trip, and it earns that only when you already know what
changed because you changed it.

---

## What you may edit

Only documentation we write and maintain:

- `docs/system-overview.md`, `docs/architecture.md`, `docs/project.md`,
  `docs/open-questions.md`
- `docs/plans/*.md`
- `CLAUDE.md`, `README.md`, `devtools/README.md`, `database-scripts/README.md`
- A built module's FE guide in `docs/fe-integration-guides/`, and `api-conventions.md` there —
  [A built module's FE guide](#a-built-modules-fe-guide)
- XML doc comments and inline comments, where they make a claim that is now false

## What you must not touch

**`requirements/`** is *read-only* (the project's `CLAUDE.md`): evidence, never a target. If the
code disagrees with the FSD, **that is not a documentation problem** — see the stop
conditions below.

**`docs/archive/`** is historical by definition. Leave it; check only that it is
still labelled as superseded.

**Generated docs** — `docs/api/api-contracts.md`, `docs/database-erd.md`, the generated
tables in `project.md` — are regenerated, never edited
(`docs/CLAUDE.md`, *Generated*).

**Implementation code**, beyond a comment that states something untrue.

---

## What must survive, no matter how little code supports it

This is where a literal reading of "remove speculative content" does real damage.
None of the following has a code counterpart, and **all of it is load-bearing**:

| Keep | Why |
|---|---|
| **`docs/open-questions.md`** — every open and answered question | The questions, their recommendations and their answers. No code will ever evidence these |
| **`docs/project.md` Part 3** and `docs/archive/requirements-history.md` — requirements history | What changed between FSD revisions |
| **The delivery schedule and feature status tables** | Facts about the project, not about the code |
| **"Not built yet", "Known trade-offs", "Open decisions"** | Deliberate statements that something is absent. Deleting them makes a gap look like an oversight |
| **`[PROPOSED]` and `[DEFERRED]` markers** | They mark an unanswered question, not stale text |
| ***Why* a decision was made, and what would change it** | The most valuable content in `architecture.md`, and the least code-evidenced |
| **`docs/archive/`** — closed defects, answered questions, plan and architecture history | The record of where code departed from design — including mistakes. Archived, never deleted |
| **Bugs and traps recorded as warnings** | e.g. the query-filter folding bug, the PostgreSQL 18 volume path. These describe things that are *not* in the code precisely because they were fixed |

**The test:** would deleting this sentence lose knowledge that the code cannot
re-derive? If yes, it stays regardless of whether the code mentions it.

---

## Stop conditions

Stop and report rather than editing when:

- **The code contradicts the FSD.** The FSD wins every conflict. This is a bug or a
  question for `docs/open-questions.md` — never a doc rewrite that enshrines the
  code's version.
- **The code contradicts a dated answer** recorded against a question. Someone
  decided that; the code drifting from it is a finding.
- **The code and the tests disagree.** You cannot tell which is intended. Report it.
- **The behaviour looks wrong.** If documenting it accurately would mean writing
  down something nobody would have asked for, say so instead.
- **You cannot establish intent** — the behaviour exists and nothing explains why.
  Describe what it does, flag that the reason is unknown, and do not invent one.

In every case: **finish the rest of the pass, and list what you stopped on.**

---

## The pass

**Where the edits go:** docs/CLAUDE.md, *Which branch a doc change goes on* — check the branch
before the first edit.

**Read `../check-docs/references/comparison-checklist.md`** and work through
it. It lists what to compare, where drift has actually happened here, and the rule
about measuring numbers rather than carrying them forward.

It is shared with `book:check-docs`: **add a new concern there**, as its header says.

Work outward, so later sections rest on facts established earlier: architecture,
then domain, then database, then API, then flows, then configuration, then tests
and diagrams. Where the checklist says *compare*, you **update the documentation**
— unless a stop condition above applies.

---

## A built module's FE guide

A built module's guide in `docs/fe-integration-guides/` is **our implementation as shipped**
(`docs/CLAUDE.md`, *Front-end documents*), so the
pass brings it in line too. A module with no guide yet is not this skill's: its contract is
drafted by `/book:outline-api`, and its guide is written when it ships.

- **What to compare** is the checklist's *API* concern, as the front end sees it: endpoints,
  request and response shapes, the permission each needs, status codes, error codes and their
  messages, and every *Deviations* row. Read them from the endpoint, its DTOs, validators and
  error definitions, and its tests; routes, request shapes and permissions also from
  `api-contracts.md` as regenerated.
- **Where each fact goes** is `api-conventions.md` (the dotnet pack):
  a rule every endpoint shares is stated there, never in a module guide, and the differences it
  lists once are not repeated as a module's deviations.
- **A change the front end must act on** also goes under the guide's *Changes the FE may not
  have consumed* (add the section if it has none); older entries move to the archive as
  `docs/CLAUDE.md`'s table says, and are never just deleted.
- **Code wins on behaviour, never on intent.** The guide says what the API does, because that
  is what the front end calls. Where the code differs from the front end's contract
  (`requirements/fe-api-contracts/`) for a reason the FSD, a *Resolved* answer or the plan gives,
  that is a *Deviations* row with its *Why*. Where it differs from the FSD, it is a stop
  condition: a `defects.md` row or a question, and the guide names its id beside the behaviour —
  never a *Deviations* row whose *Why* makes the code's version look chosen.
- **Then the header's *Last checked against the code* line:** today, and the commit checked.

`check-fe-guides.py` already fails a branch whose `api-contracts.md` changed with no guide
change. It cannot see a response-only change, nor whether the guide is right: touching the
date line satisfies the check, not this pass.

---

## House rules that still apply

This skill edits documentation, so these bind it: *one topic, one owner* (the project's `CLAUDE.md`);
*no new file* (the project's `docs/CLAUDE.md`) and *no deleted history* (the project's `docs/CLAUDE.md`);
*a question to `open-questions.md`* (the project's `CLAUDE.md`), never answered by guesswork.

Run `python3 devtools/checks/check-book.py` when you are done — it checks every
link and anchor, every document's owner, and history in live documents.

---

## Report

Finish with:

1. **Files changed**, and what changed in each. **If an FE guide is among them, say the
   front end's Drive copy is stale until `/book:publish-guides` runs.**
2. **Corrections that mattered** — where the documentation had been actively wrong,
   as opposed to merely thin. These are the ones worth a reader's attention.
3. **Content removed**, and why it was safe to remove.
4. **Stop conditions hit** — every place the code and the requirements, the tests,
   or plain sense disagreed. **This is the most important section**; a pass that
   found nothing to escalate either got lucky or was not looking.
5. **Gaps** — implemented behaviour whose intent could not be established.
6. **Verification** — `check-book.py` always; `dotnet build` if a `.cs` comment
   changed. This skill changes no behaviour, so it runs no tests of its own.
   Report the numbers.

---

## The rule that matters most

**Accuracy over tidiness.**

A document that says "we do not know why this works this way" is more useful than a
confident sentence someone invented to make the page look finished. If the code
cannot tell you the answer, say that it cannot.

---

## What next

- A stop condition hit: `/book:check-docs` on that area, or a `defects.md` row or question.
- An FE guide changed: `/book:publish-guides`, so the front end's Drive copy matches.
- Edits on a `chore/docs-<slug>` branch: its pull request opens only when the person asks
  (CLAUDE.md, *Git*).
- **In a flow** (`/book:flow`): `finish-feature` → `/book:publish-guides`; `docs-health` → `/book:check-permissions`.
