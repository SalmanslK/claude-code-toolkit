# Research cross-check

**Last refreshed:** 2026-10. If this is more than 6 months old, run fresh web searches (AI coding productivity studies, METR, DORA State of AI-assisted Software Development) and update this file before relying on it.

| Source | Finding | Use in an estimate |
|---|---|---|
| University of Chicago study of Cursor's agent, 24 organizations (vendor-published) | +39% merged PRs once the agent was the default; no rise in revert rate | Best measured team-level throughput gain is about 1.4× |
| McKinsey survey, about 4,500 developers | About 46% less time on routine coding; excludes system design, complex debugging and unfamiliar code | Gains concentrate in CRUD and boilerplate |
| METR randomized trial, 2025 | Experienced developers on mature open-source codebases were 19% slower with AI, while believing they were faster | No proven speedup on complex brownfield work |
| METR follow-up, 2026 | Inconclusive (confidence intervals cross zero); METR called its own data unreliable because developers refused to work without AI | Treat speedup claims on complex work as unproven |
| DORA 2025, about 5,000 respondents | AI adoption tracks higher throughput and also more change failures and rework | Keep rework buffers; fast builds bring more defect rounds |

## How to apply

- **Team measured beyond these gains** (Tier A or B): keep the measured costs. The research does not justify cutting further.
- **Team with no measurement** (Tier C): the class-specific AI factors in `conventional-baselines.md` are consistent with these findings.
- **The research supports buffers, not a smaller base.** Rework rises with speed.

## Sources

- [Cursor: the productivity impact of coding agents](https://cursor.com/cn/blog/topic/research)
- [LeadDev: Cursor productivity claims](https://leaddev.com/ai/cursor-claims-its-tools-are-a-massive-productivity-hack-for-devs)
- [Fungies: AI coding assistant productivity statistics 2026](https://fungies.io/ai-coding-assistant-productivity-statistics-2026/)
- [CO/AI: METR, experienced developers 19% slower](https://getcoai.com/news/study-ai-coding-tools-slow-down-experienced-developers-by-19/)
- [CoderCops: METR 2026](https://blog.codercops.com/blog/ai-coding-productivity-2x-not-10x-metr-2026)
- [Splunk: DORA 2025 review](https://www.splunk.com/en_us/blog/learn/state-of-devops)
- [RedMonk: DORA 2025](https://redmonk.com/rstephens/2025/12/18/dora2025/)
- [Thoughtworks: DORA 2025](https://www.thoughtworks.com/en-cn/insights/articles/the-dora-report-2025--a-thoughtworks-perspective)
