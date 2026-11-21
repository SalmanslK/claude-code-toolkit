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
| `fe-guides-publish`, `role-permissions-matrix`, `update-erd`, `docs-harmonizer` | Publish integration guides, audit role permissions, keep the ERD true, unify docs |
| `drive-organizer` | Audit and organize a drive or folders safely |
| `code-review`, `create-pr`, `push`, `process-ticket` | Generic review, PR, safe-push and ticket workflows |
| `commit`, `review-branch`, `review-pr`, `change-impact` | Commit, branch/PR review and impact analysis (use with the Book boilerplate) |
| `docs-consistency`, `docs-trim`, `docs-vs-code`, `docs-update-from-code`, `fsd-audit`, `requirements-check`, `requirements-sync`, `api-contract-draft`, `project-progress`, `deploy`, `factory` | The Book's documentation, requirements and delivery skills |

**The Book's skills have moved.** The `commit` … `factory` rows above are their earlier copies. The current
versions, renamed (`/book:self-review`, `/book:check-sources`, …) and kept up to date, are the
[book plugin](https://github.com/SalmanslK/book-plugin), used with the
[Book boilerplate](https://github.com/SalmanslK/book-boilerplate).

Client-specific skills, calibration data and team rosters are deliberately not here.

## Prompts

[`prompts/reusable-prompts.md`](prompts/reusable-prompts.md) — 106 reusable prompts for C# engineers (issue
resolution, code review, documentation, architecture, testing, database, deployment and more).
