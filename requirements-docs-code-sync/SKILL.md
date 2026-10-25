---
name: requirements-docs-code-sync
description: >
  a repository (and repos built the same way): an end-to-end sync pass that brings
  the whole knowledge base in line with the client's current requirements, then
  checks the code waiting for QA against them. It refreshes every requirements
  source (the FSD text and its comment threads); records new answers, defects
  and questions; sweeps open questions and open defects; propagates each FSD
  change into plans, FE guides, the QA suite and the system overview; then runs
  docs-harmonizer, then docs-gardener, then spec-audit and code-doc-audit over
  what DEV holds that QA does not; and writes a final report outside the repo.
  Use it whenever someone asks to "sync the docs with the new FSD", "check
  everything is up to date before the QA build", "verify dev minus qa against
  the requirements" or "a new FSD version landed — update everything", or wants
  the harmonizer and gardener run as part of a larger docs-and-code check, even
  if they name only some of the steps. For a single step, use that step's own
  skill instead (refresh-requirements, docs-harmonizer, spec-audit…).
---

# Requirements → docs → code sync

This skill **orchestrates** skills that already live in the repo
(`.claude/skills/`); it does not replace them. Each phase names the skill that
owns it. Load that skill and follow it. What this file adds:

- the **order** of the phases
- the **handoffs** between them
- how to do it **without spending millions of tokens re-reading the same docs**
- the lessons from the first full run (2026-09-23, FSD V13, about 4–5M
  subagent tokens)

Bundled scripts live in this skill's `scripts/` folder
(`~/.claude/skills/requirements-docs-code-sync/scripts/`); run them from the
repo root. Read `references/parallel-agents.md` before fanning out to subagents.

## Why this order

1. **Requirements first.** Every later judgement is "does X match the FSD", and
   an audit against a stale snapshot produces confident, wrong findings.
2. **Content before structure.** The harmonizer never opens the FSD or the code
   to settle a tie. Run on docs that are behind the FSD, it produces a
   consistent set of docs that are consistently wrong.
3. **Harmonizer before gardener.** The harmonizer decides which document owns
   each fact; only then can the gardener safely delete the other copies.
4. **Code last.** `spec-audit` traces FSD → plan → code → tests, so the plans
   must have stopped moving first, or its audit is stale the day it is written.

## Modes: pick the cheapest one that answers the question

| Mode | Phases 2–4 read | When |
|---|---|---|
| **delta** (default) | Only docs changed since the last sync, plus docs that cite an FSD section that moved in this pass | Routine: a new FSD version, a run of merges |
| **full** | Every living doc (about 65 files, 37k lines) | First run, a long gap, or the user asks. Roughly 3× the cost of delta |
| **verify-only** | Nothing; skip phases 2–4 | The docs were synced recently and only "does DEV minus QA match the FSD?" is being asked |

**How to find "the last sync":**

1. Look for a merged commit whose subject is `Harmonize the documentation set`,
   or whose branch was `chore/*sync*`:
   `git log origin/dev --grep "Harmonize the documentation set" -1 --format=%H`.
2. The delta file set is then:
   - `git diff --name-only <that>..origin/dev -- docs CLAUDE.md README.md`
   - **plus** every doc that cites a section the FSD diff flagged. Grep for
     each `§` number from `sections.txt`.
3. If no earlier sync exists, run **full**.

**Skip rules** (say which ones applied, in the report):

- **Phase 2** when no source moved and no comment thread brought a new answer.
  There is nothing to propagate.
- **Phase 3** when the delta set is empty and `id_status.py` and `linkcheck.py`
  are both clean.
- **Phase 4** when the last gardener pass is under two weeks old and the delta
  set is small (fewer than about 10 files). Density decays slowly.
- **Phase 5 is never skipped**, because it is the question about code.

## Phase 0 — Preflight

- **Look at the real state; don't trust a snapshot.** Run `git fetch`,
  `git branch --show-current` and `git status`. A git status captured at session
  start can be out of date: the branch it shows may already be merged.
- **Pin the baseline.** Record the DEV tip SHA (`origin/dev`) and the QA baseline
  SHA. If DEV moves during the run, say so; never silently re-base.
- **Settle what "QA" means, once.** It can be the `qa` branch or the commit
  actually deployed on the QA server. They can differ, because the QA server has
  run `dev` with the QA overlay. The branch is the usual answer. If the user
  means the deployed commit, they must supply
  `git -C /srv/app/qa/backend rev-parse --short HEAD`.
- **Branch.** `dev` takes no direct commits, so cut
  `chore/<topic>-sync-<yyyy-mm-dd>` from `dev`. The user watches this checkout in
  their IDE: branch here when it is clean. Use a worktree only when another
  session's work is present, and say so if you do.
