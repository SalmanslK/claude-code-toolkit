---
name: trim
description: >
  Use when docs feel bloated, repetitive or hard to navigate, or check-book.py warns a document is
  over size: trims, dedupes and restructures, losing nothing load-bearing. Reports before changing; applies only what the person approves. Not for deciding which
  of two disagreeing sources is right (book:check-consistency, book:check-docs). Formerly /docs-trim.
---

*`${CLAUDE_SKILL_DIR}` below is this skill's folder, the one that holds this `SKILL.md` (the base directory shown when the skill loads). If it reaches you unexpanded, write that folder's absolute path in its place; never run a command with the literal text.*

You are gardening this repository's documentation: **minimum sufficient content
that preserves everything needed to understand, build, audit, and correctly
extend the system.** Not maximum documentation, not minimum documentation —
maximum **knowledge density**:

> **useful, correct, actionable knowledge ÷ documentation size**

A shorter document that loses a business rule is a worse document. A long
document with no unnecessary sentence in it is already lean. Judge every change
by density, never by word count alone.

**Your first deliverable is a report, not a commit.**

---

## Which skill is this

This one compares docs against their own purpose and size; the siblings, by
what each compares, are the AI guide's *Which docs skill* (the project's `AI-DEVELOPMENT-GUIDE.md`) table.

**This skill does not settle who is right.** If a finding turns out to be a
contradiction between two docs, or between a doc and the code, hand it to
`book:check-consistency` or `book:check-docs` rather than guessing — gardening removes
overgrowth, it does not adjudicate correctness. If the FSD or
any file under `requirements/` looks stale, that is `/book:check-sources`'s
job, not this one's.

---

## Scope

