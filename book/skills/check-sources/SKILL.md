---
name: check-sources
description: >
  Use before trusting an FSD section, chasing a question or releasing, or when asked whether the
  client's documents are current (the FSD and its comments, QA artifacts, Q&A, the release plan:
  requirements/read-me.txt). `all` checks every live source and leads with UP TO DATE, STALE or COULD
  NOT VERIFY. Not for carrying a change through the Book (book:sync-sources). Formerly
  /requirements-check.
---

> **One source or all of them.** Named sources (or the ones a question is about): the
> phases below. **`all`** — every source with a live link: see
> [`all` — every source, verdict first](#all--every-source-verdict-first).

You are checking whether **the client's documents have moved under us**. Everything
else in this repository changes because somebody here changed it; these change on
their own, so being out of date is the default rather than an accident.

**Why it matters:** a question in `docs/open-questions.md` that looks unanswered may
have been answered weeks ago — that has happened, and chasing the client for it costs
goodwill. Worse, **a plan built on a section that has since changed is confidently
wrong**, and nothing in the code, tests or docs will contradict it. Every other skill
reasons from the snapshot, so run this **first** when requirements are in play.

*The Book's command is `book`: `python devtools/book.py <command>` from the project's root.*

---

## Blocked means stop

CLAUDE.md's rule, here: **if a source
cannot be read** — the connector fails, a permission is refused, the guard refuses a step, an
export is not available — **finish reading the sources you can, then stop before Phase 4 and
tell the person** which could not be read, why, and the one thing that would unblock each
(usually the manual export below). Capture and record nothing until they answer. **Not
knowing is not the same as no change:** never report "no change" for a source you could not
open. Continue on the person's answer — the export, or an explicit "go on without it", which
the report then names as **could not check**.

---

## The sources

**Start with `python3 devtools/book.py requirements status`** — read-only and
offline. From `requirements/read-me.txt` (the root index,
and the **one place every live link is kept** — its *LINKS*, never hard-coded here) and the
folders beside it, it prints one line per source: its live link or what the index records
instead (none, not shared, not set up — with the reason — or a `<link>` placeholder), our
newest snapshot and its date, the folder's *Last checked* line, and whether this week's
capture is already taken; then a verdict. It fetches nothing, so every source with a live
link reads **needs a live check** — what is left for you is the live comparison of exactly
those, below. The table covers the sources this skill's capture machinery applies to.

| Source | Live | Our copy | Authority |
|---|---|---|---|
| **FSD** | Google **Doc** — **text *and* comment threads** | `requirements/fsd/… - V<n>.pdf` (text); the comment threads are read live every run and saved as `comment-threads - <date>.md` | **Source of truth. Wins every conflict.** The BA answers developers' questions *in the comments*, often without touching the text |
| **Permissions matrix** | **If the project has one** (`requirements/read-me.txt` says); otherwise permissions come from the FSD (CLAUDE.md, *Layout*) | `requirements/permissions-matrix/`, empty when there is none | If one is ever shared: a Google Sheet below the FSD, captured as `V<n>.pdf` and **read as CSV, never from the PDF** |
| **QA artifacts** | A Drive **folder** plus two **Sheets** | `requirements/qa-artifacts/`, unversioned | **Not a requirement source** (below) |
| **Product Q&A** | Google **Doc** | `requirements/product-questions-and-answers/…` | Answers outside the FSD proper; same `V<n>.pdf` scheme as the FSD |
| **FE integration bugs** | Google **Sheet** | `requirements/fe-integration-bugs/`, unversioned | Treated like QA artifacts — **not a requirement source** |
| **Release Plan** | Google **Sheet** | `requirements/release-plan/`, `backup/`-with-date-suffix | The committed schedule — `project.md`'s delivery pace. **A workbook can hold other projects' tabs:** capture only the tabs that are yours, each as its own CSV — never fetch, diff or capture the whole workbook. Tab ids are in *LINKS* (`gid=`) |

**Out of scope**, not worth fetching: `wireframes/` (Figma), and anything the root
index marks as having no live source (`email-templates/`, the two loose PNGs,
`fe-api-contracts/` — derived from the frontend's code, so "refresh" means
re-deriving from that repo).

**Build from the highest `V<n>`**, numerically (CLAUDE.md, *Layout*).

### The FSD wins, and QA does not count as a requirement

*Which document wins* (the project's `docs/open-questions.md`) settles it: a rule
found only in a QA case or another supporting source is **a question for `open-questions.md`,
never a rule to adopt**; confirmed in the FSD, it is corroboration worth citing.

---

## Phase 1 — Get the current documents

For each source `requirements status` marked **needs a live check** (its link is in
*LINKS*; its last check is the line the command printed):

1. **The Google Drive connector**, if this session has one — it reads Docs and Sheets
   directly. Test it with one `get_file_metadata`
   call before committing to it. **If any read fails**, follow
   [`references/connector-failures.md`](references/connector-failures.md) — then stop
   for that source, per *Blocked means stop*.
2. **Otherwise, ask the person to export**: File → Download → **PDF** for a Doc,
   **CSV** for every Sheet. Give the link and where to save it, and wait.

**The QA folder is a Drive *folder*, so files can be added, not just changed.** List it
and compare the set of files; a new document is a finding in its own right.

### The FSD Doc's comment threads — every run, not just the text

The BA answers developers in the FSD Doc's comment threads, **frequently without
changing the text**, and the PDF export drops comments. The first run that reads them
typically finds questions already answered there, some the
opposite of what had been built. **A run that only diffs the text is not a complete
check of the FSD.**

- `read_file_content` on the FSD Doc with **`includeComments: true`**. The result lands
  on disk as JSON `{commentThreads: [...], fileContent: "..."}`; each thread carries
  `commentId`, `status` (`OPEN`/`RESOLVED`), a `headPost` and `replies` with
  `authorName`, `content`, `modifiedTime`. Dump them chronologically with a short
  script and **read every thread modified after the previous run** — the *Last
  checked* line in `requirements/fsd/read-me.txt`.
- **Threads carry no key to their position in the text** — the `kix.…` markers and the
  `AAAC…` thread ids are unrelated id spaces. Tie a thread to a section by its wording;
  a developer's question usually quotes the rule.
- **The BA's replies are answers.** Cross-check each against `open-questions.md`'s
  *Still open* table: an answered question moves with the quoted reply and its date.
  Where the reply contradicts built code it is a `defects.md` row, never a silent fix.
  "Need a meeting" / "will clarify later" is recorded on the question too.
- **`RESOLVED` means the thread was closed, not that the Doc was corrected.** A
  resolved "Updated" reply should show in the text diff; if it does not, check.
- Comment activity moves `modifiedTime`/`fileSize` without changing the export. A
  metadata move with an identical PDF means **read the new comments**, not "nothing
  happened".
- **Save the threads with the snapshot**, so the BA's answers are part of the book: `python3 devtools/book.py fsd-threads --save`
  writes `requirements/fsd/comment-threads - <date>.md` (it needs `live_credential` in your
  private settings file — `devtools/README.md`, *Private settings*; without it, write the
  same file from the dump above). It prints what Phase 5 records: the Doc's
  `modifiedTime`, and the time the threads were read through — keep both in
  `requirements/fsd/read-me.txt`'s *Last checked* line as `(modifiedTime <t>)` and
  "modified after <t>", because **the next check (`book fsd-threads`) compares the live Doc
  against exactly those two**. Saving threads is a record, not a capture: it may happen on any
  day. **But record the new `modifiedTime` only when our newest `V<n>` still matches the
  Doc's text** (Phase 2 found only comment activity, or Phase 4 captured it). When the
  text moved and was not captured, leave the recorded `modifiedTime` as it was, so the
  next check keeps reporting the FSD stale until the capture — never a false all-clear.

A quick `includeComments` read on the Product Q&A Doc costs one call; the QA
artifacts are `.xlsx`, which the reader does not comment-expand.

## Phase 2 — Fingerprint before diffing

**Cheap check first, per source.**

- **Anything with metadata:** compare `modifiedTime` against the date our copy was
  taken. Last modified *before* our copy means **it cannot have changed** — conclusive,
  one call. Corroborate with exact byte size. This is the only fingerprint for
  spreadsheets and binaries, and the fastest for everything else. *Caveat:* our copy's
  date is its file time on disk, the download time only if it was downloaded fresh —
  where the margin is narrow or provenance unclear, extract and compare instead.
- **A folder:** its `modifiedTime` changes when children are added or removed, not when
  a child is edited. Check the children individually; if they cannot be listed, the
  folder's contents are **unverified**, not clean.
- **Text documents and PDFs:** compare counts —
  [`references/diffing-and-capturing.md`](references/diffing-and-capturing.md).

**Nothing moved → stop here for that source.** That is a complete and useful answer.

## Phase 3 — Diff (only what moved)

Follow [`references/diffing-and-capturing.md`](references/diffing-and-capturing.md):
the guard-compliant diff, the noise to read past, section sizes, and the four
categories Part 3 uses.

## Phase 4 — Capture (only what moved)

**Where the capture goes.** A new snapshot and everything Phase 5 records with it are a
general refresh — docs/CLAUDE.md, *Which branch a doc change goes on* says which branch; its pull
request opens only when the person asks (CLAUDE.md, *Git*). Check the branch before
the first write.

**At most one capture per source per week** (Monday to Sunday) — the *Cadence* in
`requirements/read-me.txt`. Before capturing, run
`git fetch origin`, then `requirements status` again: its `capture:` field says whether this
week's capture is taken — on `origin/dev`, this branch, or an unmerged `origin/chore/docs-*`
branch (an open capture counts too). Only snapshot files count — a saved
`comment-threads - <date>.md` is a record, not the week's capture. If the fetch fails, stop:
a stale `origin/dev` cannot answer this. `check-protected-paths.py` fails a second capture of
a source in one week, so a capture this field says is taken will not merge.

- **None this week, and this is the weekly sweep** (`all`), or the person asked to take
  the week's capture early: capture, as below.
- **Otherwise, do not capture.** Report the source as `moved — captured at the next
  weekly sweep`, record what Phase 5 can record without a snapshot (a BA answer from a
  comment thread goes on its question now), and say which plans the change lands on. A
  second capture in the same week only on the person's explicit word. Until the
  capture, the FSD's *Last checked* `modifiedTime` stays where it was (Phase 1), so the
  next check reports it stale — the honest answer while our copy is behind.

**FSD, matrix and Product Q&A** — save the download as the next version,
`… - V<n+1>.pdf`, in the same folder, matching the naming exactly. **Never overwrite or
edit an existing `V<n>.pdf`**; they are the record of what we were told and when.

**QA artifacts, FE integration bugs and the Release Plan** — move the superseded copy
into that source's `backup/` folder with a date suffix, and put the new one at its
plain filename, so links to "the current document" keep working. **Not the `V<n>`
scheme**: they are fast-changing trackers, and an immutable file per check would be
noise.

Decode and verify every capture as the reference says, before treating it as good.

## Phase 5 — Record

- **Answers from the FSD Doc's comments** go on the question they answer in
  `docs/open-questions.md` — quoted, dated, marked
  as from a comment. No Part 3 section: Part 3 is the text's history. A comment that
  contradicts built code is a `defects.md` row.
- **FSD and matrix revisions** append a section to
  `docs/project.md` **Part 3**, in the shape the existing
  sections use: the short version, the numbered categories, how the comparison was
  produced. **Part 3 keeps only the latest comparison per source**: move the one it
  replaces, verbatim, to the top of
  `docs/archive/requirements-history.md`
  in the same change.
- **QA artifact and FE integration bug changes do not go in Part 3** — they are not
  requirements. Each produces one of: a **question** in `open-questions.md` (it states a
  rule the FSD does not); a **note on the feature's plan** (confirmed by the FSD, and it
  adds a test worth having); a **`defects.md` row** for an FE-reported bug confirmed
  against our code (a person triages each entry); or **nothing**.
- **Product Q&A changes** that answer an open question move it to *Resolved* with the
  date and the quoted answer.

**Each question's State**, where the ledger keeps them (a Book from 1.6: the *Questions* rules in
`.claude/book/docs.md`): from the threads read this run, propose each live question's next State —
`OPEN · NOT POSTED` (no thread), `OPEN · POSTED` (a thread, no answer: **Posted** is its date and id),
`ANSWERED · THREAD ONLY` (answered in the thread, not in the FSD text: **Answered** is the date and the role;
it moves under *Answered, waiting for the FSD text*), or `RESOLVED` (the highest revision's text says it:
**In FSD text** is `V<n> §x`; it moves to the archive with one line under *Resolved*). A question with no
State line gets one. Show every proposal and write them only on the person's word; then list **what to
post** (NOT POSTED questions), **what to ask the BA to add to the text** (THREAD ONLY) and **which threads
to resolve** (RESOLVED with **Thread resolved:** no) — posting and resolving nothing yourself.

