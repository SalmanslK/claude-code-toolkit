# Claude skills

Personal Claude Code skills. Copy a folder into `~/.claude/skills/` (or a project's `.claude/skills/`) to use it.

| Skill | What it does |
|---|---|
| `estimating-ai-assisted-work` | Effort estimates, ranges and buffers for teams that build with AI tools, calibrated from measured git history |
| `daily-scrum-updates` | Private standup log rebuilt from Git history and Claude session transcripts |
| `team-daily-activity` | What each developer did on a given day or week, from Git |
| `backend-development-history` | Delivery timeline of a backend repository from inception to today |
| `pending-work-items` | One private tracker per project of asks of people, pending decisions and outside dependencies |
| `role-permissions-matrix` | Build the role × action matrix from the requirements and audit what the code enforces |
| `drive-organizer` | Audit and organize a drive or folders safely |

**The Book's skills live elsewhere.** Commit, review, impact, requirements, docs and delivery skills
(`/book:self-review`, `/book:check-sources`, …) are the [book plugin](https://github.com/SalmanslK/book-plugin);
the FE-guide and deploy skills come with the [Book boilerplate](https://github.com/SalmanslK/book-boilerplate)'s
packs; the Factory is [ai-factory-kit](https://github.com/SalmanslK/ai-factory-kit). Their earlier copies were
here until 21 Nov 2026, with these generic ones the Book now covers:

| Removed | Use instead |
|---|---|
| `code-review` | `/book:self-review` (your branch), `/book:peer-review` (a teammate's PR) |
| `create-pr`, `push` | `/book:ship` (local CI, description, push and PR); the Book's guard refuses unsafe pushes |
| `process-ticket` | `/book:flow build-task`, after `/book:plan` |
| `docs-harmonizer` | `/book:check-consistency` |
| `update-erd` | the boilerplate dotnet pack's `gen-database-erd.py`, checked in CI |
| `requirements-docs-code-sync` | `/book:sync-sources` |

Client-specific skills, calibration data and team rosters are deliberately not here.

## Prompts

[`prompts/reusable-prompts.md`](prompts/reusable-prompts.md) — 106 reusable prompts for C# engineers (issue
resolution, code review, documentation, architecture, testing, database, deployment and more).
