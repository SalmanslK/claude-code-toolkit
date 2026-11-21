# Shared mechanics: the three standup and history skills

daily-scrum-updates, team-daily-activity and backend-development-history all use what is on this page.
It is the one owner of these rules. A skill links here; it does not restate them.

## 1. The private-file rule

The logs are the user's private data, not project documents.

- Never `git add`, `commit`, `push` or `rm` a log, never gitignore one, and never create one inside a
  working tree. Writing a log is a plain file write.
- If the script prints `BLOCK`, the output folder is inside a repository or worktree. Stop, tell the user,
  and write nothing.
- Every git command is read-only. The script enforces this with an allow-list. Never `fetch`, `pull` or
  `checkout`. If the clone looks stale, say so and let the user refresh it.
- Never copy a host, IP address, port, path, credential or `.env` value out of a transcript.

## 2. Configuration: `~/.claude/daily-scrum-updates/config.json`

The user edits this file. Change a key only when the user asks, keep every other key, and never add a
person's email on your own.

| Key | Default | Used by |
|---|---|---|
| `directory` | `~/.claude/daily-scrum-updates` (`~` and `{project}` expanded) | all three |
| `workingDays`, `holidays` | Mon–Fri, none (ISO dates) | scrum, team |
| `projectNames` | repo folder name (the main repo's name, even in a worktree) | all three |
| `authors` | none: email → display name, for aliases and order | team, history, scrum (aliases) |
| `utcOffset` | `+05:00` (PKT). **The one place the timezone is set** | all three |
| `deployment.integrationBranch` | `dev` | team, history |
| `deployment.mergeDeploysTo` | `null`: a merge proves nothing about an environment | history |
| `backupDirectory` | `null`: skip. When set, copy each log you wrote there after writing | all three |

A one-off `dir=<path>` from the user becomes `--dir <path>` for that run only.

## 3. The script

```bash
python ~/.claude/skills/daily-scrum-updates/scripts/standup_evidence.py <command> ...
```

Run it from the repository. It prints structured text and writes nothing. Its docstring lists safeguards
S1–S23, and `test_standup_evidence.py` beside it proves each one:

```bash
python -m unittest discover -s ~/.claude/skills/daily-scrum-updates/scripts -p "test_*.py"
```

| Command | Prints |
|---|---|
| `status --log scrum\|team\|history` | file paths, entries, last date, missing working days, transcripts present, known devs and unmapped authors (team), scan state (history) |
| `dates --log scrum\|team [SPEC]` | the days a run covers, with working or not, existing or provisional, future |
| `evidence --log scrum\|team [SPEC]` | per day: `=== DATE (...) -> ACTION`, then the evidence |
| `has-entry --log scrum\|team DATE` | `ABSENT`, `EXISTS` or `PROVISIONAL`. Run it immediately before each write (concurrent runs) |
| `merges [--since D] [--until D]` | PR merges on the integration branch's first-parent line, with author by count and merger |
| `pr-authors MERGE [PATH ...]` | commit share per author inside one PR, scoped to paths if given; `listed (>=20%)` |
| `deploys [--since ISO]` | the deployment ledger from this machine's deploy transcripts |

SPEC: nothing (fill missing; first run is the last 5 working days), `today`, `yesterday`, `tomorrow`,
`YYYY-MM-DD`, `MM-DD-YYYY`, `Sep 8`, `this week`, `last week`, `this month`, `backfill`, `backfill N`,
`backfill A..B`. Transcript text is capped and every cut is marked. Use `--full` to lift the caps.

## 4. Reading the ACTION on each day

| ACTION | Do |
|---|---|
| `WRITE` | Write the entry from the evidence |
| `WRITE (provisional ...)` | team only: write it with the `MARKER` line the script prints as its first line |
| `REPLACE the provisional section` | team only: replace that section whole. Once the day is over, drop the marker |
| `EXISTS - authoritative` | Do not touch it. If the evidence says it is wrong or incomplete, report that and ask |
| `NO EVIDENCE` | scrum: one bullet saying the day could not be reconstructed. team: the date with everyone under `_No activity:_` |
| `SKIP ...` | Nothing to write and nothing to report |
| `FUTURE` | Write only a plan the user stated inline, marked as planned |
| `ANNOUNCE` (backfill) | Tell the user the exact range and wait for a go-ahead before writing |
| `NOTE interpreted ...` | Say the interpretation back in the report |
| `UNMAPPED` | Report the suggested `authors` line. Never edit the map yourself |

## 5. What the evidence lines mean

- **Commit placement**: `landed by PR #N on <date>`, `direct to dev, no PR`, or `open on <branch>`, and
  whether the commit was in the integration branch **by the end of that day**. Work open at the end of the
  day is in progress, even if it merged later. "Not yet merged" is provable from Git. "No PR yet" is not.
- **PR lines**: the author is the email with the most commits in the PR. `%ae disagrees` means the count
  won. `TIE` means you weigh which side carries the feature. `merged by` is the person who clicked merge.
  `your role: unknown` means you ask the user before choosing a verb.
- **BRANCH REFRESHES ignored** counts merges like "Merge branch 'dev' into feature/x". They are never work.
- **Ids are read as of the commit**: describe a `D`/`Q` id from `git show <sha>:docs/defects.md` (or the
  questions file), never from the working tree. Ids get renumbered when two branches claim one number.
- **Sessions** (scrum only): the user's prompts (`>`), the last assistant text of that day (`<`), the
  branch and the title. Only what the user landed on is an update, not drafts or dead ends.

## 6. Known limits

- Transcripts are local to this machine and this install. A session on another machine, a cloud session or
  another clone path is invisible to them. Git has no such gap. A thin day reconstructed from Git alone may
  be this limit, so say so.
- PR merges are recognised in Bitbucket's and GitHub's merge-commit wording. A squash or rebase merge
  leaves no merge commit, so it shows as a commit placed `direct to dev, no PR`.