Then check what any change lands on: **an open question now answered** — move it (the
highest-value outcome of the skill); **a plan built on a changed section** — flag it,
do not rewrite it in this pass; **a contradiction with built code** — a finding against
the code or a new question, **never against the PDF**; **the delivery schedule**, if
scope moved.

---

## Rules

**Never edit anything in `requirements/`.** Add a new snapshot; change nothing already
there. Two exceptions: a tracker's current copy, replaced at capture after its predecessor
moves into `backup/` (Phase 4 — the guard names those files exactly); and the
`read-me.txt` files, in two places: a link in the root file's *LINKS*, when the
link itself changes, and a folder's one **`Last checked:`** line, which each run
**overwrites** with its date and outcome — captured `V<n>`; unchanged; moved, not
captured (with what moved, and the `modifiedTime` left at the last capture's); or could
not check. A check that found nothing leaves only that line and the commit. **Never
append a dated note** — what a revision changed goes in Part 3, what a
comment answered goes on its question.

**A design showing something the FSD does not specify is not a requirement.**

**Where the FSD contradicts itself**, precedence does not help: a question for
`open-questions.md`.

---

## Report

1. **Which sources were checked**, and which could not be reached — and why
2. **The fingerprint** per source — ours versus current
3. **Moved or not.** If nothing moved, stop here
4. **What changed**, in the four categories, with section numbers
4a. **What the comment threads say** — threads new or replied-to since the last run,
    and which questions they answer. "No new threads" is a result; "did not read them"
    is not an option
5. **What it lands on** — questions answered, plans affected, contradictions with built
   code, schedule impact; the States proposed, and what to post, ask to add or resolve
6. **What was captured** — new filenames, and the Part 3 section added

---

## `all` — every source, verdict first

When the question is "is everything current" — and as the weekly sweep:

1. **Run `requirements status`, then the phases for every source it marks *needs a live
   check*** — not a subset picked in advance. Its own verdict is never the answer: it read
   only the repository. Unreachable sources are reported to the person before anything is
   captured or recorded, per *Blocked means stop*. A source it lists as `not configured`
   (a `<link>` placeholder) has no live link: report it as `no live link — nothing to
   check` (with the person to supply one if its folder holds snapshots); it counts in
   neither `STALE` nor `COULD NOT VERIFY`, nor does `none`, `not shared` or `not set up`.
2. **Lead with one verdict line**, before the report, once every live check is done:
   - **`UP TO DATE`** — every source was read and matched its snapshot.
   - **`STALE — <n> source(s) moved`** — name them.
   - **`COULD NOT VERIFY — <n> source(s) unreachable`** — name them and why. **Never
     round this down to `UP TO DATE`.**

   In more than one bucket: lead with the worse. `STALE` and `COULD NOT VERIFY` both
   outrank `UP TO DATE`.
3. **Then the full report** — the verdict is a top line, not a replacement.
4. **A changed FSD section**: `/book:impact` on that section names the modules, plans and
   tests it lands on; a change no plan covers is a new item.

---

## What next

- A changed FSD section: `/book:impact` on it; a plan built on it is flagged, not rewritten here.
- Captures or records made: commit them on the general-refresh branch; its pull request opens
  only when the person asks.
- The whole knowledge base must follow a new revision: `/book:sync-sources`.
- **In a flow** (`/book:flow`): `weekly-sweep` → `/book:progress`; `new-fsd-revision` → `/book:impact`; `answers-arrived` → `/book:sync-sources`; `qa-artifacts-changed` → `/book:raise`; `new-feature` → `/book:plan`; `spec-says-x` → `/book:fact-check`; `after-merge` → done; `qa-build` → `/book:progress`; `new-project` → the `new-feature` flow.
