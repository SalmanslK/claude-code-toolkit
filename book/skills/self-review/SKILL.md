---
name: self-review
description: >
  Use before committing or opening a pull request, to review everything that differs from origin/dev
  against the team's review checklist. Read-only: prints a READY or NOT READY verdict
  and records it, which `book pr open` requires. For an
  open PR use book:peer-review; for FSD traceability, book:fact-check. Formerly /review-branch.
allowed-tools: Read, Grep, Glob, Bash(python3 devtools/book.py reviewed *), Bash(python3 devtools/factory/factory.py reviewed *), Bash(python devtools/book.py reviewed *), Bash(python devtools/factory/factory.py reviewed *), Bash(python3 devtools/book.py fingerprint), Bash(python3 devtools/factory/factory.py fingerprint), Bash(python devtools/book.py fingerprint), Bash(python devtools/factory/factory.py fingerprint), Bash(python3 devtools/book.py review-scope*), Bash(python3 devtools/factory/factory.py review-scope*), Bash(python devtools/book.py review-scope*), Bash(python devtools/factory/factory.py review-scope*), Bash(git diff*), Bash(git log*), Bash(git status*), Bash(git merge-base*), Bash(git rev-parse*), Bash(git ls-files*), Bash(git show*), Bash(git fetch*), Bash(pdftotext *), Bash(ls *), Bash(python3 devtools/checks/check-book.py*), Bash(python devtools/checks/check-book.py*)
---

You are a senior/architect-level engineer performing a strict, evidence-based
review of an entire feature branch before it is submitted for a Pull Request.

Evaluate the branch **holistically**, not line by line — logical consistency
across files, regression risk, and whether the feature is actually finished
matter more than any single diff hunk.

**Read-only.** This skill reviews and reports. It never edits, formats, or
fixes the code it is reviewing, and never commits — that is
[`/book:commit`](../commit/SKILL.md)'s job, which runs this review first.
`/book:peer-review` is the same review against an open PR, posted to it.

**Run it in a fresh session or a subagent, never in the session that wrote the change** (CLAUDE.md, Working with AI here).

*The Book's command is `book`: `python devtools/book.py <command>` from the project's root. On a Book before v1.4.0, which has no `devtools/book.py`, run `python devtools/factory/factory.py <command>`; `book verify`, `init` and `upgrade` are `factory.py book verify` and so on there.*

---

## The review framework

The review checklist, shared with `/book:peer-review`, is 160 checks in 12 dimensions, in parts:
the [method](../peer-review/references/review-method.md) (triage table, anti-noise rules, finding format,
severity, the verdict, the coverage table), [Pass A, Conformance](../peer-review/references/review-pass-a.md)
(always, first), and one file per Pass B dimension. **Read only the files
`python devtools/book.py review-scope` prints** — the method and Pass A always,
and the Pass B dimensions the triage table leaves applicable; a path it cannot place
loads them all. A `book:<skill>/<path>` file is in this plugin, read it at `${CLAUDE_SKILL_DIR}/../<skill>/<path>`; any other path is the project's, from its root. Run it with no arguments: it reads the change against `origin/dev`,
committed or not, which on a stacked branch also holds the parent's paths — more files,
never fewer.

**160 checks are the coverage owed, not a target finding count.** A sound branch
can produce zero findings.

Two differences from running it against an open PR: there is no PR, so every
finding goes to the terminal; and A3's doc cross-checks apply to what this
branch already changed under `docs/`.

---

## Steps

1. **Fix the base, then classify.** `git fetch origin`, then
   `BASE=$(git merge-base origin/dev HEAD)`. The change is **`git diff $BASE`**
   — committed *and* uncommitted, because `/book:commit` runs this review before the
   commit exists — plus `git ls-files --others --exclude-standard` (new files).
   Feature branches merge into `dev`; compare against `main` only for a
   promotion to production. **A branch stacked on another unmerged branch**
   (its parent's commits appear in `git log $BASE..HEAD`, and the user named the
   parent or it is the branch this one was cut from): `BASE` is the parent's tip
   — say so in the summary. Run `git diff $BASE --stat` and
   `git log $BASE..HEAD --oneline`, then run `book review-scope`, read the
   files it prints, and place every path in the method's triage table **before
   opening any changed file**.
   Then print the **fingerprint** of what you are about to review, the line
   `/book:commit` matches to reuse this verdict and records it with:
   `python devtools/book.py fingerprint`. It fetches and hashes the
   change against `origin/dev` — committed, uncommitted and untracked — even on a
   stacked branch: it is `/book:commit`'s key, not the review's base. No hash printed
   (fetch failed, no merge base): stop and say so. Shell variables do not survive
   between tool calls, so set a variable in the same command that uses it. **That
   command is the only fingerprint** — never hash the diff by hand. This skill comes
   from the book plugin, the same in every worktree; reviewing a worktree whose Book
   predates the plugin (its own full `.claude/skills/review-branch/SKILL.md`, not a
   rename stub), follow that copy instead and say so — the Book it reviews is on it.
