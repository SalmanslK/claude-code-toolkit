---
name: pending-work-items
description: Use when the user asks to create, update or check a project's private tracker of asks and decisions — "create the pending items file", "update the tracker", "what are we waiting on", "who owes us what", "mark X done in the tracker" — or after a run of merges when it is stale. Keeps ONE private Markdown file per project, outside the repository, updated in place, holding only what the project's status documents cannot (asks of people, pending decisions, outside dependencies, the user's next steps) by owner, and linking to them for tasks. Not for remaining build tasks or feature status (the repository's Book answers "what is left": project-progress, the feature index, each plan's tasks), delivery history (backend-development-history) or a standup log (daily-scrum-updates).
---

You keep **one private tracker per project**: a single Markdown file, outside the repository, that holds what
the project's own documents cannot. That means asks of people, decisions waiting on someone, dependencies
outside the team, and the user's own next steps, grouped by who holds each one. It is the user's working
list, not a project document.

**Must hold (read first):**
- **The Book answers "what is left".** Where the repository keeps its status in a Book, that is the owner of
  remaining build work: in Book-style repositories, the feature index (`docs/project.md` Part 1), each
  plan's Tasks, and the generated *Open tasks* and *Task progress* tables, kept current by `/project-progress`.
  **Never copy a task, a feature status or a defect list into the tracker.** Link to the Book, and keep only
  the rows the Book has no place for (§What belongs here).
- **Outside the repository, never committed.** One file per project, no date in its name, updated in place.
- **Do not act on the list.** Updating it never posts, deploys, merges, opens a PR or messages anyone.

## What belongs here, and what does not

| Holds a row here | Not here: link instead |
|---|---|
| An **ask of a person**: a BA answer awaited, an owner's agreement, an IT or DevOps request, the FE or QA team adopting a change | A plan task, Built or open: the Book (plan Tasks, Open tasks table) |
| A **decision** waiting on someone, with who decides | A feature's status or phase: the Book (feature index) |
| An **outside dependency**: a mailbox, a server, a licence, a client document | A defect or open question's own status: the repository's defect and question logs. The row is the *ask* about it ("BA to answer Q53"), with the id |
| The **user's own next steps** that are not a plan task: a PR to open on their word, a deploy to schedule, a review to give | Work history and finished items: Git, PRs and the Book |
| A PR or branch **waiting on a person** (review, approval, the user's go-ahead) | The PR's content or test results |

A row is a **wait**, not a **job**. If the Book can hold it as a task, it belongs in the Book. Say so, and
leave it out of the tracker.

## The rules

1. **One file per project, updated in place until the project ends.** Never create a dated copy. The date
   lives in the line **"As of <weekday> <date>."** at the top. Change that line on every update.
2. **Open items only.** Delete a row the moment it is done. No strikethrough, no "Done" table, no story.
3. **Where the file goes:** `D:\Claude-Local\<Project>\<Project>-Pending-Action-Items.md` by default, or
   wherever the user names (say so). Look for an existing tracker first and reuse it. Never inside a
   repository; never staged, committed or pushed.
4. **The repository owns the facts; the tracker points at them.** Before keeping or adding a row, check it at
   its source: open questions, defects, plan tasks, open PRs, unmerged branches. A row you cannot verify
   stays only as *carried over — confirm*. Never invent a status.
5. **Group by who holds the item:** the user, each teammate, the BA, FE, DevOps or IT, QA. Number the rows
   within each group.
6. **No secrets, no personal data.** No tokens, passwords, connection strings, private-settings values or
   customer data. Refer to people by the names the project already uses.
7. **Report faithfully.** "Merged" or "CI passed" means you saw it. A check you could not make is
   "could not check", never "done".

## Modes

### Create (no file yet)

1. Find the project's root, README, `CLAUDE.md` and status docs. Find its Book: where "what is left" lives,
   and whether a generated Open tasks table exists. Ask only for what you cannot find, such as the owners or
   the folder.
2. Read the sources in rule 4. For a git project, run
   `git branch -r --no-merged origin/<integration branch>` and check open PRs and recent merges. Do not
   `git fetch` unless the user agrees: say if the clone looks stale.
3. Write the file from the template. **Where things stand** takes a few sentences and links the Book's
   Open tasks table for the remaining build work.
4. Show the path and a short summary, and list what you carried over unverified.

### Update (the file exists)

1. Read the whole file.
2. Reconcile each row against its source:
   - done: delete it;
   - changed: rewrite it;
   - blocked: say on what;
   - a new ask or decision from the conversation: add it under its owner.

   **A row that is really a task moves to the Book.** Say so, and remove it here once the Book has it. Remove
   any group that became empty.
3. Change **"As of"**, and refresh **Where things stand** and its link to the Book.
4. Keep the file's sections and wording, and do not reshuffle what did not change.
5. Report the delta: removed, added, changed, moved to the Book.

### Check ("what are we waiting on")

Read the file and verify the rows most likely to be stale against their sources. Answer briefly and plainly,
then:
- **Name every row you did not verify** ("not re-checked: …"), so a stale row is never presented as current.
- For **remaining build work**, answer from the Book (its Open tasks table, or `/project-progress` when it
  looks stale), and say that this is where the answer came from.

Offer an Update, but edit nothing unless asked.

## Writing the rows

- One line of state per row, in plain words, with the id or link that proves it (`Q53`, `D98`, `#189`, a
  branch, a plan task). Say what unblocks a blocked row.
- Keep the user's actions apart from the ones you can do. Anything that needs the user's permission is
  "waiting for your word", never "mine".
- Prefer the owner's current wording, and keep ids stable.

## Never

- Create a second or dated tracker, strike through done rows, or keep history in the file.
- Copy plan tasks, feature status or defect lists into it.
- Put the file in a repository, or stage, commit or push it.
- Mark anything done that you did not see done; invent an owner, an id or a date.
- Copy secrets or private settings into it.

## What next

- If the Book's Open tasks table looks stale, run **project-progress** in the repository.
- For a module's dates and deployments, use **backend-development-history**.
- For today's standup line, use **daily-scrum-updates**.
