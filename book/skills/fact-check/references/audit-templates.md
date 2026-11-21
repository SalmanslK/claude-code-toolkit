# Audit file templates

Three files under `docs/Audit/`. Each has one job; nothing is restated between
them — the matrix carries evidence, the report carries the narrative, the
findings file carries the actions. Cross-reference by ID.

---

## `docs/Audit/spec-traceability.md`

```markdown
# Spec traceability — FSD → Plan → Code → Test

**FSD:** V<n> (`requirements/fsd/… - V<n>.pdf`) · **Audited commit:** `<branch>@<sha>` ·
**Last full pass:** <date> · **Scope so far:** <modules audited; "whole project" when complete>

Statuses: VERIFIED · PARTIAL · MISSING · CONTRADICTED · UNTRACED · UNVERIFIED · NOT_APPLICABLE
(definitions in the book:fact-check skill's `SKILL.md`). IDs are stable — never renumbered, never reused.

## <Module> — FSD §<section> — plan `docs/plans/<feature>.md`

| ID | FSD ref | Requirement | Plan ref | Code evidence | Test evidence | Status |
|---|---|---|---|---|---|---|
| FSD-2.5.1-R01 | §5.1.1 | Total record count shown on Pending | §1, §6 | `…/WidgetReadRepository.cs:98` | `CompanyListTests.Listing_pending_…` | VERIFIED (observed) |
| FSD-2.5.1-R08 | §5.1.8 | Pending list not paginated (BA, 2026-01-14) | §2 Q8 | `…/ListPendingWidgetsQuery.cs:12` — paged | — | CONTRADICTED (observed) → D1 |
| FSD-2.5.1-R07 | §5.1.7 | Frozen Action column on horizontal scroll | — | — | — | NOT_APPLICABLE — FE rendering |

### Untraced behaviour in this module

| ID | Code evidence | What it does | Nearest justification found | Status |
|---|---|---|---|---|
| UNT-COM-001 | `…/ReorderPendingCompaniesCommand.cs:41` | Refuses a partial id set on reorder | plan §10 | UNTRACED — plan decision, no FSD line |
```

Rules for the matrix:

- **One row per atomic requirement.** Split a paragraph into its checkable
  statements; a row that says "list works as specified" cannot be verified.
- **`Code evidence` is `path:line`**, never a folder. **`Test evidence` is
  `Class.Method`.** `—` means none was found, which is itself the finding.
- **Global sections (§2.2 …)** get one block at the top of the file, one row
  per rule, whose evidence is the **shared mechanism** and its test. Module
  blocks cite the global ID in prose and add a row **only** where the module
  bypasses the mechanism — that row's ID is the module's own
  (`FSD-2.2.6-R02` in the global block; `FSD-2.5.1-R23` for Companies'
  unpaged Pending list, which cites it).
- **`VERIFIED` / `CONTRADICTED` carry `(observed)` or `(traced)`** — see the
  skill's status vocabulary.
- **A status change keeps the history inline**: `CONTRADICTED (traced) →
  VERIFIED (observed, 2026-01-20, PR #96)`.
- **Untraced behaviour** is a separate table per module with `UNT-<MOD>-<nnn>`
  ids — it has no FSD reference to key on.

---

## `docs/Audit/spec-compliance-audit.md`

```markdown
# Spec compliance audit

**Audit date:** <date> · **FSD:** V<n> (captured <date>, `docs/project.md` Part 3) ·
**Plan(s):** `<file>` (status, last changed <date>) · **Audited commit:** `<branch>@<sha>` ·
**Scope:** <module(s) | whole project> · **Previous audit:** <date or "none">

## Coverage

| Module | Rows | VERIFIED | PARTIAL | MISSING | CONTRADICTED | UNTRACED | UNVERIFIED | N/A |
|---|---|---|---|---|---|---|---|---|

Counts only — no percentage, no score.

## FSD → Plan
What the plan omits, waters down, or reinterprets. One line per item, ID-linked.

## Plan → Code
Planned and not built, partial, differs from plan, claimed without evidence.

## Code → FSD
Contradictions, and every UNTRACED behaviour with what would justify it.

## Tests
Requirements with no meaningful test evidence, by ID.

## Existing defects touched
`D<nn>` rows this audit relies on or corroborates — reference only.

## Required follow-up
Ordered list, each pointing at an `SA-<nnn>` finding, a `D<nn>`, or a
`open-questions.md` question to raise.

## Final gate
- FSD → Plan: …
- Plan → Code: …
- Code → FSD: …
- Tests: …
- Not declared compliant because: <the rows that prevent it>

## History
| Date | Scope | Commit | Outcome |
|---|---|---|---|
```

---

## `docs/Audit/spec-audit-findings.md`

```markdown
# Spec audit findings

Actionable items only. Compliance findings, not defects — a finding that
turns out to be a defect is logged in `docs/defects.md` by whoever owns the
fix and referenced here by `D<nn>`; this file never adds a `D` row itself.

Severity: HIGH — FSD behaviour missing or contradicted on a shipped path ·
MEDIUM — partial, or reinterpreted without a recorded decision ·
LOW — untested, or traceability gap only.

## Open

### SA-001 · HIGH · CONTRADICTED (observed) · Pending list is paginated
- **FSD:** §5.1.8 + BA comment 2026-01-14 (Q8)
- **Plan:** `companies-and-locations.md` §2 (stated default while Q8 was open)
- **Code:** `…/ListPendingWidgetsQuery.cs:12` (`IPagedQuery`)
- **Test:** `CompanyListTests.Listing_pending_and_completed_costs_a_fixed_number_of_queries` asserts the paged shape
- **Expected:** whole list in one response
- **Actual:** §2.2.6 page, max 100 rows
- **Action:** already D1 — verify on merge of the fix, then flip R08
- **Status:** Open · found <date>

## Resolved

### SA-000 · … · Resolved <date> — <how, with commit or PR>
```

Rules for findings:

- **One finding per root cause.** Five requirements failing for the same
  reason are one `SA` with five IDs listed, not five findings.
- **A finding cites the matrix row(s)**; it does not repeat the evidence
  columns.
- **Resolved is a state, not a deletion.** Move the entry, add the date and
  the commit or PR that resolved it.
- **Questions are not findings.** An FSD ambiguity becomes an
  `open-questions.md` question; the finding that exposed it is `UNVERIFIED` until the
  answer lands, and says which question it waits on.
