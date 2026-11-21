# Pass A — Conformance — Requirements & Business Logic (checks 1–15)

Part of the review checklist; its method is [`review-method.md`](review-method.md).

**Runs first, on every review, however small the diff.** It asks whether the
code does what was decided; [Pass B](review-method.md#pass-b--correctness--dimensions-212-checks-16160)
asks whether what is there is right. It covers dimension 1 of the framework
in full.

**Only this pass can find an omission.** Reading a diff cannot reveal the
requirement nobody implemented — there is nothing to read. A review that
skips this passes half-built features and calls them sound, and the gap then
arrives in UAT as a defect against a specification we signed up to. That is
the most expensive way for a review to fail, and the only one the author
cannot catch by re-reading their own diff.

### A1 · Requirements to code — checks 1, 3, 4, 9

**Contradiction and omission are different failures, and only the first is
easy to see.** [A2](#a2--code-to-our-docs--check-4-part-15) catches "the doc
says X, the code does Y." It cannot catch "the FSD specifies X and nothing in
the diff does anything at all" — silence produces no mismatch. **That gap is
how a specified requirement ships as missing without a single reviewer
noticing.**

So for every feature the diff touches, go the other way — from the
requirement to the code, not from the code to the requirement:

1. **Read the FSD section the feature claims**, from the highest `V<n>.pdf` in
   `requirements/fsd/` — that section's pages only (`factory fsd-page "<heading>" --print`), by
   [Reading the FSD](../../fact-check/references/reading-the-fsd.md). Extract
   it rather than trusting a summary of it. **Unreadable: stop and tell the
   person** — this pass is never skipped, and a review without it is not a READY.
2. **List what it specifies.** Fields, validation, defaults, messages,
   required behaviours, required state transitions (*check 9*).
3. **Find each one in the diff.** What is absent is *check 1* (requirement
   not implemented) or *check 3* (required business rule missing).
4. **Check the global sections too** — §2.2 binds every module, so a feature
   PR can satisfy its own section perfectly and still miss a rule that
   applies to it.
5. **Cross-check the two documents that already track this**:
   [`docs/qa-artifact-test-suite.md`](docs/qa-artifact-test-suite.md)
   for what QA will fail us on, and
   `docs/api/fe-api-coverage.md`
   for endpoints the front end requires.

**A documented deferral is not a defect.** Each feature plan carries a
*"Deliberately not built"* table, and something listed there with a stated
landing place is a decision (*check 4 handled correctly*), not an omission —
do not report it.

**But check that the landing place exists.** A deferral pointing at "its own
plan" or "a later phase" when no such plan and no such phase entry exists
means nobody owns it, and it will be discovered as a defect by QA instead
(*incorrect assumption about the requirement — check 4*). **That is a
finding** — see [Conformance findings specifically](review-method.md#conformance-findings-specifically).

### A2 · Code to our docs — check 4 (part), 15

Find the doc that owns the affected topic — the owners are tabled in
[`CLAUDE.md`](CLAUDE.md#where-knowledge-lives) — and compare.

**Neither side is presumed right.** Where code and documentation disagree,
work out which represents the intended design; where the FSD is one of the
sides, the FSD wins and the code is the finding (*business logic inconsistent
with existing system behaviour — check 15*). Flag a contradiction you cannot
settle rather than quietly picking one. Report it once, not per file.

A guide in `docs/fe-integration-guides/` must be updated in the **same**
change as the API it describes.

### A3 · The change to the docs it invalidated

CLAUDE.md: *"If you change behaviour, fix the doc that owns it in the same
commit."* A PR that alters behaviour and leaves its documentation behind has
an unfinished change in it, not a follow-up ticket.

Check the three that go stale fastest:

- **`docs/fe-integration-guides/<module>.md`** — written from shipped code and
  **trusted by another team**. A guide that now lies is worse than none, and
  it is a finding on the PR that made it lie.
- **The feature's plan in `docs/plans/`** — *"If the implementation departs
  from the plan, update the plan in the same commit."* Including its
  *Deliberately not built* table, where a scope change should show up.
- **`docs/api/fe-api-coverage.md`** — a new or renamed endpoint needs its row.

**Record the conformance verdict per FSD section, including the sections that
pass.** It goes in the terminal review, not on the PR. A satisfied
requirement leaves no comment behind, so without the table a reader cannot
tell a section that was checked and found clean from one nobody opened.

```markdown
### Requirements conformance

| FSD | Requirement | Status |
|---|---|---|
| §2.4.1–2 | Date and time formats, options and defaults | ✅ complete |
| §2.4.3 | Preferences screen behaviour | — front end |
| §2.2.6 | Page size saved per user per screen | ❌ **not built** — see below |
| §2.2.8 | Added/Updated By and Date on every record | ✅ complete |
```

**A green row is worth as much as a red one.** "§2.4 checked, complete" tells the
next reader the section was examined; silence tells them nothing.

### A4 · Business rule correctness — checks 2, 5–14

Beyond "is it there", is the rule **right**? This is where most of dimension
1's remaining checks live, and it needs the code read, not just the FSD.

| # | Check | Apply it here |
|---|---|---|
| 2 | Business rule implemented incorrectly | Compare the code's actual condition against the FSD sentence word for word — an off-by-one on a comparison operator or an inverted boolean reads fine at a glance |
| 5 | Incorrect default behaviour | What happens when the caller supplies nothing? Compare against the FSD's stated default, not what seems reasonable |
| 6 | Incorrect edge-case behaviour | Empty collections, zero, boundary dates, the last item in a page, the first record for a new tenant |
| 7 | Invalid state allowed | Can the aggregate be constructed or saved in a state the domain forbids? `ISoftDeletable` — deleted is invisible, inactive is visible and labelled; several aggregates carry both and conflating them is this check |
| 8 | Invalid state transition allowed | Can a status move somewhere the domain doesn't permit — an entity re-entering a terminal state, a business-unit-scoped record changing unit when the FSD forbids it |
| 9 | Required state transition missing | A workflow step the FSD requires that nothing in the diff triggers |
| 10 | Incorrect operation ordering | File write / row save / old-file delete must run in that order for uploads — a filesystem does not roll back; two `SaveChangesAsync` calls in the wrong order can commit a user with no invitation |
| 11 | Duplicate business operation | Can the same request, retried or double-submitted, create two of something meant to be one? |
| 12 | Missing idempotency | `IUnitOfWork.ExecuteInTransactionAsync`'s block **may run more than once** under retry-on-failure — is everything inside it safe to repeat? |
| 13 | Incorrect idempotency | An idempotency guard that only checks part of the key, or that a resubmission with the same *changed* value can defeat |
| 14 | Incorrect handling of partial/failed operations | A failed external call (email, storage) after the local write already committed — is the inconsistency acceptable and intentional (`UserEmailNotifier` logs-and-swallows by design), or does new code do the same thing without that being a decision? |

**A reference check has two questions, and only one applies to resubmitted
data**: "does this row exist" and "may it be chosen *now*." Checking only the
first on a value the record already had is *check 4* (incorrect assumption)
— a mistake that recurs.
