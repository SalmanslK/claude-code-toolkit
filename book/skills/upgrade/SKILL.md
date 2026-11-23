---
name: upgrade
description: >
  Use when a project's Book should move to a newer template release — "upgrade the Book", "take the new
  release". Runs the drift report, stops on conflicts, applies what the project never changed, carries
  the new settings by hand, then verify, review, local CI and the pull request. Not for a new Book or
  verifying one (/book:setup). Formerly /book-upgrade.
allowed-tools: Read, Grep, Glob, Bash(git status*), Bash(git log*), Bash(git diff*), Bash(git fetch*), Bash(git show*), Bash(git branch --show-current*), Bash(python devtools/book.py verify*), Bash(python3 devtools/book.py verify*), Bash(python devtools/checks/check-*), Bash(python3 devtools/checks/check-*), Bash(python devtools/checks/run-self-tests.py*), Bash(python3 devtools/checks/run-self-tests.py*), Bash(sh devtools/checks/ci-local.sh*), Bash(python devtools/book.py upgrade*), Bash(python3 devtools/book.py upgrade*), Bash(python devtools/book.py defects*), Bash(python3 devtools/book.py defects*), Bash(python devtools/book.py requirements*), Bash(python3 devtools/book.py requirements*), Bash(git tag -l*), Bash(git tag --list*)
---

# /book:upgrade — the project's Book, at the newer release

