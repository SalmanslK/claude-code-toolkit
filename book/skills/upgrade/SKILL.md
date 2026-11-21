---
name: upgrade
description: >
  Use when a project's Book should move to a newer template release — "upgrade the Book", "take the new
  release". Runs the drift report, stops on conflicts, applies what the project never changed, carries
  the new settings by hand, then verify, review, local CI and the pull request. Not for a new Book or
  verifying one (/book:setup). Formerly /book-upgrade.
allowed-tools: Read, Grep, Glob, Bash(git status*), Bash(git log*), Bash(git diff*), Bash(git fetch*), Bash(git show*), Bash(git branch --show-current*), Bash(python devtools/book.py verify*), Bash(python devtools/factory/factory.py book verify*), Bash(python3 devtools/book.py verify*), Bash(python3 devtools/factory/factory.py book verify*), Bash(python devtools/checks/check-*), Bash(python3 devtools/checks/check-*), Bash(python devtools/checks/run-self-tests.py*), Bash(python3 devtools/checks/run-self-tests.py*), Bash(sh devtools/checks/ci-local.sh*)
---

# /book:upgrade — the project's Book, at the newer release

**A script compares; this skill decides with the person.** `book upgrade` (in the newer
template's checkout) says, for every file the template owns, whether the project can take the new
copy. This skill runs it, shows the person what it means, applies only what they approve, and carries
over by hand what the tool never writes. One project, one branch, one pull request.

*The Book's command is `book`: `python devtools/book.py <command>` from the project's root. On a Book before v1.4.0, which has no `devtools/book.py`, run `python devtools/factory/factory.py <command>`; `book verify`, `init` and `upgrade` are `factory.py book verify` and so on there.*

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

`book upgrade --apply` writes only `BEHIND` and `NEW` template files, and stamps
`book_version` in `devtools/factory/factory.toml`. **Everything else is this skill's to carry, by
hand, with the person:**

- **The project's settings.** A new release's new sections in `factory.toml` (an allow-list, a
  check's settings, a pack's `factory-append.toml`) are never added. Without them a new check fails
  on its first run. Read the release's notes and the template's
  `devtools/factory/book-template/skeletons/factory.toml.tmpl` and pack `factory-append.toml` for what is new; every allow-list
  entry gets its reason.
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

- **Ask** where the newer template's checkout is, and which release (`git tag` there). The
  checkout's tags rebuild the installed version, so it must hold `v<book_version>` too.
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
| `DROPPED` | the new template no longer has it | kept; the person deletes it or keeps it |
| `UNKNOWN` | no installed version to compare | kept; read its diff |
| `DECLINED` | in `[book] declined` | never written |

Show the person the counts, every `CONFLICT`, `REMOVED`, `DROPPED` and `UNKNOWN` file, and the diffs
of what would be written. **Then stop for their approval.**

**Read `REMOVED` twice.** A pack file whose path the template renames with the project's name, while
the project kept the old path, shows as `REMOVED` though it is there. Find it by content before
calling it deleted.

### 3. Apply, then carry over

```sh
python devtools/book.py upgrade --target <project> --apply
```

Then, on the branch, in reviewable commits:

1. the applied files, as the tool staged them;
2. each `CONFLICT`: the template's change merged into the project's copy, keeping the project's
   stricter lines; say which side won where they disagree;
3. the settings and document rules the tool never writes (above), each entry with its reason;
4. `book_version` already stamped by `--apply`: check it reads the new release.

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