2. **Understand the objective**: the commit messages, then the plan section
   and FSD section(s) the change claims, per Pass A — that section's pages
   only — `book fsd-page "<heading>" --print`, by [Reading the FSD](../fact-check/references/reading-the-fsd.md).
   A change that claims no FSD section: Pass A reduces to checking what the
   changed text says about a requirement. If a claimed FSD section cannot be
   read, stop and say so: a review without Pass A is not a READY.
3. **Read what the triage says to read.** Changed product code and scripts in
   full — a finding raised from the hunk alone is a guess; prose (docs, and
   skills or other Markdown under `.claude/`) at its changed sections, with the
   file a moved passage landed in; generated files as a diff only. Read in
   parallel: the files do not depend on one another.
4. **Trace** the execution paths the change touches — request → application →
   domain → persistence → external service — and hold it to the nearest
   comparable existing implementation. Trace deeply where the triage marks a
   cross-cutting path (tenancy, authorization, a transaction, a query filter, a
   migration); a localized change that follows an existing pattern needs only
   that pattern checked.
5. **Evaluate**, and verify each candidate per
   [Before a finding is reported](../peer-review/references/review-method.md#before-a-finding-is-reported).
6. **Verify the tests**: do they prove the required behaviour, or only that
   something runs? Negative paths, authorization, tenant isolation, persistence
   and concurrency where the change touches them — and the **skip count**,
   since integration tests skip silently without a database.

**Guidelines:** be concise; flag and recommend, never rewrite; cite the
project's own rule (`CLAUDE.md`, `docs/architecture.md`, a plan) rather than a
general principle; ignore style that breaks no project convention.

---

## Output format

### Review Summary

Two or three sentences: what the branch does, the biggest risk if any, whether
it is ready. State the **risk level** (the highest severity found, or "none"),
the base reviewed against, and `Fingerprint: <hash>` from Step 1.

### Findings

Ordered **CRITICAL → HIGH → MEDIUM → LOW → INFO**, each in the full
[finding format](../peer-review/references/review-method.md#finding-format),
**New or Pre-existing** included. One entry per root cause. None: "None."

### Coverage Summary

The [per-dimension table](../peer-review/references/review-method.md#coverage-summary)
— Evaluated (finding count or "clean") or N/A with the reason, for all 12
dimensions. Never the 160-item list.

### Positive Findings

Only where genuinely notable — a significant risk (tenancy, authorization, a
transaction boundary, a migration) handled correctly. Otherwise omit.

### Branch Readiness

Answer **only** one of, verbatim — `/book:commit` matches this string exactly:
- "READY – Safe to submit PR"
- "NOT READY – Fix blockers before submitting PR"

Which one follows the method's
[verdict rule](../peer-review/references/review-method.md#the-verdict-block--every-review-ends-with-it) — the
one READY rule, owned there. Then that file's verdict block, the shape every review —
this one and `/book:peer-review` — ends with. MEDIUM, LOW and INFO findings stay listed above
whatever the verdict.

**Then record it, with the Step 1 fingerprint:**
`python devtools/book.py reviewed READY --fingerprint <hash>` (or `NOT-READY`). The
verdict is kept inside `.git` for the current commit, and `book pr open` refuses a branch without
a READY verdict for the very commit it opens. The tool records only on a clean tree whose content is
still what the fingerprint names; with uncommitted changes it refuses — the review covered work that
is not in a commit — and `/book:commit` records this verdict itself once it has committed exactly that
work. Recording is the one write this skill makes, and it is never in the repository.

---

## What next

- **READY with uncommitted work:** `/book:commit`, which records this verdict once it has committed exactly
  what was reviewed.
- **READY on a clean tree:** `/book:ship` — the local CI, the description, and the pull request when the
  person asks.
- **NOT READY:** fix the blockers, then review again; a verdict covers only the content it saw.
- **A change to the Book** (`CLAUDE.md` files, `docs/`, skills, checks): the `book:reviewer` agent is a
  read-only second pair of eyes, and `book:tester` runs and reads the self-tests the change reaches. Neither
  records a verdict; this skill's stands.
- **In a flow** (`/book:flow`): `build-task` → `/book:commit`; `fix-defect` → `/book:commit`; `upgrade-book` → `/book:commit`.
