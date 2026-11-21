# Claude skills

Every Claude Code skill and agent I use, in one place, current. Copy a folder into `~/.claude/skills/`
(an agent file into `~/.claude/agents/`), or a project's `.claude/`, to use it.

## Personal skills (root)

Maintained here. The installed copies in `~/.claude/skills/` are the working copies; copy them back here
after a change, with client names and client data left out.

| Skill | What it does |
|---|---|
| `estimating-ai-assisted-work` | Effort estimates, ranges and buffers for teams that build with AI tools, calibrated from measured git history |
| `daily-scrum-updates` | Private standup log rebuilt from Git history and Claude session transcripts |
| `team-daily-activity` | What each developer did on a given day or week, from Git |
| `backend-development-history` | Delivery timeline of a backend repository from inception to today |
| `pending-work-items` | One private tracker per project of asks of people, pending decisions and outside dependencies |
| `drive-organizer` | Audit and organize a drive or folders safely |

## Generic skills (root)

For projects that do not use the Book; a Book project uses the Book skill named beside each.

| Skill | What it does | In a Book project |
|---|---|---|
| `code-review` | Review a branch, diff or PR by severity, read-only | `/book:self-review`, `/book:peer-review` |
| `create-pr`, `push` | Open a PR from the commits; push safely, never force | `/book:ship` |
| `process-ticket` | Ticket → plan → branch, code and tests → ready for review | `/book:flow build-task` |
| `docs-harmonizer` | One voice across documents: duplication, contradictions, terms | `/book:check-consistency` |
| `update-erd` | Bring the ERD in line after a schema change | the dotnet pack's `gen-database-erd.py` |
| `requirements-docs-code-sync` | One end-to-end pass: requirements → docs → code | `/book:sync-sources` |
| `role-permissions-matrix` | Build the role × action matrix and audit what the code enforces | — |

## Agents (`agents/`)

Nine role agents: solution architect, build and DevOps, code reviewer, data and persistence, .NET backend,
integration and debugging, project manager, React front end, tester. Maintained here; installed in
`~/.claude/agents/`.

## The Book's skills (`book/`)

**A copy.** They are maintained in their own repositories and copied here at each release:

| Folder | What | Maintained in |
|---|---|---|
| `book/skills/`, `book/agents/` | The book plugin's 21 skills (`/book:flow`, `/book:self-review`, `/book:check-permissions`, …) and its 2 agents — v0.4.0 | [book-plugin](https://github.com/SalmanslK/book-plugin) |
| `book/packs/fe-guides/`, `book/packs/deploy/` | The packs' skills: `/check-guides`, `/publish-guides`, `/release-notes`, `/deploy` — boilerplate v1.3.2 | [book-boilerplate](https://github.com/SalmanslK/book-boilerplate) |
| `factory/` | The Factory skill, which builds a new Book | [ai-factory-kit](https://github.com/SalmanslK/ai-factory-kit) |

Change them there, not here, or the next copy overwrites the change. To use them, install the plugin
(`claude plugin marketplace add SalmanslK/book-plugin`) rather than copying folders.

Client-specific data (calibration sets, estimate registers, team rosters) is deliberately not here.

## Prompts

[`prompts/reusable-prompts.md`](prompts/reusable-prompts.md) — 106 reusable prompts for C# engineers (issue
resolution, code review, documentation, architecture, testing, database, deployment and more).