Everything under `docs/` (per `CLAUDE.md`'s ownership table) plus `CLAUDE.md`
itself and `README.md`. A change to a `CLAUDE.md` file needs an owner's approval
(CLAUDE.md, *Git*) and the guard asks first: propose it in the
report, never apply it as a safe trim. **Not** `requirements/`
(read-only: CLAUDE.md, *Layout*). **Not** `docs/archive/` — historical by
definition; check only that it still reads as superseded, don't compress it.
**Not** application code, and no code changes even if a doc turns out to describe
dead behaviour — that's a `book:update-docs` or `book:check-docs` finding, not a
license to touch `src/`.

Sources of truth, highest first: [`book:check-docs`'s Phase 4](../check-docs/SKILL.md#phase-4--weigh-the-evidence)
— the FSD, dated answers, then approved plans and `docs/architecture.md`, then the code.
Use the order only to judge whether a *doc* statement is still current — never
to rewrite the FSD or the code.

**Pick the documents before reading.** Named documents, or a folder: those.
"The docs" with nothing named: start from `python3 devtools/checks/check-book.py`
— its size warnings and the largest live documents are where density is lost —
and say which documents you took. A whole-set pass is the exception, asked for.

---

## Workflow

### Phase 1 — Discover

Read every in-scope document in full — skimming misses both duplication and the
sentence that justifies keeping something. For each, record its owner topic per
`CLAUDE.md`'s ownership table, and check it against a two-line test: *what is
this document's one job, and would that job survive if this document vanished?*
A document with no clear job, or one already covered by its owner elsewhere, is
itself a finding.

### Phase 2 — Audit

Look for, per document and across the set:

- **Stale**: superseded requirements, implementation detail that no longer
  matches code, completed plans still carrying step-by-step build narrative
  instead of the decisions that outlived it.
- **Duplicate**: the same detailed fact carried in full by two documents — a
  finding under CLAUDE.md's "one topic, one owner". A short contextual summary that
  links to the owner is not one: it is `book:check-consistency`'s D4 (intentional summary),
  `KEEP` ([duplication rules](../check-consistency/references/duplication-rules.md#d4--intentional-summary)).
- **Diary, not knowledge base**: session narrative ("we tried X, then Y"),
  debugging blow-by-blow, or a `TODO` restating a requirement already known —
  keep the decision, drop the journey.
- **Derivable from code**: mechanics a reader gets by opening the file — a
  method signature, a folder listing, an obvious default.
- **Verbose**: a paragraph doing a sentence's job, repeated examples where the
  rule alone suffices, a rule restated three ways for emphasis.
- **Missing**: a current business rule, constraint, or FSD requirement no
  document states — flag it, don't fabricate the fix.

### Phase 3 — Classify

Every finding gets exactly one tag:

| Tag | Meaning |
|---|---|
| `KEEP` | Valuable and current as written |
| `COMPRESS` | Valuable, unnecessarily verbose |
| `MERGE` | Duplicates or overlaps another passage; needs one canonical home |
| `MOVE` | Correct content, wrong document per the ownership table |
| `REMOVE` | Confirmed obsolete, derivable, or diary-only |
| `REVIEW` | Can't confirm obsolete/current from the docs alone |

**`REVIEW` is not a fallback for laziness — it's the honest answer when status
can't be established from the documentation itself.** Route it, don't drop it:
possibly-stale-vs-code → `book:check-docs`; possibly-contradicted-by-another-doc →
`book:check-consistency`; possibly-superseded-requirement → `/book:check-sources`.

Never tag `REMOVE` for any of: business rules, functional requirements, domain
knowledge, constraints, architectural decisions and their rationale, security or
data-integrity rules, integration or compatibility contracts, migration
requirements, non-obvious behaviour, known edge cases, or FSD interpretation
needed to implement correctly — even when long, even when it looks like it could
be inferred later. If in doubt whether a passage is one of these, it's `REVIEW`,
not `REMOVE`. [*What must survive*](../update-docs/SKILL.md#what-must-survive-no-matter-how-little-code-supports-it)
(open questions, requirements history, `[PROPOSED]`/`[DEFERRED]` markers, the
`docs/archive/` record, trade-offs, warnings) is binding here.

### Phase 4 — Optimize (only after the person approves the report)

**Where the edits go.** A trim is a general refresh, never on a feature branch
(docs/CLAUDE.md, *Which branch a doc change goes on*): check `git branch --show-current` before
the first edit; on the wrong branch, stop and offer to cut one.

Apply what the *Apply directly* column below covers; everything in *Ask first* waits
for the person's answer. For each:

- **Compress** by cutting words, never by cutting the claim. A compressed rule
  still names its exception; a compressed rationale still says *why*.
  Prefer a table or list over prose when the content is enumerable.
  Reduce repeated examples to the one that earns its place; the rule can stand
  without a worked example if it's already unambiguous.
- **Merge** into whichever side already owns the topic per `CLAUDE.md`'s
  ownership table (or, absent a ruling there, whichever is more complete); leave
  a reference in the other, don't leave two full copies.
  Deleting the losing side outright when it also carried nuance the winner
  lacks is a `book:check-consistency` job (reconciling *content*, not just removing
  the duplicate) — flag it there instead of quietly dropping the nuance.
- **Move** to the correct owner; leave a link behind, not a stub copy.
- **Remove** only what Phase 3 confirmed obsolete/derivable/diary — delete
  outright, don't comment out, but see "Do not delete" below for history that
  must be demoted instead of deleted.
- **Never create a new markdown file** — the only routine new files are the ones
  `docs/CLAUDE.md`, *New files* lists, and a trim
  creates none of them.

**Do not delete history — demote it**, to the archive file
`docs/CLAUDE.md`'s table names, leaving
the id or heading behind. History *presented as current guidance* must go; history
labelled as history is the point, not a violation of "remove what's dead".

**Ask before, don't ask after:**

| Apply directly | Ask first |
|---|---|
| Compressing verbose prose without cutting a claim | Removing a full section, even if it looks diary-only |
| Fixing a broken/misdirected internal link | Merging or splitting documents |
| An exact duplicate paragraph with an obvious canonical home | Anything touching `requirements/` interpretation |
| Moving a passage to its stated owner, leaving a link | A `REVIEW` item — route it, don't resolve it yourself |

### Phase 5 — Validate

After applying changes (a trim keeps every claim — it does not re-check claims
against the FSD or the code; that is `book:check-docs`):

1. **Run the tools, both must pass.**
   `python3 "${CLAUDE_SKILL_DIR}/../sync-sources/scripts/heading_guard.py" --claims` —
   every heading, id, link target and number the changed files held before still
   there, moves between changed files included — and
   `python3 devtools/checks/check-book.py` (links, anchors, owners, history). Each
   `LOST` line is either an approved `REMOVE`/`MOVE` you name in the report, or put back.
2. **Re-read only the passages whose claim changed** — reworded rather than cut,
   merged, or a `REMOVE` — against the text they replaced: the tools see the same ids
   and numbers in a sentence whose meaning moved. A pure compression the tools pass
   needs no re-read.
3. Confirm no contradiction with an untouched sibling document, and that nothing on
   the "must survive" list (Phase 3) got compressed into silence.

Docs-only edits need no build or test run.

### Phase 6 — Report

1. **Documents reviewed**, and **documents modified**.
2. **What changed**, grouped by tag (`COMPRESS`/`MERGE`/`MOVE`/`REMOVE`), one
   line each with before → after where it's not obvious.
3. **Important knowledge preserved** — the close calls: content that looked
   removable but was kept, and why.
4. **`REVIEW` items**, each routed to the skill that owns resolving it.
5. **Approximate size reduction**, only where genuinely measurable (word count
   or line count per file); don't manufacture a number for its own sake.

---

## Rules that hold in every mode

**Density over brevity.** The target is knowledge-per-token, not a smaller file.
Do not compress a passage below the point where a future reader would have to
re-derive the reason behind a decision.

**Never silently delete uncertain content.** `REVIEW`, then route it — silence
here is indistinguishable from an unreviewed loss six months later.

**Never rewrite a source-of-truth document to make the docs smaller** (see *Scope*).

**One finding, one tag.** Don't apply `REMOVE` to something you've also flagged
`REVIEW` — resolve the ambiguity by routing it, not by picking the more
convenient tag.

---

## Modes

| Invocation | Does |
|---|---|
| `/book:trim` or `/book:trim audit` | Phases 1–3 and the report. Changes nothing; ends by asking what to apply |
| `/book:trim optimize` | Phases 1–6: applies the *Apply directly* column on a `chore/docs-<slug>` branch, asks before the rest. Asking for `optimize` is the approval Phase 4 needs |

Drift against the FSD or the code is not a trim: route it to `/book:check-docs`.

---

## The rule that matters most

**A garden that has been weeded down to nothing is not tended, it's gone.**
Every `REMOVE` is a bet that the knowledge is truly derivable or truly dead.
Bet wrong and the next person to need it has no way to know it ever existed —
that's why `REVIEW` exists, and why it's never a shortcut to skip.

---

## What next

- `REVIEW` items routed to `/book:check-docs`, `/book:check-consistency` or `/book:check-sources` —
  run those next.
- Edits made: commit them on the `chore/docs-<slug>` branch; its pull request opens only
  when the person asks (CLAUDE.md, *Git*).
- **In a flow** (`/book:flow`): `docs-health` → `/book:check-guides`.
