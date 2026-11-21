---
name: check-consistency
description: >
  Use when documents may disagree with each other: a rename, heavy doc edits, or a docs branch before its PR. Finds duplication, contradictions, terminology drift and missing links between docs, and
  reports before changing anything. Not for docs against code
  (book:check-docs) or bloat (book:trim). Formerly /docs-consistency.
allowed-tools: Read, Grep, Glob, Bash(git diff*), Bash(git log*), Bash(git ls-files*), Bash(git grep*), Bash(python3 devtools/checks/check-book.py*), Bash(python devtools/checks/check-book.py*)
---

You are making a project's documentation **work as one system**.

Every document has a job. Concepts have one home and are referenced from
everywhere else. Nothing contradicts anything. That is the whole skill:

> **ONE CONCEPT → ONE CANONICAL HOME → MANY REFERENCES → MINIMAL DUPLICATION → ZERO CONTRADICTIONS**

**Your first deliverable is a report, not a commit.**

---

## The boundary that defines this skill

You compare **documentation against documentation**. You do not open the code to
decide which document is right. (The sibling skills, by what each compares, are
the AI guide's [*Which docs skill*](AI-DEVELOPMENT-GUIDE.md#which-docs-skill) table.)

This matters because the two questions have different answers. Two documents can
agree perfectly and both be wrong about the system — that is not yours. Two
documents can disagree while one of them matches the code exactly — you can see
the disagreement but **not** which one is correct.

**When a contradiction cannot be settled from the documentation alone, report it
as `Requires Code/Documentation Reconciliation` and stop.** Do not open a source
file to break the tie, and never assume the newer document, the longer one, or the
one you read first is the right one. Guessing here is worse than reporting,
because a confident wrong resolution removes the evidence that anything was ever
in doubt.

---

## Scope — decide it before reading anything

| Asked about | Scope | Read |
|---|---|---|
| Named documents, a concept, or a renamed term | **Scoped** | Those documents; the owner of each topic they touch; `git grep -n` for the concept or term across `docs/` and the root docs, and the passages it hits |
| A change — a branch, a run, "after these edits" | **Scoped** | `git diff --name-only <base> -- docs/ '*.md'`, the changed sections, and the owner of each topic they touch |
| "The whole docs", before a release, a periodic pass | **Full** | Everything below, in full |

Say which scope you chose in the report's first line. A scoped pass that finds a
contradiction reaching beyond its documents names the other side and stops there —
it does not widen itself into a full pass.

**Start from what is already decided and already checked:**

- **CLAUDE.md's [Where knowledge lives](CLAUDE.md#where-knowledge-lives)
  table is the canonical map.** Phase 3 reads ownership from it; it does not
  rebuild it. A document violating it is a finding; a concept it does not place is
  where Phase 3's judgement is needed.
- **Run `python3 devtools/checks/check-book.py` first.** Broken links and anchors,
  ownerless documents and history in live documents are its findings — cite them,
  do not re-derive them by reading.

The full scope is everything under `docs/`: `.md`, `.mdx`, documentation text
files, ADRs, API docs, setup guides, feature and domain docs, technical notes, and
the **diagrams embedded in them** — Mermaid, ERDs, sequence, architecture and
workflow diagrams all make claims and can contradict prose. Generated documents
(`docs/api/api-contracts.md`, `docs/database-erd.md`) are compared, never
harmonized: they change only by regenerating.

Also read, but do not treat as yours to reorganise:

- **Root-level docs** (`README.md`, `CONTRIBUTING.md` where one exists, a repo-level agent or rules
  file). They routinely duplicate `docs/` content, so they are in scope for
  *findings*. Edit them only when the project's own rules place them in your care.
- **Requirement and client source material** (specifications, contracts, exported
  designs). **Read-only.** These are evidence for settling a contradiction, often
  the deciding evidence — but a finding is never raised *against* them.
- **Archived or superseded material.** Not stale by definition. Check only that it
  is still clearly marked as superseded, and that nothing current links to it as
  though it were live.

---

## Workflow

Phases 1–3 build the map. Phases 4–7 use it. Do not start editing during any of
them.

### Phase 1 — Inventory

Read every document in scope. **Read them fully** — duplication and contradiction
both hide in the middle of long files, and a skim finds neither. In a scoped pass,
"in scope" is the scope table's *Read* column; the owner of a topic is read at the
section that owns it.

Record: path, its apparent purpose, main topics, documents it links to, documents
it appears to overlap, and concepts it looks authoritative about.

### Phase 2 — Responsibility mapping

Give every document a one-line statement of its job. Then flag the ones where you
could not: unclear responsibility, several unrelated responsibilities, heavy
overlap with a sibling, or no obvious place in the hierarchy.

**A document whose responsibility you cannot state in one line is itself a
finding.** That is usually where duplication has been accumulating.

### Phase 3 — Canonical knowledge map

For each significant concept, name the document that owns the authoritative
explanation, and list every other place it appears.

A concept may be summarised anywhere. Only one document should carry the detailed
authoritative version. Where two documents both look authoritative, that is a **C4
scope conflict** — see `references/canonical-ownership.md` for how to choose, and
for when the answer is to split the concept rather than pick a winner.

### Phase 4 — Duplication analysis

Classify every repeat as D1–D4 and decide whether it is harmful. **D4, intentional
contextual summary, is correct and stays.** Full rules and worked examples:
`references/duplication-rules.md`.

### Phase 5 — Contradiction analysis

Classify every conflict as C1–C5. C5 — ambiguous, insufficient evidence — is never
resolved by you. Full rules: `references/contradiction-rules.md`.

### Phase 6 — Terminology harmonization

Build the preferred-term list, the deprecated synonyms, and the acronyms, starting
from the glossary: [`system-overview.md` §3 *Vocabulary*](docs/system-overview.md#vocabulary).
**Count each variant, don't hunt for it by reading:**
`git grep -c -i -w "<variant>" -- docs README.md AI-DEVELOPMENT-GUIDE.md ":!docs/archive" ":!docs/Audit"`
gives the files and the number of uses per file; open only the hits (`git grep -n`). Which
variant is right, and whether two words are one concept, stays your judgement.
**Different words for genuinely different concepts are not a conflict** — check
before you normalise. Full rules: `references/terminology-guidelines.md`.

### Phase 7 — Cross-reference analysis

Find concepts mentioned without a link to their canonical home, places a reader
would be stuck, duplicated detail replaceable by a reference, and broken or
misdirected internal links.

**Prefer few meaningful links to many.** A document where every third noun is a
link is harder to read, not easier. Do not add a link merely because you can.

---

## Modes

Default to **Audit** unless the invocation says otherwise.

| Mode | Does | Ends with |
|---|---|---|
| **Audit** | Phases 1–7. Changes nothing. | The report |
| **Review** | Audit, plus sorting every finding into *safe*, *recommended*, or *needs a decision*. Changes nothing — applying any of it is Harmonize | The report, and a decision list |
| **Harmonize** | Applies what is approved or unambiguously safe | A list of what changed, and what was left |

Use `templates/harmonization-report.md` for the report's shape.

**Where the edits go:** [docs/CLAUDE.md, *Which branch a doc change goes on*](docs/CLAUDE.md#which-branch-a-doc-change-goes-on). Check
`git branch --show-current` before the first edit; on the wrong branch, stop and offer to cut one.

In **Harmonize**, before any structural change — merging, splitting, moving,
renaming, deleting, or moving canonical ownership — state which files are
affected and how ownership changes, **and get approval**. Safe changes may be
applied and listed as done.

| Apply freely | Ask first |
|---|---|
| Broken or misdirected internal links | Deleting a document |
| Exact duplicate paragraphs, where a canonical home is already clear | Merging or splitting documents |
| A cross-reference typo | Moving canonical ownership |
| An established term used inconsistently | Resolving an ambiguous contradiction |
| A missing link to an explicitly canonical document | Rewriting business or architectural content |

---

## Rules that hold in every mode

**Reducing duplication is not the goal; coherence is.** A reader who has to open
three documents to understand one thing is worse off than one who read a sentence
twice. Cutting a helpful summary down to a bare link is a regression, and it is
the most common way this work goes wrong.

**Never resolve a contradiction by deleting one side.** Determine which is
canonical and correct the other, or flag it. Deleting the losing side destroys the
evidence that the disagreement existed.

**Do not delete history — demote it.** Mark it superseded, or move it to wherever
the project keeps its record of past decisions. What must not survive is history
presented as current guidance.

**Respect the project's own conventions.** If it forbids new markdown files, do
not propose one without saying why the existing owners cannot hold the content. If
it names document owners, follow them.

---

## Final validation

After harmonizing, confirm and **report the numbers rather than asserting
success**:

- Every document has a stated purpose; related documents complement rather than
  compete
- Every major concept has one canonical home, and no concept has two authoritative
  explanations without a stated reason
- Harmful duplication is reduced; intentional summaries survived
- No contradiction is unresolved *and* unflagged
- Terminology is consistent, or the exception is documented
- `check-book.py` passes — links, anchors, owners, history
- Names describe responsibilities

---

## The rule that matters most

**Map first. Change later.**

Every edit you make is evidence destroyed about how the documentation got into the
state it was in. Knowing *which* document was wrong, and saying so, is worth more
than a directory that quietly agrees with itself.

---

## What next

- `Requires Code/Documentation Reconciliation` findings: `/book:check-docs` on them.
- Approved items after Audit or Review: run Harmonize. Then `/book:trim`, which may
  remove copies only once this pass has named each fact's owner.
- Edits on a `chore/docs-<slug>` branch: its pull request opens only when the person asks
  ([CLAUDE.md, *Git*](CLAUDE.md#git)).
- **In a flow** (`/book:flow`): `docs-health` → `/book:check-docs`.
