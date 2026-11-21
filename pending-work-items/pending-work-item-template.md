# <Project> — What we are waiting on

**As of <Weekday> <YYYY-MM-DD>.** Open asks, decisions and dependencies only. Finished items are not listed. A private file, **updated in place: this is the one tracker until the end of the project** (no new file per day; change the "As of" date instead).

**What is left to build is not here.** The repository's Book owns it: <the feature index, e.g. `docs/project.md` Part 1> and each plan's Tasks, with the generated **Open tasks** table (<link or path>), kept current by `/project-progress`. This file holds only what the Book has no place for. Re-check a line at its source (<the defect log, open questions, PRs>) before acting on it.

**Where things stand:** <Three or four sentences. What is merged and where (branch / last PR number). What is deployed to each environment and at which commit. The Book's headline, e.g. "Phase 3: 4 of 6 features built; see Open tasks". The one or two waits that decide the schedule.>

**Schedule:** <Release 1 to <date> · go-live <date>> (<where the release plan lives>).

Who: **<Owner A>** (<area>), **<Owner B>** (<area>), the **BA** (<how they answer>), **FE**, **DevOps / IT**, **QA**. `Q` = open question, `D` = defect, `#` = pull request. <Add the project's other id prefixes.>

---

## 1. Waiting on the user's word

| # | Item | Notes |
|---|---|---|
| 1 | **<A PR to open, a deploy to schedule, a post to approve>** | <What is ready; what the user must say; the id or branch that proves it.> |

## 2. Pull requests and branches waiting on a person

| # | Item | Waiting on | Notes |
|---|---|---|---|
| 1 | **<PR or branch, in plain words>** | <Name> | <Review, approval or go-ahead; what unblocks it. Not the PR's content.> |

## 3. Decisions

| # | Decision | Who decides | Notes |
|---|---|---|---|
| 1 | **<The choice, in one line>** | <Owner / BA / client> | <Our recommendation and where it is written, e.g. the open-questions doc; what waits on it.> |

## 4. The BA and questions

Questions are posted as comments in <where> by whoever owns the topic; the BA answers there. **<Rule about who may post, e.g. nothing is posted without the user's word in that turn.>**

| Who | Ask | Notes |
|---|---|---|
| **<Owner>** | **<Q ids>** to post | <One line: what is asked.> |
| **BA** | **<Q ids>** to answer | <What is awaited, and what it blocks (link the plan task, do not copy it).> |

## 5. Others: outside dependencies

| Who | Ask | State |
|---|---|---|
| **IT / DevOps** | **<Item>** | <What is needed, by when, what it blocks.> |
| **FE** | **<Item>** | <The contract change they must adopt; link the FE guide.> |
| **QA** | **<Item>** | <Cases to rewrite or a status to set.> |

## 6. On hold

- **Blocked until <X> exists:** <the ask that unblocks it, and who holds it>.
- **Accepted gaps:** <ids, and where the acceptance is recorded>.