- **Commit once per phase, and never push until the end.**
- **Pick the mode** (above) and tell the user in one line, together with the
  delta file count.

## Phase 1 — Requirements refresh, then answers, defects and questions

1. **`/refresh-requirements`**, which wraps `requirements-snapshot`. Every
   source listed in `requirements/read-me.txt` is checked live. Check metadata
   first; diff a source only if it moved.
2. **FSD text: `scripts/fsd_diff.py OLD.pdf NEW.pdf --out <scratch>`.**
   - It measures each section's size and writes a body diff cleaned of page
     numbers and TOC lines.
   - A table row that looks reordered is usually `pdftotext`. Check it against
     the Doc's own text.
   - When a heading is inserted, the headings after it are renumbered (V13 moved
     §2.13.12 to §2.13.13). Note the renumbering.
3. **Comment threads, on every run.** Call `read_file_content` with
   `includeComments: true`. The result lands on disk as JSON; then run
   `scripts/fsd_comments.py <json> --since <last run> --out <scratch>`. The last
   run is dated in `requirements/fsd/read-me.txt`. Read each thread the script
   lists. The BA answers in these threads without editing the text.
4. **Summarise a big new section with an agent.** When the diff shows a whole
   section written for the first time (§2.14 in V13), have a
   **sonnet** agent read it from the scratch copy and return a dense summary
   plus its ambiguities. The main context never loads roughly 1,000 lines of
   FSD.
5. **Verify claims against the code before logging a defect.** Send every item
   to one read-only **Explore** agent in a single numbered list, asking for
   `path:line` evidence.
   - A comment or new text that contradicts built code is a `defects.md` row.
   - Where the FSD text and a BA comment disagree with each other, it is a
     **Part 2 question**, not a defect (Q94 → Q123).
6. **Sweep the open questions and open defects.**
   - **Start with `scripts/id_status.py`.** It lists duplicate defect ids,
     Still-open rows that don't match their sections, and a *candidate* list
     of citations whose status looks wrong.
   - **Then one sonnet agent** checks only what the script can't: whether an
     open question is answered by the new text or a comment, and whether an
     open defect is fixed in the code but still in *Open*. Give it the
     scratch copies (`fsd-live-doc.txt`, `fsd-comments-all.txt`) so it doesn't
     fetch them again.
7. **Record:**
   - a Part 3 entry in the existing shape;
   - Part 2 moves: an answered section moves under *Resolved*, and its row is
     deleted;
   - `defects.md` rows;
   - a dated note in each source's `read-me.txt`;
   - the new `V<n>.pdf`, after checking it opens with `pdftotext`.

   **Allocate every new Q and D id yourself**, never in parallel.
8. **Renumbering:** code comments and tests go in their **own** commit, then
   re-run the build and the API-contracts check. Living docs are renumbered in
   phase 2. Leave these alone:
   - Part 3
   - `docs/release-notes/` (dated snapshots)
   - `docs/archive/`
   - `docs/Audit/` (spec-audit regenerates it)

Commit. Lead with the refresh verdict, as refresh-requirements orders.

## Phases 2–4 — one agent per area, kept across all three phases

The biggest cost in the first run was **re-reading the same files three times**:
a tracing agent, then a harmonizer auditor, then a gardener, all on the same
docs. Instead, start **one agent per area** at phase 2 and **keep it across
phases 2, 3 and 4 with SendMessage**. Its files are already in its context, so
each later phase costs a fraction of the first.

- **Areas (full mode):**
  - **A** — `project.md`, `defects.md` and the root docs
  - **B** — architecture, system-overview and the infra plans, plus
    `api-conventions.md` and FE coverage
  - **C** — core module plans and guides
  - **D** — Orders plans and guides, plus the QA suite

  In delta mode, group the delta files into two or three areas by the same
  lines.
- **If an agent's context is nearly full**, typically above 350k tokens, replace
  it with a fresh agent for the next phase. Brief it with the previous phase's
  report, not the files.
- **Model tiers:** audits that need judgement use the main model. Applying an
  already-approved list is mechanical: when you need a fresh agent for that,
  use **sonnet**. Code lookups use **Explore**.

### Phase 2 — Propagate each FSD change into the docs that own it

Send each area agent the Part 3 checklist: this revision's and the previous
one's changes. It traces each item into the feature plan, Part 1 and Part 2,
the FE guide, the QA suite, the system overview, and `authorization.md` if
permissions changed. It reports `file:line`, the current text, the proposed text
and the source. Then it applies the fixes to its own files. The rules:

- **FE guides describe shipped code only.** They may warn of a gap by its defect
  id, and never claim a logged defect is fixed.
