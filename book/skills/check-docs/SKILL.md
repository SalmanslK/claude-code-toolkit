---
name: check-docs
description: >
  Use when the docs and the code may disagree and it is not known which is wrong — before a release,
  after a run of merges, or when a branch that changed docs/ is about to open its PR. Audits both ways,
  reports with evidence and stops for approval. Not for refreshing docs from code already trusted
  (book:update-docs), nor docs against each other (book:check-consistency). Formerly /docs-vs-code.
allowed-tools: Read, Grep, Glob, Bash(git diff*), Bash(git log*), Bash(git ls-files*), Bash(git show*), Bash(git grep*), Bash(pdftotext *), Bash(python3 devtools/checks/check-book.py*), Bash(python devtools/checks/check-book.py*), Bash(python3 devtools/checks/test-trend.py*), Bash(python devtools/checks/test-trend.py*), Bash(python3 devtools/checks/gen-api-contracts.py --check*), Bash(python devtools/checks/gen-api-contracts.py --check*)
---

You are auditing whether this repository's **code and its documentation agree**.

This is not a documentation refresh. **Neither side is presumed correct.** Code
carries bugs, half-finished work and things nobody meant to keep; documentation
carries yesterday's design, tomorrow's intention, and decisions that were reversed
in a chat thread. The job is to find where they disagree, work out which one is
wrong, and say so with evidence.

**Your first deliverable is a report, not a commit.**

*The Book's command is `book`: `python devtools/book.py <command>` from the project's root.*

---

## What counts as documentation here

**Only what we write and maintain:**

| | |
|---|---|
| `docs/system-overview.md` | what the product is |
| `docs/architecture.md` | how we build |
| `docs/project.md` | where we are — features, requirements history |
| `docs/open-questions.md` | every BA question, open and answered |
| `docs/defects.md` | every open defect, and a one-line entry per fixed one |
| `docs/plans/*.md` | one design per feature |
| `docs/fe-integration-guides/*.md` | how the front end calls each built module, and what every module does the same way |
| `docs/api/fe-api-coverage.md` | the endpoints the front end requires, and whether we have them |
| `docs/qa-artifact-test-suite.md`, `docs/e2e-testing.md`, `docs/dev-smoke-test-suite.md` | which QA cases and checks our tests prove |
| `docs/api/api-contracts.md`, `docs/database-erd.md` | **generated** — compared, never edited: a mismatch is fixed by regenerating, or in the generator |
| `CLAUDE.md` | the rules |
| `README.md`, `devtools/README.md`, `database-scripts/README.md` | how to run it |
| XML doc comments and inline comments | they make claims too, and they go stale |

