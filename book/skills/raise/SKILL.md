---
name: raise
description: >
  Use when a defect is confirmed or the requirements leave something open — "raise a defect for this",
  "log this as a bug", "ask the BA about X", "add a question". Writes the defects.md row or the
  open-questions.md section in the house shape, with the next free id across every branch, and drafts
  any FSD comment without posting it. Not for fixing the defect.
argument-hint: defect | question
allowed-tools: Read, Grep, Glob, Bash(git status*), Bash(git log*), Bash(git show*), Bash(git fetch*), Bash(git branch*), Bash(python "${CLAUDE_SKILL_DIR}/scripts/next_id.py"*), Bash(python3 "${CLAUDE_SKILL_DIR}/scripts/next_id.py"*), Bash(python devtools/checks/check-book.py*), Bash(python3 devtools/checks/check-book.py*), Bash(python devtools/book.py config*), Bash(python3 devtools/book.py config*)
---

# /book:raise defect | question — one row, written right

*`${CLAUDE_SKILL_DIR}` below is this skill's folder, the one that holds this `SKILL.md` (the base directory shown when the skill loads). If it reaches you unexpanded, write that folder's absolute path in its place; never run a command with the literal text.*

A defect or a question exists only once it is in its ledger: a finding left in a chat or a pull request
dies with it. This skill writes **one** entry, in the shape `docs/CLAUDE.md` sets (*Defects*,
*Questions*, *Ids — D, Q*), so the checks pass on the first try. It never fixes the defect and never
answers the question.

**Defect or question?** A defect surprised us: the code is wrong against the FSD, an answer or its own
contract. A question is something the requirements do not settle, for the BA or the client. A
deliberate compromise is neither (the architecture guide's *Known trade-offs*); a missing requirement is
a defect only once we claimed the feature built, before that it is scope. When it is not plain which,
say why you lean one way and ask.

## 1. Take the id

```
git fetch
python "${CLAUDE_SKILL_DIR}/scripts/next_id.py"
```

It reads the highest id on the base, on every branch and in the working tree, so two branches never
take the same number. **Exit 2 means it could not check** (the base is not fetched): stop and say so,
never guess a number. Re-run it just before the commit if the work took a while.

## 2. Gather the facts, never guess them

- **What is wrong or open, in one or two sentences**, and **where**: the file and line, the route, the
  screen. Open the code; do not write from memory or from a grep hit alone.
- **The FSD section** it breaks or leaves open, from the highest revision in `requirements/fsd/`. Quote
  the words that matter. Infrastructure, CI, tests and code quality: "No FSD angle".
- **For a question:** the decision only someone outside can make, as **one closed question in plain
  words, with no section numbers**, and **your recommendation** (what gets built unless the answer says
  otherwise). Check *Resolved* first: an answered question is not asked twice.

## 3. Write the entry

**A defect**, under *Open* in `docs/defects.md`, using the table's own columns:

- **Severity** as the ledger's key shows it; **Status** one of `Open` · `Mitigated` · `Partial` ·
  `Blocked — <Q id or party>`.
- **Where the table has Type and Source columns** (a Book from 1.6): **Type** one of `spec-divergence` ·
  `bug` · `regression` · `test-gap` · `security` · `data` · `config-infra` · `tooling-ci`, and **Source**
  as `<source>: <reference>`, the source one of `qa` · `fe` · `ba-product` · `requirement-sync` ·
  `code-review` · `audit` · `tests-ci` · `developer`: *code-review: PR #60*. What each means: the
  *Defects* rules in `.claude/book/docs.md`. The Note ends with the day found: *found YYYY-MM-DD*.
- **Where it has a Found by column instead** (an older Book): **Found by** starting with one of the fixed
  words (`Review`, `PR review`, `Spec audit`, `Requirements check`, `Test`, `Guard/CI`, `While building`,
  `QA`, `Consumer`, `Client`, `Requirement change`), then the detail: *PR review, PR #60*; the text ends
  with **its class and the day found**: *Class: api-contract · found YYYY-MM-DD*, one class from the
  table in `docs/CLAUDE.md`.
- The text short (about 600 characters): what is wrong, where, the FSD section. The investigation goes
  in the commit or the PR, not the row.

**A question**, under *Still open* in `docs/open-questions.md`: a row in its summary table if the
ledger keeps one, and a `#### Q<n> · <title>` section with `**Status:** OPEN · **Raised:** <date> ·
**Area:** <topic>` — and, where the ledger keeps question States (a Book from 1.6), under it `**State:** OPEN ·
NOT POSTED · **Posted:** — · **Answered:** — · **In FSD text:** not yet · **Thread resolved:** no` — the question, and the recommendation line, headed as the project sets it:
`[book] recommendation_heading`, read with `python devtools/book.py config book.recommendation_heading`
(from Book 1.6 the settings are `factory.toml` over the Book's defaults; `"**What we suggest:**"`, say), or
`**Recommendation:**` when it sets none. Copy an existing question's heading if unsure. A plan
that depends on it lists the id in its open questions, and marks what it built on the recommendation
`[PROPOSED]`.

**The FSD comment** (a question for the client to answer in their document): draft it in the reply, in
plain words with the recommendation. **Never post it** unless the person says so in this turn.

## 4. Check, and say where it goes

```
python devtools/checks/check-book.py
```

It holds the status words, the Type and Source (or, in an older Book, the class and *Found by*), the question State and duplicate ids *[enforced]*. Show the person the
entry. **Which branch:** a defect the current work found or fixes stays on the work's branch; one raised
on its own goes on a `chore/docs-<slug>` branch cut from the base with `--no-track` (`docs/CLAUDE.md`,
*Which branch a doc change goes on*). Commit only when asked; the id goes in the fixing commit's message.

## What next

- A defect to fix now: a `fix/<id>-<slug>` branch; its commit names the id.
- A question that blocks a plan: the plan lists it; `/book:check-sources` before chasing the answer.
- An answer arrived: `/book:sync-sources` moves it to *Resolved* and carries it through the Book.
- **In a flow** (`/book:flow`): `answers-arrived` → `/book:impact`; `qa-artifacts-changed` → `/book:progress`; `new-feature` → done; `fix-defect` → `/book:self-review`; `spec-says-x` → `/book:write-for`; `dev-deploy` → done.
