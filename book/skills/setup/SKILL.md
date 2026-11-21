---
name: setup
description: >
  Use to set up the Book in a new repository or to check an existing one is ready — "set up the Book
  here", "is this repo ready", "verify the Book". Asks the person for every answer, runs `factory book
  init` (creates only what is absent) and `factory book verify`, and reports READY, READY WITH GAPS or
  NOT READY. Not for taking a Book to a newer template (book:upgrade) or fixing what verify finds in the
  documents. Formerly /book-setup.
---

# /book:setup — a Book that is set up, or a list of what is not

**A script does the checking; this skill asks and decides.** `factory book verify` and
`factory book init` (`devtools/factory/book.py`) do the mechanical work. This skill gathers the answers
only a person can give, puts each one into the parameter file, and reports what the script found.
Nothing is guessed: an answer the person has not given stays an empty string, which leaves a
`<!-- FILL -->` slot that verify reports as `TO FILL`.

## Must never

- overwrite or "tidy" existing content — plans, ledgers, guides, `project.md` rows, snapshots;
  init reports an existing path as `KEPT` and leaves it, and upgrade writes only template files the
  project never changed;
- edit or delete anything already in `requirements/`;
- read, print or copy a private settings file, a credential store, `.env` or `~/.ssh` — verify
  reports private settings by key name, *set* or *not set*, and nothing else;
- put a token, an account password, a person's email or a home-folder path in the repository;
- create, rename, trash or share a Drive folder or Doc; post to Jira, Bitbucket or the FSD; change
  branch protection — say what a person must do instead;
- set the guard to `warn`, edit `settings.local.json`, point `core.hooksPath` anywhere but
  `.githooks`, or skip hooks;
- commit to a protected branch — work on `chore/book-setup-<slug>`, cut from the base with `--no-track`;
- delete a branch, or a file this run did not create;
- report a check that could not run as passed — `COULD NOT CHECK` is written as it is.

## Steps

### 1. Verify first, always

```sh
python3 devtools/factory/factory.py book verify
```

Read-only. One line per element (`OK`, `MISSING`, `WRONG <why>`, `TO FILL <slot>`,
`COULD NOT CHECK <why>`, `N/A`), then the existing checks it calls, then a verdict. It takes a few
minutes because it runs the self-test suites; `--no-self-tests` is faster but then cannot say READY.
If the verdict is **READY**, say so and stop at *What next*. For another repository, run that
repository's own copy of the command — only its own run can say whether its private settings are set.

### 2. Greenfield or brownfield

Ask which, unless it is plain: a repository with no `CLAUDE.md` and no `docs/` is greenfield.

| | Greenfield (new repository) | Brownfield (existing repository) |
|---|---|---|
| Files | init copies the template's files and writes skeletons | init creates only what is missing; everything present is `KEPT` and its findings become a punch list |
| Owners | from the template | `check-book.py` lists unowned documents; propose an owner or a move to `docs/archive/` for each, and the person approves each one |
| History | empty archive files | dated logs in live documents move to the archive through `/book:trim`, one approved change at a time |
| `requirements/` | folders, read-mes, the index; the first FSD filed as V1 | existing documents filed as snapshots **as they are** — no renames of tracked files |
| Hooks and guard | switched on at init | switched on **last**, after the clean-up, so the guard does not refuse it; then a full verify |
| Pace | one setup pull request | staged, one pull request each: (1) hygiene files, (2) owners and archive, (3) requirements index, (4) hooks on |

### 3. Ask for each answer

Ask in plain words, one at a time, and write each into `book.toml` at the repository root under
`[book]` (init refuses a file that lacks any of them):

| Key | Ask |
|---|---|
| `name`, `slug`, `env_prefix` | The product's name in PascalCase (dotted parts allowed: `Example.Shop`), its lower-case slug, its environment-variable prefix (`EXAMPLE_`) |
| `title` | The product's title as the documents' headings carry it (`Example Shop`): letters, digits, spaces, dots and hyphens |
| `stack` | `dotnet` (the template's stack pack) or `none` |
| `mode` | `greenfield` or `brownfield` (step 2) |
| `base_branch`, `protected_branches` | The integration branch, and every branch reached only by promotion |
| `git_host`, `ci_live` | Bitbucket or another host; whether CI runs today (if not, the local CI gate is required) |
| `owners` | The AI-file owners: **each person runs `factory pr whoami` themselves** and gives their account id. Written `owners = [{ name = "A Person", account_id = "<id>" }]`, one table per owner, or `[]` |
| `jira_site`, `jira_key` | The Jira site and project key, or empty for no tracker |
| `fsd_label`, `fsd_link` | The FSD's label in the index (`FSD`) and its live Google Doc link |
| `fe_drive_folder_id` | The FE team's **existing** Drive folder, from its link — never created here |

Also ask, and record in the documents after init rather than in `book.toml`: the other requirement
sources and their links (`requirements/read-me.txt`; a source delivered as files, with nothing to fetch,
goes under NO LIVE LINK and needs no read-me), the snapshot folders besides the FSD
(`[requirements.sources] snapshot_dirs`), the phase-table columns and the open-question recommendation
heading if they differ from the defaults (`[book]`), the exact tracker paths for
`[guard] read_only_maintained`, DEV and QA targets (`[deploy]`, DEV and QA only), and the modules
(`[[modules]]`). `book.toml` holds no secret, and leaves with the setup pull request, or is deleted
once the person agrees it served its purpose.

### 4. Init

On a work branch cut with `--no-track`:

```sh
python3 devtools/factory/factory.py book init --params book.toml
```

It copies the template's files with the names replaced, writes skeletons with `<!-- FILL -->` slots,
keeps empty folders with `.gitkeep`, stages exactly what it created, switches the hooks on
(greenfield), regenerates the rules table, then runs verify. Run it again at any time: it creates
nothing that exists. A template other than this repository's is the template's own
`factory.py book init --target <this repo>`. Init writes the template version into `factory.toml`
`book_version`, which upgrade reads.

### 5. Upgrade, when a newer template is out

Not here: **`/book:upgrade`** takes a Book to a newer template (the drift report, the person's call on
each conflict, the apply, verify, review and the pull request). Say so, and stop at verify.

### 6. Report

Lead with the verdict. Then, grouped for the person:

- **What a person must do** — every `TO FILL`, and the `CONFIRM` line (the AI-file owners as
  default reviewers on the base branch, in the Git host's settings);
- **What is wrong** — every `MISSING` and `WRONG`, each with the owner document or skill that fixes it;
- **What could not be checked** — every `COULD NOT CHECK`, with what would let it run (`git fetch
  origin`, the self-tests, that repository's own run).

In brownfield, turn the `WRONG` lines into the punch list for the next stage; never fix existing
documents in this run. Commit what init created with an imperative message; open a pull request only
when the person asks.

## What next

- **READY** — start real work: a feature's plan (`/book:plan`) and its row in
  `docs/project.md`; `/book:check-sources all` before the first estimate.
- **READY WITH GAPS** — fill the slots verify lists (the FSD link and V1 snapshot, the owners, the
  Drive folder), then verify again.
- **NOT READY** — work the list from the top, one pull request per stage, and verify after each;
  the verdict should rise each time.
- **In a flow** (`/book:flow`): `new-project` → `/book:check-sources`.