**`requirements/`** is [read-only](CLAUDE.md#layout): evidence in this audit, often the
deciding evidence. If the code contradicts the FSD, the finding is against the code or
against a question in `docs/open-questions.md`, never against the PDF.

`docs/archive/` is historical by definition. Do not report it as stale; check only
that it is still marked as superseded.

---

## Phase 1 — Discovery

Read, do not assume. The point of the audit is that memory and documentation are
exactly the things under suspicion.

**Scope first — it decides how much of the below is read:**

| Asked about | Read |
|---|---|
| A module or feature | Its plan, its FE guide, its rows in the owning docs; its feature folders across the layers, its endpoints, configurations and migrations, its tests — and the cross-cutting mechanisms it goes through, at the point it uses them |
| A change — a branch, "DEV minus QA", a run | `git diff --name-only <base>..<head>`; the changed code and the docs that describe it, both ways; `/book:impact`'s map (`book impact <paths>`) for which docs those are |
| The whole repository | Everything below |

State the scope in the executive summary. **Run
`python3 devtools/checks/check-book.py` first** — broken links and anchors are its
findings, not this audit's.

**Code** (the whole-repository list): aggregates and value objects in `Domain/Features/`, marker interfaces in
`Domain/Abstractions/`, commands, queries and handlers in `Application/Features/`,
ports in `Application/Abstractions/`, endpoints in `API/Endpoints/`, EF
configurations and repositories in `Persistence/`, interceptors, migrations and the
model snapshot, `database-scripts/seed/`, external implementations in
`Infrastructure/`, options and pipeline wiring in `API/Configuration/`,
`Directory.Packages.props`, `bitbucket-pipelines.yml`, `Dockerfile`, `compose*.yaml`,
`appsettings*.json`.

**Tests:** `UnitTests` for domain rules, `ArchitectureTests` for the guardrails,
`IntegrationTests` for anything touching a database. Test names in this repository
are sentences — read them; they state intended behaviour more plainly than most
comments.

**Documentation:** the files listed above, in full.

---

## Phase 2 — Compare

**Read `references/comparison-checklist.md`** and work through it. It lists what to
compare, where drift has actually happened in this repository, and the rule about
measuring numbers rather than carrying them forward — with the tool that prints each count.

It is shared with `book:update-docs`: **add a new concern there**, as its header says.

---

## Phase 3 — Classify every mismatch

| Type | Meaning | Usual action |
|---|---|---|
| **A** | Documentation right, code wrong | Change the code |
| **B** | Code right, documentation stale | Change the documentation |
| **C** | Both unclear or self-contradictory | Needs a decision |
| **D** | Code, documentation and tests all disagree | **Escalate — never resolve silently** |
| **E** | Implemented, documented nowhere | Add documentation |
| **F** | Code does something no requirement or decision explains | Flag; do not rationalise it |

---

## Phase 4 — Weigh the evidence

In this order. When a higher source contradicts a lower one, **say so** rather than
quietly picking a winner.

1. **The FSD.** It wins every conflict; where it is silent or contradicts itself,
   [Which document wins](docs/open-questions.md#which-document-wins) says what
   decides.
2. **Answered questions in `docs/open-questions.md`.** An answer with a date settles the
   matter and outranks any design written before it.
3. **A feature plan's decisions** — the design as built, each with its *Why*. How
   the code came to depart from an earlier design is in `docs/archive/plans-history.md`.
4. **Integration and architecture tests.** They run against a real database and a
   real host, so they are strong evidence of intended behaviour.
5. **The domain and application code**, where it is consistent with itself.
6. **Database constraints and migrations.**
7. **Unit tests.**
8. **Code comments**, which are assertions and can be false — this repository has
   already shipped a comment claiming a foreign key that did not exist.
9. **Historical notes.**

**Never invent a requirement.** If a behaviour exists and nothing explains why,
that is Type F, not an opportunity to write a rule that matches the code.

**Do not delete history — archive it.** Correct the current statement in place and
move the old one, verbatim, to the matching file in `docs/archive/` (see
`docs/CLAUDE.md`). What must not survive is history *presented as current*.

---

## Phase 5 — Risk

**Critical** — anything that leaks or corrupts data across tenants, a wrong
authorization rule, an API contract mismatch, incorrect database documentation
someone would act on, a deployment instruction that would fail or destroy data.

**High** — a business rule implemented differently from the FSD, wrong validation,
wrong status transitions, a feature plan that misdescribes what shipped.

**Medium** — architecture documentation that no longer matches the layout,
terminology drift, an incomplete flow.

**Low** — formatting, duplication, wording.

---

## Phase 6 — Report, then stop

Deliver:

**1. Executive summary** — totals by risk and by type, and how many need a human
decision rather than an edit.

**2. The findings table.**

| ID | Area | Documentation says | Code does | Tests say | Type | Source of truth | Action | Confidence |
|---|---|---|---|---|---|---|---|---|

**3. Per finding**, with file paths and line numbers on both sides, the conflict
stated in one sentence, the recommendation, the reason, and a confidence of High,
Medium or Low.

**4. The synchronisation plan**, grouped into *code changes*, *documentation
changes*, and *needs a decision*.

**5. A decision list** — `AUD-001 → Update Code`, one line each.

**Then stop.** Do not begin changing things. A trivially obvious Type B — a stale
test count, a renamed file — may be fixed in passing and listed as done, on the
branch Phase 7 names (check it first); anything
touching behaviour, contracts, schema or a business rule waits for approval.

---

## Phase 7 — Apply what is approved

**Where the edits go.** Code changes go on a work branch; doc changes as
[docs/CLAUDE.md, *Which branch a doc change goes on*](docs/CLAUDE.md#which-branch-a-doc-change-goes-on) says — check the branch before the first edit.

**Code changes** keep the existing architecture, CQRS shape, domain boundaries and
database integrity. Update or add tests in the same commit.

**Documentation changes** describe only what the code, schema, contracts, tests and
configuration actually do. Do not write intent as though it were behaviour.

The house rules bind it: [one topic, one owner](CLAUDE.md#where-knowledge-lives),
[no new file](docs/CLAUDE.md#new-files), [a question to `open-questions.md`](CLAUDE.md#features).

Afterwards, verify in proportion to what changed, and report the numbers rather
than asserting success:

- **Always:** `python3 devtools/checks/check-book.py`.
- **A `.cs` file changed** (a comment included): `dotnet build`.
- **Code behaviour changed:** the tests CLAUDE.md's
  [Building and testing](CLAUDE.md#building-and-testing) names for it —
  the touched feature's, or the full suite when the change is cross-cutting.

Docs-only changes need no test run.

---

## The rule that matters most

**Analyse first. Change later.**

An audit that quietly edits until everything matches has destroyed the evidence
that anything was ever wrong. Being right about *which* side was wrong is the
entire value of the exercise.

---

## What next

- Approved Type A findings: each code fix on its own work branch, with its `defects.md` row.
- Approved doc fixes outside a work branch: commit them on the `chore/docs-<slug>` branch;
  its pull request opens only when the person asks ([CLAUDE.md, *Git*](CLAUDE.md#git)).
- An FE guide changed: `/book:publish-guides`. Requirement text in doubt: `/book:check-sources`.
- **In a flow** (`/book:flow`): `docs-health` → `/book:update-docs`; `qa-build` → `/book:check-guides`.