**A script compares; this skill decides with the person.** `book upgrade` (in the newer
template's checkout) says, for every file the template owns, whether the project can take the new
copy. This skill runs it, shows the person what it means, applies only what they approve, and carries
over by hand what the tool never writes. One project, one branch, one pull request.

*The Book's command is `book`: `python devtools/book.py <command>` from the project's root.*

## Must never

- apply before the person has seen the report;
- overwrite a file the project changed (`CHANGED`, `CONFLICT`): the project's lines win, and the
  template's change is carried over by hand where it still applies;
- write a project's settings from another project's values, or copy a project's name, path or key
  into the template's files;
- edit `requirements/`, or a generated doc by hand;
- commit to a protected branch, skip hooks, or delete a branch;
- report a check that could not run as passed.

## What the tool never writes

`book upgrade --apply` writes the `BEHIND` and `NEW` template files, and stamps
`book_version` in `devtools/factory/factory.toml` once nothing is left to merge (step 3). Going to 1.6 it
also rewrites the project's own files once: every `CLAUDE.md` (the `SPLIT` lines), `factory.toml`, and
`devtools/factory/book-files.lock` ([Going to 1.6](#going-to-16)). **Everything else is this skill's to
carry, by hand, with the person:**

- **The project's settings.** From 1.6 the Book's defaults files (`devtools/factory/book-defaults*`)
  supply every new key and code rule, so `factory.toml` holds only the project's own values and
  exceptions; read the report's `CONFIRM factory.toml` lines for what the defaults add. Before 1.6, a
  new release's new sections (an allow-list, a check's settings, a pack's `factory-append.toml`) are
  never added, and a new check fails on its first run without them: read the release's notes and the
  template's `devtools/factory/book-template/skeletons/factory.toml.tmpl` for what is new. Every
  allow-list entry gets its reason.
- **The project's documents.** `docs/` (but the plan template) is the project's. A rule the release
  adds to `docs/CLAUDE.md` or another owner document shows up as a `CONFLICT` or not at all: add it by
  hand.
- **The move onto this plugin (template 1.3.0).** A Book from before it gets `WRONG` lines for each
  step: enable `book@book-plugins` in `.claude/settings.json` (a project-edited file is a `CONFLICT`);
  point `[review_scope]` at `book:peer-review/references/` and, for dotnet, `.claude/review/`; delete
  the old skill and agent files the plugin now provides, once it is enabled, carrying any local edit
  over first. Do all three in the upgrade's own commit.
- **Files the project keeps on purpose** (its own CI script, generator wording, a stricter check):
  they stay `CHANGED`. A pack file the project replaces with its own goes into `[book] declined`, so
  the report stops offering it.

## Steps

### 1. Before the report

- **Ask** where the newer template's checkout is, and which release (`git tag --list`, run in that
  checkout). The checkout's tags rebuild the installed version, so it must hold `v<book_version>` too.
- **Check the project can be compared:** `devtools/factory/factory.toml` has `[book] name`, `slug`
  and `env_prefix`, and a semver `book_version` (`1.2.8`). A Book installed before init wrote them
  needs them added first, set to the release it matches; a date-style version reads as newer than
  every release. It also needs `[book] stack` and `[book] packs` (what was installed): without them the
  upgrade compares no pack files and verify skips the pack checks.
- **Branch:** `chore/book-upgrade-<version>`, cut from the base with `--no-track`, holding nothing
  else. Check it before the first edit.

### 2. The report (read-only)

The person runs it from the template's checkout, or approves it in this session:

```sh
python devtools/book.py upgrade --target <project>
```

Each file the template owns gets one state:

| State | Means | Then |
|---|---|---|
| `CURRENT` | already the new copy | nothing |
| `BEHIND` | the project never changed it; the template did | `--apply` updates it |
| `NEW` | the template adds it | `--apply` creates it |
| `CHANGED` | the project's own edit; the template did not change it | kept |
| `CONFLICT` | both changed it | kept; the report shows the template's change to carry by hand |
| `REMOVED` | the project deleted it | left absent; confirm on purpose, or a renamed path (below) |
| `DROPPED` | the new template no longer has it | kept; the person reads why, then deletes it or keeps it |
| `RETIRED` | a file of the Book's own template copy (`devtools/factory/book-template/`), unchanged, that the new template dropped | `--apply` removes it, staged |
| `SPLIT` | a `CLAUDE.md` the Book owned before 1.6, the project's own from now on | kept, importing the Book's rules: never delete it |
| `UNKNOWN` | no installed version to compare | kept; read its diff |
| `DECLINED` | in `[book] declined` | never written |

Show the person the counts, every file under *For a person* (`CONFLICT`, `REMOVED`, `DROPPED`, `UNKNOWN`;
each is listed there once), and the report's *Diffs to decide on*. The diffs of the `BEHIND` and `NEW`
files, which `--apply` takes without a decision, are in the file the report names (`--diffs <path>`
chooses it): offer it, never paste it whole. **Then stop for their approval.**

**The old names' stubs.** Going to template 1.5.0 or later, each rename stub still under
`.claude/skills/` is `DROPPED`, and the report's note names the `/book:` skill each points at. The old
names stop working after this upgrade: delete those folders in the same pull request, and tell the team
the new names (the AI guide's *Old names* table lists them).

**Long-lived branches older than v1.4.0, going to 1.5.0.** Nothing to do first: never ask the person to
promote the base branch into `qa`, `uat` or `main` to take 1.5, which would release unfinished work. From
template 1.5.0 the pipelines' AI-files step judges a pull request into a branch whose Book is older than
v1.4.0 with that branch's own `factory.py`, as before, until a promotion brings it 1.5. The report names each
such protected branch for information; pass the note on and carry on.

**Read `REMOVED` twice.** A pack file whose path the template renames with the project's name, while
the project kept the old path, shows as `REMOVED` though it is there. Find it by content before
calling it deleted.

### Going to 1.6

From 1.6 the Book's rules and defaults live in the Book's own files, and the project's files hold only
what is the project's. The report's section *The 1.6 move* says what `--apply` will do, and its *Diffs to
decide on* show each `CLAUDE.md` and `factory.toml` before and after the move; walk the person through
both, file by file.

- **`SPLIT` lines.** Each `CLAUDE.md` (and, for dotnet, `src/CLAUDE.md` and the nested ones under
  `src/<Name>.API/` and `src/<Name>.Persistence/`) loses the blocks that are the Book's and gains an
  import of `.claude/book/`; the project's own blocks stay, under their headings. The nested files are
  the project's now: **never delete one**, or Claude Code stops loading the stack's rules there.
  `factory.toml` loses the keys equal to the defaults, and gains `[book] type_source_from` and, for
  each Book file the project changed, a `[book] drift_accepted` entry.
- **`CONFIRM` lines** are the person's, each one:
  - read what each `CLAUDE.md` keeps: a block that says a Book rule in other words repeats it;
  - a `factory.toml` comment the split kept, and each setting or code rule the project had removed that
    the defaults now give again (named on the run that splits the file: set it again in `factory.toml`,
    or switch a code rule off with `[[code_rules]]`, its `id` and `enabled = false`);
  - `python devtools/book.py defects classify`, then `--apply` once the person has read it: each open
    defect's Type and Source;
  - `python devtools/book.py requirements import`, then `--apply`, where the project has
    `docs/Audit/spec-traceability.md` and no register yet: the requirements register. Read its own CONFIRM
    lines (an id held twice, a pass section to merge into its modules, columns kept in the evidence
    appendix); it is not OK when an audit cell was lost or a link broke;
  - `python devtools/checks/check-rules.py --write`: the enforced-rules table, which now names the
    Book's rules files;
  - `/book:check-sources` once: each open question's State, proposed for the person to approve.
- **`[book] drift_accepted`.** A Book file the project changed is kept and listed there, so check-book
  warns rather than fails. Settle each entry in this pull request or the next: move the change to a
  setting (a project key wins; `[extend.<table>]` adds to a list) or to the project's `CLAUDE.md`, or
  list the file under `[book] declined` if the project owns it now (never a defaults file or a
  `.claude/book/` file: check-book fails such an entry); then take the entry out.
- **A `CONFLICT` is settled differently.** A Book file merged by hand that still differs from the
  Book's copy fails check-book's drift rule: carry the template's change, then move the project's
  change out as above, or keep it under `drift_accepted` with its reason until it moves.

### 3. Apply, then carry over

```sh
python devtools/book.py upgrade --target <project> --apply
```

Then, on the branch, in reviewable commits:

1. the applied files, as the tool staged them;
2. each `CONFLICT`: the template's change merged into the project's copy; say which side won where
   they disagree. Before 1.6, keep the project's stricter lines; from 1.6, a Book file that still
   differs fails check-book, so its change moves to a setting, `[book] declined` or
   `[book] drift_accepted` ([Going to 1.6](#going-to-16));
3. going to 1.6, each `CONFIRM` step of the report's *1.6 move*, in its own commit where it writes
   files (`defects classify --apply`, `requirements import --apply`, `check-rules.py --write`);
4. the settings and document rules the tool never writes (above), each entry with its reason;
5. `book_version`: `--apply` stamps the new release only once no `CONFLICT` or `REMOVED` file is left. Until
   then it keeps the installed one and lists those files in `[book] pending_merge`, which the report and
   `book verify` name: take each off the list once merged (or its absence settled), **keeping `[book]
   pending_merge_for` as it is** (without it the next run lists every file again), run `--apply` again, and
   check `book_version` reads the new release.

A project improvement found on the way, which belongs in the template, is listed for the template,
never written into it from here.

### 4. Prove it

```sh
python devtools/book.py verify
python devtools/checks/run-self-tests.py devtools/factory/hooks
python devtools/checks/run-self-tests.py devtools/factory
python devtools/checks/run-self-tests.py devtools/checks
```

`verify` reads READY (a `CONFIRM` line is a person's), and no suite skips a test or runs none.
Compare the test count with the base: a test class the project had must not disappear in the merge.
A failure is fixed on the branch, never skipped.

### 5. Review, local CI, the pull request

- **`/book:self-review` in a fresh context** (a subagent), never this session. A fix after it needs the
  checks again.
- **`sh devtools/checks/ci-local.sh`** on the last commit; paste its *Local CI* section.
- **The pull request:** `book pr open`, only when the person asks. Its description names the
  release, the counts from the report, every conflict and how it was resolved, the settings added by
  hand, and the *AI files* line (an upgrade changes the files that steer the AI, so an owner approves).

## Report

Lead with where the project is: the release it moved from and to, and READY or not. Then:

- **Done:** files updated and created, conflicts merged, settings and rules added by hand.
- **For the person:** what needs their decision (a `DROPPED` file, a `REMOVED` one, an owner's
  approval), and what could not be checked.
- **For the template:** anything found that belongs in the template, one line each.

## What next

- Merged: the next project, one pull request each.
- A new check reports findings in the project's own code: `/book:self-review`, or a `defects.md` row
  for a real defect.
- Something found belongs in the template: note it for the template's next release.
- **In a flow** (`/book:flow`): `upgrade-book` → `/book:self-review`.
