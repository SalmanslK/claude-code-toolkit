---
name: fact-check
allowed-tools: Read, Grep, Glob, Edit(docs/Audit/**), Write(docs/Audit/**), Bash(git log*), Bash(git show*), Bash(git diff*), Bash(git grep*), Bash(git ls-files*), Bash(git rev-parse*), Bash(git fetch*), Bash(pdftotext *), Bash(ls *), Bash(python3 devtools/book.py fsd-page*), Bash(python devtools/book.py fsd-page*), Bash(diff *)
description: >
  Use when asked whether the code matches the FSD, whether a plan captured everything it requires, or to
  build the traceability matrix under docs/Audit/ — before a release, after a module is Built. One
  module or the whole project. Not for a branch review (book:self-review) or docs against code
  (book:check-docs). Formerly /fsd-audit.
---

You are auditing whether **the FSD, the plan and the code say the same thing**,
and whether that can be *shown* — requirement by requirement, with a file and
a line on every claim. This is a **compliance and traceability audit**, not a
code review: quality, performance, style and security are someone else's
skill unless they change what the FSD asked for.

**The FSD is immutable here. It wins every conflict, and this skill never edits
it.** Everything this skill writes goes under **`docs/Audit/`** and nowhere else.

**Evidence or UNVERIFIED.** Never "implemented", "covered" or "compliant" from a
related feature existing, a plan saying so, or a comment claiming it.

**An unreadable FSD section means no audit of that module.** If a module's
section cannot be read — no PDF, an extraction refused or garbled past citing —
write no rows for that module, finish the modules that could be read, and open
the report with which module was not audited and why. No PDF at all: stop before
anything is written and tell the person. One unreadable requirement in an
otherwise readable section is `UNVERIFIED` with the reason.

*The Book's command is `book`: `python devtools/book.py <command>` from the project's root.*

---

## Inputs, and where they are

| | Where | Read it how |
|---|---|---|
| **FSD** | `requirements/fsd/… - V<n>.pdf` — **highest `n` numerically** | `book fsd-page "<heading>"` locates the section's pages ([`references/reading-the-fsd.md`](references/reading-the-fsd.md)); print only those. Quote section numbers **and** heading text |
| **Plan(s)** | `docs/plans/<feature>.md`; find them through `docs/project.md` Part 1 (Feature → FSD § → Plan → Status) | §1 *What the FSD says*, §8 open questions, the *Why* lines in the design sections, and the *Deliberately not built* table are the load-bearing parts; build history is in `docs/archive/plans-history.md` |
| **Answered questions** | `docs/open-questions.md` — a dated BA answer outranks any plan text written before it | *Resolved* holds one line per answered question, by topic — the rule in force; the full record is `docs/archive/questions-resolved.md`. `project.md` Part 3 (latest) and `docs/archive/requirements-history.md` (earlier) for what moved between FSD revisions |
| **Code** | `src/…/Domain/Features/`, `Application/Features/<Feature>/` (commands, queries, validators, `<Feature>Errors`), `Application/Abstractions/`, `API/Endpoints/`, `Persistence/` (configurations, repositories, migrations) | Trace the path: endpoint → handler → domain → repository → schema |
| **Tests** | `tests/UnitTests` (domain rules), `ArchitectureTests` (guardrails), `IntegrationTests` (real database) | Test names are sentences; a test is evidence only if it exercises the behaviour named in the requirement |
| **Existing audit** | `docs/Audit/` — the three files below, if present | Update, never recreate |
| **Adjacent owners** | `docs/defects.md`, `docs/qa-artifact-test-suite.md`, `docs/api/fe-api-coverage.md`, `docs/open-questions.md` | **Reference by id; never restate or re-log** |

**Where the writes go.** A standalone audit is a general refresh
(docs/CLAUDE.md, *Which branch a doc change goes on*) — check the branch before the first write.

**Audit a commit, not a working tree.** Record it as `origin/dev@<sha>`
(`git rev-parse --short origin/dev`) unless told to audit another branch, and
if the checkout you are reading from is on a different branch, say so and
confirm it holds the same commit. A local checkout on someone else's feature
branch is not `dev`.

---

## Scope

Given a module: its FSD section(s) from Part 1, its plan, its feature folder,
its tests. Given the whole project: every row in Part 1 whose status is Built,
one module at a time, same method. **State the boundary in the matrix header**
— which sections are in, which adjacent ones were left out and why.

**Read only what the scope names.** The module's sections of the FSD, its plan,
its feature folders and the tests whose names cite it — not the whole FSD, not
sibling modules. Reach outside only to follow a call the trace leads to, or a
global section (below). An existing row in `spec-traceability.md` whose code
and test still exist at the audited commit is re-checked at those lines, not
re-derived.

**Three or more modules:** audit each in its own read-only agent, in parallel —
each gets this skill, its module's scope and the audited commit, writes
nothing, and returns its rows and findings in the
[templates'](references/audit-templates.md) shape. This session audits the
global sections itself, then is the **only writer** to `docs/Audit/`: it
merges the rows, keeps IDs stable, and resolves any two agents that disagree
about a shared mechanism. One or two modules: audit them here.

**Global sections (§2.2 and its siblings) bind every module** — a module can
satisfy its own section and miss a rule that applies to all of them. They are
audited **once, in their own block**, against the shared mechanism that
implements them — `PagedListQueryHandlerBase`, `SearchTerm`, the auditing
interceptor, an architecture test — and a proof of the shared mechanism
counts for every module that goes through it. A module's block then cites
the global ID, and adds a row of its own only where the module **bypasses or
deviates from** the shared mechanism (a hand-written handler that trims its
own search, a list that opts out of paging).

**FE-only requirements** (navigation, toasts, frozen columns, blank-state
headings) are `NOT_APPLICABLE` **with the reason stated** — and the backend's
half, if any (the data the screen needs), still gets its own row.

---

## Requirement extraction and IDs

One row per **atomic, checkable statement** in the FSD: a field, a validation,
a default, a message, a state transition, an authorization rule, a list
column, a sort, a filter. Not one row per paragraph.

**ID scheme:** `FSD-<section>-R<nn>` — `FSD-2.13.6-R08`. Stable for life:
never renumber, never reuse; a requirement that vanishes from the FSD keeps
its row with status and the revision that removed it. Plan items are cited by
section (`plan §4`, `plan §6`); code by `path:line`; tests by class and
method name. IDs live in `docs/Audit/` only — the FSD is never edited to
carry them.

---

## The three passes

Run all three. Each finds what the others cannot.

**1 · FSD → Plan.** For every requirement: is it in the plan, where, and does
the plan's wording *change* it? Flag missing, partial, contradicted, and
interpretations that alter behaviour ("we read X as Y"). A plan's *Deliberately
not built* entry with a real landing place is a decision, not a gap; one whose
landing place does not exist is a finding.

**2 · Plan → Code.** For every plan item: the handler, entity, validator,
endpoint, migration or repository that implements it, and the test that
proves it. Flag planned-not-built, partial, differs-from-plan, and "plan says
shipped, no evidence".

**3 · Code → FSD.** Read the feature's code cold and ask *what does this
actually do?* — validators, error messages, state guards, query filters,
permissions, defaults. Every behaviour either traces to an FSD requirement, an
answered question, or a plan decision — or it is **`UNTRACED`**. Useful is not
the same as specified.

**Evidence order when sources disagree** is `book:check-docs`'s Phase 4: FSD,
then dated answers in `open-questions.md`, then the plan's design, then integration and
architecture tests, then code, then schema, then unit tests, then comments.
Say which two disagreed; never quietly pick.

---

## Status vocabulary

| Status | Means | Needs |
|---|---|---|
| `VERIFIED` | Behaviour is in code **and** a test exercises it | code `path:line` + a named test |
| `PARTIAL` | Part of it, or all of it without test evidence | say which half is missing |
| `MISSING` | No implementation and no documented deferral | — |
| `CONTRADICTED` | Code does something different | FSD quote + code line |
| `UNTRACED` | Behaviour with no FSD, answer or plan decision behind it | code line; needs a human |
| `UNVERIFIED` | Could not be determined from what is available | say what would settle it |
| `NOT_APPLICABLE` | Not this repository's to implement | the reason |

**Code existing is not `VERIFIED`.** An endpoint, a DTO field or a validator
rule with no test naming the behaviour is `PARTIAL` with `Test: none`.

**`VERIFIED` and `CONTRADICTED` say how they were established:** `(observed)`
when a test or a run showed the behaviour, `(traced)` when it was derived by
reading the code path. A traced contradiction is a real finding, and the
first action on it is a test that observes it.

---

## Outputs — `docs/Audit/`, and only there

Three files, templates in [`references/audit-templates.md`](references/audit-templates.md):

- **`spec-traceability.md`** — the matrix, one row per ID.
- **`spec-compliance-audit.md`** — the report: date, FSD version, plan dates,
  commit audited, scope, then findings by pass. **No score, rating or
  percentage** — a number hides the row that failed.
- **`spec-audit-findings.md`** — one entry per actionable finding, `SA-<nnn>`,
  with its own lifecycle (`Open` → `Resolved <date>` / `Superseded`).

**Updating an existing audit:** keep the IDs, keep history, flip statuses
with a date, mark resolved findings resolved. Nothing obsolete stays presented
as current; nothing current is deleted to make room.

**Boundaries.** A defect already in `docs/defects.md` is cited as `D<nn>`,
not re-described. A compliance gap that is *not yet* a defect is a finding
here — do not add it to `defects.md` from this skill; say in the finding that
it is a candidate. A QA case is `qa-artifact-test-suite.md`'s, an FE endpoint
is `fe-api-coverage.md`'s, an ambiguity in the FSD is a **question for
`open-questions.md`** — the finding names it and stops; it does not invent
the answer.

---

## Final gate

Close every audit with, explicitly: FSD → Plan (all represented? any
reinterpreted?), Plan → Code (all built? what is missing?), Code → FSD
(conforming? what is untraced?), Tests (which requirements have no meaningful
test evidence?), and the counts per status. **Never write "fully compliant"
while any material row is `MISSING`, `CONTRADICTED`, `UNTRACED` or
`UNVERIFIED`.**

---

## Red flags — stop and re-read the rule

| The thought | What it actually is |
|---|---|
| "Built, just untested" | `PARTIAL`. Untested is unverified |
| "Harmless in practice" | The FSD said something else. `CONTRADICTED` |
| "That reading is defensible" | A reinterpretation. Flag it; the BA decides |
| "Benign, documented in the plan" | Documented where, against which FSD line? If nowhere: `UNTRACED` |
| "The plan's reading of the FSD numbering" | The plan is under audit. Cite the PDF page and heading |
| "A related feature covers it" | Which requirement, which line, which test? |
| "FE-only" with no reason | `NOT_APPLICABLE` carries its reason or it is `UNVERIFIED` |
| "Close enough" | `CONTRADICTED` beats close enough. `MISSING` beats implied |
| "I'll audit the checkout I'm on" | Name the commit of `dev` |

---

## What next

- **`MISSING` or `CONTRADICTED` in a completed module:** a `docs/defects.md` row each, today
  (CLAUDE.md, Features).
- **A requirement the FSD leaves open:** a question in `docs/open-questions.md` with a recommendation,
  never a guess in the plan.
- **`UNVERIFIED`:** name what could not be checked, and run the audit again once it can be.
- **The matrix changed:** it lands through a pull request, like any other doc.
- **In a flow** (`/book:flow`): `new-fsd-revision` → `/book:check-guides`; `finish-feature` → `/book:check-guides`; `spec-says-x` → `/book:raise`; `qa-build` → `/book:check-permissions`.
