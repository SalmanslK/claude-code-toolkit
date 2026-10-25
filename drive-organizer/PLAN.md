# Drive Organization Plan (the process we followed, as a checklist)

Time on a typical drive: 1-2 hours of conversation, mostly approvals.
Order matters: **repos and tooling first (to know what must not move), personal/work files next, user folders last.**

## 0. Prepare
- [ ] Install the skill: copy this folder to `~/.claude/skills/drive-organizer/`.
- [ ] Back up anything irreplaceable first (this process only moves files, but a backup is cheap).
- [ ] Decide scope: data drive (e.g. `D:\`) and/or `Desktop`, `Downloads`, `Documents`, `Pictures`, `Videos`.
- [ ] Run Claude Code from the drive root; paste the prompt from `PROMPT.md`.

## 1. Inventory (read-only)
- [ ] Top-level folders: file count, size, newest file.
- [ ] Git repos + worktrees (`Get-GitRoots`). A `.git` *file* = worktree: never move.
- [ ] Reparse points/junctions (`Get-ReparsePoints`): do not follow.
- [ ] Exact duplicates (`Find-DuplicateFiles`) in non-repo areas.
- [ ] Zips and what they were extracted to (`Compare-ZipToFolder`).
- [ ] Shortcuts that point into the drive (`Get-ShortcutTargets`).
- [ ] Empty folders (`Get-EmptyFolders`).
- [ ] Credential-looking files (names like `Cred*`, `*.PublishSettings`, `client_secret*`, `*recovery*`, `.env`).

## 2. Plan (needs your approval)
- [ ] `PLAN.md` in `_Drive-Audit-<date>\`: findings table, proposed structure, move/archive/leave list, risks.
- [ ] Agree the target structure and naming style. Default:
  `Work / Personal / Learning / Tools / Credentials / Archive / repos` (+ `Claude-Local` or other tool folders as they are).
- [ ] Agree what is left untouched (repos, worktrees, app folders, credentials).

## 3. Execute in small batches (log every batch with a category letter)
| Batch | What | Rule |
|---|---|---|
| A | Loose files in the drive root | Group into `Work\Reports`, `Work\Notes-Scripts`; leave `.editorconfig` |
| B | Small stray top-level folders | Merge into the matching home (`AI`, `Reusable Prompts` → `Learning`) |
| C | Technology/learning pile | `Books`, `Courses`, `Reference`, `Interview Prep`, `Notebooks`, `AI`; `Installers` → `Tools` |
| D | Personal loose files | By type: Pictures / Media / Documents / Receipts |
| E | Old stuff | → `Archive\<Name>-<Year>` (keep intact, don't split) |
| F | Duplicates and junk | → `To Delete - Review Before Deletion` with manifest |
| G | Consolidate | Fold work-related items out of Personal (contracts, invoices, appreciation) into `Work` |
| H | Descriptive names | Rename `New folder`, `ReviewFiles2` etc. only after looking inside |
| I | Credentials | One `.txt` per project; verify every value is present; originals → review folder |
| J | Desktop | Project folders/files → `Work`/`Learning`; keep app shortcuts; fix broken shortcuts |
| K | Downloads | Classify by name pattern + content peek; exact duplicates → review; ambiguous → `Work\Inbox` |
| L | Documents/Pictures/Videos | Leave app-managed folders; move user recordings/files to the drive |
| M | Inbox triage | Open each unknown file, classify, file; leftovers listed to you |
| N | Special cases | LocalDB `.mdf/.ldf` (drop via SQL, with approval), build output inside repos (report only) |

After each batch: show counts, any `SKIP`/`FAILED`, and ask before the next risky one.

## 4. Verify
- [ ] `Test-AuditLog`: all moves present, none left at origin, sizes match.
- [ ] `git worktree list` and `git status` unchanged in key repos.
- [ ] Open each Desktop shortcut target exists.
- [ ] Spot-check 5 random moved files open.

## 5. Report + your follow-ups
- [ ] `REPORT.md`: before/after, moved items, archives, deletion inventory, unresolved, statistics, next steps.
- [ ] You review `To Delete - Review Before Deletion`, then delete it yourself.
- [ ] Empty leftovers (`tmp`, review folder) – delete yourself if the tool is blocked.
- [ ] Move credentials into a password manager; rotate stale ones; delete the plain-text files.
- [ ] Back up the organized drive (external disk or cloud).

## What this found on the first run (for calibration)
| Finding | Count / size |
|---|---|
| Git repos (+3 worktrees linked both ways) | ~65, never moved |
| Exact duplicate files | ~50 (small), plus 3 redundant zips, 1 stale clone, 5 installers |
| Build output inside a repo (`PubTmp`) | 2.7 GB, moved to review |
| Stale LocalDB test databases | 38 DBs, 4.2 GB, dropped via SQL |
| Credential files | 14 → 2 |
| Downloads classified | 224 files (35 left in Inbox after triage) |
| Drive free space | 205 GB → 193 GB free of 261 (net: more data on D: after moving Desktop/Downloads in) |