- **A built module's plan** notes the change and points at the defect. An
  unbuilt plan absorbs the change.
- **A new FSD self-contradiction** becomes a Part 2 question (Q124), not a quiet
  choice.
- **Rules files** (CLAUDE.md, the skills): factual corrections go to the user
  first.

Commit.

### Phase 3 — `/docs-harmonizer`, Review mode

1. **Run the scripts first:** `id_status.py` and `linkcheck.py`. Hand each area
   agent its share of their output as "known candidates", so it spends its
   reading on contradictions and duplication and not on id or link hunting.
2. **Each area agent audits its files** against the harmonizer's references,
   grepping the whole set for its own concepts. It reports **SAFE /
   RECOMMENDED / NEEDS A DECISION**, capped at about 60 findings, with the
   contradictions first.
3. **Items that need the code** go to phase 5. Record their ids.
4. **Tell each agent to apply its SAFE findings.** Meanwhile bring the
   RECOMMENDED list and every decision to the user **in one message**, with a
   suggested answer for each.
5. **After the user decides,** send each agent its approved items. **Allocate
   any new id or renamed anchor centrally first.** Route cross-area leftovers
   yourself once the owning agent has finished.
6. **`linkcheck.py` must report 0 broken.** Then commit.

### Phase 4 — `/docs-gardener`

The same area agents apply the gardener's **"Apply directly"** column only.

- **To the user:** removals, merges and cross-file moves.
- **Routed onward:** REVIEW items.
- **Compress only obvious verbosity** in Part 2 *Resolved*, Part 3,
  `defects.md` rows and dated history. They are the project's record.
- **Afterwards,** `heading_guard.py --since HEAD` must report 0 headings lost,
  and `linkcheck.py` must report 0 broken.

Commit.

## Phase 5 — Verify DEV minus QA against the requirements

1. **Sort the range.**
   - Run `git log --first-parent --merges <qa>..<dev>` and `git diff --stat`.
   - Split the PRs into docs-only and code-carrying.
   - Name the modules the code touches.
2. **`/spec-audit`** against the current FSD, scoped to two groups:
   - modules the code in the range touches
   - modules whose FSD sections changed in the revisions this pass covered

   Skip modules that are specified but not built. This refreshes `docs/Audit/`.
3. **`/code-doc-audit`** on the same modules. Feed it every finding held back
   for code evidence in phases 3 and 4.
4. **Every mismatch** becomes a `defects.md` row or a Part 2 question. Code fixes
   happen on their own branches later.

Commit.

## Wrap-up

1. `dotnet build`, then `dotnet test`, and **check the skip count**.
2. Both generator `--check`s.
3. `/code-review`.
4. Push, and open the PR. Its description carries a summary, a test plan and the
   baseline SHAs.
5. `graphify update .`
6. Offer `/update-fe-integration-guides-on-drive` if any FE guide changed.
7. **The final report goes outside the repo**: `D:\Claude-Local\<Project>\reports\`,
   named `<Project>-<topic>-YYYY-MM-DD.md` (the user's single home for
   Claude-written docs, decided 2026-09-24), or a path the user names. CLAUDE.md's ownership table has no home for a run report.

## The final report

- **Baseline:** branch, SHAs, mode, the FSD version reached, and the skip rules
  that applied.
- **Per phase:** what it found, what it changed, and its commit.
- **Numbers:**
  - sources checked
  - comment threads read
  - questions answered and raised
  - defects logged, fixed and renumbered
  - findings by bucket
  - links checked and broken
  - lines removed
  - approximate subagent tokens, so the next run can compare
- **Decisions** the user made, one line each.
- **Still open:** questions for the BA, defects from this pass, routed REVIEW
  items, and anything that could not be checked.

## Never

- Edit `requirements/`, except a new `V<n>.pdf` or a `read-me.txt` note.
- Fix code in this pass. Log it.
- Report "no change" for a source it could not reach. Report "could not check".
- Resolve a contradiction by deleting one side.
- Let two agents write the same file at the same time.
- Put this skill's scripts or report into the repo. They live with the skill and
  in the scratchpad.

## Scripts

| Script | Replaces |
|---|---|
| `linkcheck.py [root] [--files …]` | Every agent writing its own link checker. It exits 1 on any broken link |
| `heading_guard.py [--since REF]` | Hand-diffing headings after a compression pass |
| `id_status.py [root]` | Reading 37k lines to find stale Q and D statuses and duplicate defect ids. Its section 3 is candidates only, so read each hit |
| `fsd_diff.py OLD NEW --out DIR` | Ad-hoc `pdftotext` diffing and section sizing |
| `fsd_comments.py JSON --since TS [--out DIR]` | Hand-parsing the connector's comment JSON |
