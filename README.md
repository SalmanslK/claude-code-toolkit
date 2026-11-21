# Claude skills

Personal Claude Code skills. Copy a folder into `~/.claude/skills/` (or a project's `.claude/skills/`) to use it.

| Skill | What it does |
|---|---|
| `estimating-ai-assisted-work` | Effort estimates, ranges and buffers for teams that build with AI tools, calibrated from measured git history |
| `daily-scrum-updates` | Private standup log rebuilt from Git history and Claude session transcripts |
| `team-daily-activity` | What each developer did on a given day or week, from Git |
| `backend-development-history` | Delivery timeline of a backend repository from inception to today |
| `pending-work-items` | One private tracker per project of asks of people, pending decisions and outside dependencies |
| `requirements-docs-code-sync` | Bring requirements, docs and code back into agreement in one pass |
| `role-permissions-matrix`, `update-erd`, `docs-harmonizer` | Audit role permissions, keep the ERD true, unify docs |
| `drive-organizer` | Audit and organize a drive or folders safely |
| `code-review`, `create-pr`, `push`, `process-ticket` | Generic review, PR, safe-push and ticket workflows |

**The Book's skills live elsewhere.** Commit, review, impact, requirements, docs and delivery skills
(`/book:self-review`, `/book:check-sources`, …) are the [book plugin](https://github.com/SalmanslK/book-plugin);
the FE-guide and deploy skills come with the [Book boilerplate](https://github.com/SalmanslK/book-boilerplate)'s
packs; the Factory is [ai-factory-kit](https://github.com/SalmanslK/ai-factory-kit). Their earlier copies were
here until 21 Nov 2026.

Client-specific skills, calibration data and team rosters are deliberately not here.

## Prompts

[`prompts/reusable-prompts.md`](prompts/reusable-prompts.md) — 106 reusable prompts for C# engineers (issue
resolution, code review, documentation, architecture, testing, database, deployment and more).
