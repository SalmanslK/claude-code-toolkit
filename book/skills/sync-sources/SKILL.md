---
name: sync-sources
description: >
  Use when the whole Book must catch up with the client's requirements — "sync the docs with the new
  FSD", "a new FSD version landed, update everything". End to end: refresh every source, record new
  answers, defects and questions, carry each FSD change into the plans, FE guides and QA suite, then
  book:check-consistency, book:trim and book:fact-check. Not for one step alone (use that step's skill).
  Formerly /requirements-sync.
---

# /book:sync-sources — requirements → docs → code

This skill **orchestrates** the other skills of this plugin; it does not replace them. Each
phase names the skill that owns it — load that skill and follow it. What this file adds:

- the **order** of the phases, and the **handoffs** between them;
- how to run it **without re-reading the same docs** three times;
- the lessons from the first full run (a full run spends millions of subagent tokens).

Its helper scripts are in [`${CLAUDE_SKILL_DIR}/scripts/`](scripts/); run them from the repository root. Read
[`references/parallel-agents.md`](references/parallel-agents.md) before fanning out to subagents.

*The Book's command is `book`: `python devtools/book.py <command>` from the project's root. On a Book before v1.4.0, which has no `devtools/book.py`, run `python devtools/factory/factory.py <command>`; `book verify`, `init` and `upgrade` are `factory.py book verify` and so on there.*

## Why this order

1. **Requirements first.** Every later judgement is "does X match the FSD", and an audit against a
   stale snapshot produces confident, wrong findings.
2. **Content before structure.** `/book:check-consistency` never opens the FSD or the code to settle a
   tie. Run on docs that are behind the FSD, it produces a set of docs that are consistently wrong.
3. **Consistency before trimming.** `/book:check-consistency` decides which document owns each fact; only
   then can `/book:trim` safely delete the other copies.
4. **Code last.** `/book:fact-check` traces FSD → plan → code → tests, so the plans must have stopped
   moving first, or its audit is stale the day it is written.

## Modes: pick the cheapest one that answers the question

| Mode | Phases 2–4 read | When |
|---|---|---|
| **delta** (default) | Only docs changed since the last sync, plus docs that cite an FSD section that moved in this pass | Routine: a new FSD version, a run of merges |
| **full** | Every living doc | First run, a long gap, or when asked. Roughly 3× the cost of delta |
| **verify-only** | Nothing; skip phases 2–4 | The docs were synced recently and only "does DEV minus QA match the FSD?" is asked |

**The last sync** is the line `**Last requirements sync:**` under `project.md` Part 3 — its date,
the `dev` commit it reached, its mode and its tokens. Every pass rewrites it (wrap-up). The delta set
is what changed under `docs`, `CLAUDE.md` and `README.md` since that commit — `book sync-plan`
lists it — **plus** every doc that cites a section this pass's FSD change list names, which you add
after Phase 1. No such line: run **full**. *Why:* searching merge messages for "sync" also finds
FE-guide refreshes, which are not a sync.

**Skip rules** — `sync-plan` prints them with the counts it has and decides none; you confirm each,
and say which applied, in the report:

- **Phase 2** when no source moved and no comment thread brought a new answer.
- **Phase 3** when the delta set is empty and `id_status.py` and `check-book.py` are both clean.
- **Phase 4** when the last trim is under two weeks old and the delta set is under about 10 files.
- **Phase 5 is never skipped** — it is the question about code.

## Phase 0 — Preflight

- **Run `python devtools/book.py sync-plan`** (`--mode full|verify-only` when the person
  asked for one). Read-only: it fetches, then prints the real state of the checkout (a status
  captured at session start can be out of date), the pinned `origin/dev` and `origin/qa` SHAs, the
  last-sync line, the suggested mode, the delta set, QA's deployed commit, DEV minus QA, and the skip
  rules with their counts. Work from its SHAs. If DEV moves during the run, say so; never silently
  re-base.
- **The QA baseline is the commit deployed on the QA server**, not the `qa` branch: nothing deploys
  from `qa` yet, and the QA environment runs `dev` with the QA overlay
  ([CLAUDE.md, *Branches*](CLAUDE.md#branches)). `sync-plan` reads it through `book deploy
  status --target qa` and prints a `→ baseline:` line. *From the ledger — NOT a live read*: say so
  and ask the person to confirm it. *none* (`COULD NOT READ` and no ledger record): stop and ask;
  never fall back to the `qa` branch, which it prints for reference only.
- **Branch.** A sync is a general refresh, so
  [docs/CLAUDE.md, *Which branch a doc change goes on*](docs/CLAUDE.md#which-branch-a-doc-change-goes-on)
  sends it to `dev` on a branch of its own:
  `git checkout --no-track -b chore/docs-sync-<yyyy-mm-dd> origin/dev`. If the checkout holds
  someone else's work, use a worktree and say so.
- **Commit once per phase; push only at the end.**
- **Pick the mode** — `sync-plan` suggests one; a long gap since the last sync is your call for
  **full** — and say it in one line, with the delta file count.

## Phase 1 — Requirements refresh, then answers, defects and questions

1. **`/book:check-sources all`** — every source in `requirements/read-me.txt`, checked live.
   Metadata first; diff a source only if it moved.
2. **The FSD change list is the Part 3 entry `/book:check-sources` just wrote** — new requirements,
   corrections, renames, what did not change, section by section. Reuse it; do not diff again.
   `python "${CLAUDE_SKILL_DIR}/scripts/fsd_diff.py" OLD.pdf NEW.pdf --out <scratch>` is for what that entry does not cover: a pass
   spanning two or more revisions (diff the oldest against the newest), or a section's size. A heading
   inserted renumbers the ones after it; note it.
3. **Comment threads, on every run:** `/book:check-sources all` has already saved today's
   `requirements/fsd/comment-threads - <date>.md` — read every thread in it new since the last
   check; the BA answers there without editing the text. **Do not run `fsd-threads --save` again**:
   the tool allows one save a day. (Threads not saved — no sign-in: the Drive connector's comment
   export, then `python "${CLAUDE_SKILL_DIR}/scripts/fsd_comments.py" <json> --since <last check> --out <scratch>`.)
4. **Summarise a big new section with an agent.** When a section is written for the first time, a
   **sonnet** agent reads it from the scratch copy and returns a dense summary and its ambiguities,
   so the main context never loads a thousand lines of FSD.
5. **Verify against the code before logging a defect.** One read-only **Explore** agent, one
   numbered list, `path:line` evidence. New text or a comment that contradicts built code is a
   `defects.md` row; where the FSD text and a BA comment disagree, it is a **question** in
   `open-questions.md`, not a defect.
6. **Sweep the open questions and defects.** Start with `python "${CLAUDE_SKILL_DIR}/scripts/id_status.py"` (rows in the wrong
   section, citations whose status looks wrong — candidates only); a duplicate D or Q id is
   `devtools/checks/check-book.py`'s, which fails pre-commit and CI on one. Then one
   **sonnet** agent checks what the script cannot: an open question answered by the new text or a
   comment, an open defect fixed in the code but still *Open*. Give it the scratch copies.
7. **Record what `/book:check-sources` did not.** It has already written the snapshot, the Part 3
   entry, the `Last checked:` lines and the answers from comment threads — check they are there; do
   not write them twice. Add the `defects.md` rows and questions steps 5–6 found. A source it
   reported `moved — captured at the next weekly sweep` has no new snapshot: phases 2–5 work from
   its diff, and the report says the capture is pending.
   **Allocate every new Q and D id yourself**, never in parallel.
8. **Renumbering:** code comments and tests in their **own** commit, then the build and the
   API-contracts check. Living docs are renumbered in phase 2. Leave alone: `project.md` Part 3,
   `docs/release-notes/`, `docs/archive/`, `docs/Audit/` (`/book:fact-check` regenerates it).

Commit. Lead with the refresh verdict, as `/book:check-sources all` orders.

## Phases 2–4 — one agent per area, kept across all three

The biggest cost of the first run was **re-reading the same files three times**. Instead, start
**one agent per area** at phase 2 and **keep it across phases 2, 3 and 4 with SendMessage** — its
files are already in its context.

- **Areas (full mode):** **A** `project.md`, `defects.md`, `open-questions.md` and the root docs;
  **B** architecture, system overview, the infra plans, `api-conventions.md` and FE coverage;
  **C** core module plans and guides; **D** the remaining module plans and guides, and the QA suite. In delta
  mode, two or three areas on the same lines.
- **A context nearly full** (above about 350k tokens): a fresh agent for the next phase, briefed with
  the previous phase's report, not the files.
- **Model tiers:** judgement on the main model; applying an approved list on **sonnet**; code
  lookups on **Explore**.

### Phase 2 — Propagate each FSD change into the docs that own it

Each area agent gets this revision's and the previous one's change list, and traces each item into
the feature plan and its Tasks, `project.md` Part 1, `open-questions.md`, the FE guide, the QA suite,
the system overview, and `authorization.md` if permissions changed. It reports `file:line`, current
text, proposed text and source, then applies the fixes to its own files.

- **FE guides describe shipped code only** — a gap by its defect id, never a logged defect called fixed.
- **A built module's plan** notes the change and points at the defect; an unbuilt plan absorbs it,
  tasks included.
- **A new FSD self-contradiction** becomes a question, not a quiet choice.
- **Rules files** (CLAUDE.md, the skills): factual corrections go to the person first.

Commit.

### Phase 3 — `/book:check-consistency`: Review, then Harmonize the safe items

1. **Checks first:** `python "${CLAUDE_SKILL_DIR}/scripts/id_status.py"` and `python devtools/checks/check-book.py`; each area
   agent gets its share as known candidates, so it reads for contradictions and duplication, not ids
   and links.
2. **Each area agent audits its files**, grepping the whole set for its own concepts, and reports
   **SAFE / RECOMMENDED / NEEDS A DECISION**, about 60 findings at most, contradictions first.
3. **Items that need the code** go to phase 5; record their ids.
4. **Agents apply their SAFE findings** — book:check-consistency's Harmonize, which applies what is
   unambiguously safe. The RECOMMENDED list and every decision go to the person
   **in one message**, each with a suggested answer.
5. **After the decisions,** each agent gets its approved items. **Allocate new ids and renamed
   anchors centrally first.** Route cross-area leftovers once the owner has finished.
6. **`check-book.py` passes** — every link and anchor resolves, every doc has an owner. Commit.

### Phase 4 — `/book:trim`

The same agents apply the trim's **"Apply directly"** column only. Removals, merges and cross-file
moves go to the person; REVIEW items are routed onward. Compress only obvious verbosity in the
project's record (*Resolved*, Part 3, `defects.md` rows). Afterwards `heading_guard.py --since HEAD --claims`
reports 0 headings and 0 claims lost and `check-book.py` passes. Commit.

## Phase 5 — Verify DEV minus QA against the requirements

1. **Sort the range:** `python devtools/checks/task-evidence.py --since <qa>` — the line `sync-plan`
   printed under *DEV minus QA*, with the confirmed baseline — lists every PR merged
   since the QA baseline, with the plans and the D, Q and Jira ids it touched — the modules the code
   reaches. Split the PRs into docs-only and code-carrying with `git diff --stat` per merge.
2. **`/book:fact-check`** against the current FSD, scoped to the modules the code touches and the modules
   whose FSD sections changed in this pass. Skip specified-but-unbuilt modules.
3. **`/book:check-docs`** on the same modules, with every finding held back for code evidence.
4. **Every mismatch** becomes a `defects.md` row or a question. Code fixes happen on their own
   branches later.

Commit.

## Wrap-up

1. **Record the pass first:** rewrite the `**Last requirements sync:**` line under `project.md`
   Part 3 — `<date> · dev <short sha> · <mode> · <tokens>`, the tokens measured through Phase 5 —
   and commit it, so the commit reviewed below is the commit the PR opens. The next delta starts
   from here, and the next run's cost can be compared.
2. **`sh devtools/checks/ci-local.sh`** — for a docs-only pass, its repository (`checks`) tier: the
   generators' `--check`s, `check-book.py`, `check-private-data.py` and the rest. A Phase 1
   renumbering commit that touched code raises the tier to the build and tests — **check the skip
   count**.
3. `/book:self-review`, then `/book:ship` on the same commit — the description (add the baseline SHAs
   `sync-plan` pinned), and the push and pull request only when the person asks. Any later commit
   needs both again.
4. Offer `/book:publish-guides` if an FE guide changed, and `/book:progress` if tasks moved.
5. **The final report goes outside the repository**, to the person's own folder for written
   reports, or a path they name — `CLAUDE.md`'s ownership table has no home for a run report.

## The final report

- **Baseline:** branch, SHAs, mode, the FSD version reached, the skip rules that applied.
- **Per phase:** what it found, what it changed, its commit.
- **Numbers:** sources checked, comment threads read, questions answered and raised, defects
  logged, fixed and renumbered, findings by bucket, links checked and broken, lines removed.
- **Tokens, by phase:** each subagent's total from its completion notice, and the session's own,
  summed per phase — measured, not estimated. The total through Phase 5 is on the last-sync line;
  the wrap-up's own is reported here only.
- **Decisions** the person made, one line each.
- **Still open:** questions for the BA, defects from this pass, routed REVIEW items, and anything
  that could not be checked.

## Never

- Edit `requirements/`, except a new `V<n>.pdf` or a `read-me.txt`'s link or `Last checked:` line.
- Fix code in this pass — log it.
- Report "no change" for a source it could not reach — report "could not check".
- Resolve a contradiction by deleting one side.
- Let two agents write the same file at the same time.
- Put the run's report in the repository.

## Scripts

| Script | Replaces |
|---|---|
| *(the repo's own)* `book sync-plan [--mode M]` | Phase 0 by hand — the fetch, the pinned SHAs, the last-sync line, the delta set, QA's deployed commit and DEV minus QA; read-only, and it decides no skip rule |
| `heading_guard.py [--since REF] [--claims]` | Hand-diffing headings after a compression pass; `--claims` also ids, link targets and numbers |
| *(the repo's own)* `check-book.py` | Every agent writing its own link checker or duplicate-id hunt — it checks every link, anchor, owner and D/Q id, and runs on every commit |
| *(the repo's own)* `task-evidence.py --since REF` | Sorting a range of merges by hand — it lists each PR with its plans and ids |
| `id_status.py [root]` | Reading every doc to find stale Q and D statuses; its section 2 is candidates only |
| `fsd_diff.py OLD NEW --out DIR` | Ad-hoc `pdftotext` diffing and section sizing |
| `fsd_comments.py JSON --since TS [--out DIR]` | Hand-parsing the Drive connector's comment JSON, when `book fsd-threads` cannot run |

## What next

- The pull request, when the person asks; then `/book:publish-guides` and `/book:progress`
  where the wrap-up offered them.
- Each mismatch Phase 5 logged: its own `fix/D<n>-…` branch later, never in this pass.
- **In a flow** (`/book:flow`): `new-fsd-revision` → `/book:fact-check`; `answers-arrived` → `/book:raise`.
