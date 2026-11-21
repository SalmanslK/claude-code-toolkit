---
name: write-for
description: >
  Use when someone needs a short message for a named non-engineer — "write this up for the PM", "explain
  it to the client", "a note for the QA lead". The answer first, at most five plain points, no
  unexplained id or term. Drafts only; never sends. Not for docs in the repository or a build's release
  notes.
allowed-tools: Read, Grep, Glob, Bash(git log*), Bash(git show*), Bash(git diff*)
---

You are writing **a short message for one reader who is not an engineer**: a project manager, the
client, a QA lead. The rule is the one in `CLAUDE.md`, *Write for the reader*: answer first, then only
what they need.

**You draft. You never send, post, email or comment.** The person copies it where it goes.

---

## Step 1 — Who, and what they need

- **The reader:** given as the argument (`/book:write-for the client`). Not given: ask who it is for, and
  what they will do with it (decide, approve, plan, test).
- **The subject:** what the person asked about, or the work of this session. Not clear: ask, in one
  question.

## Step 2 — Get the facts from their owners

Read only what the message needs, from the document that owns each fact (the table in `CLAUDE.md`,
*Where knowledge lives*): status from `docs/project.md` and the plans' Tasks, decisions from *Resolved*
in `docs/open-questions.md`, defects from `docs/defects.md`. A fact from the conversation alone is said
to be unconfirmed, or left out.

**What you could not confirm, you say** in the draft's last line, never smooth over.

## Step 3 — The draft

- **The answer first**, in one sentence: what is done, what is decided, what is needed from them.
- **Then at most five points**, each one line, in plain words.
- **No id, file path, branch or term left unexplained.** `Q12` becomes *the open question about
  discounts*; *migration* becomes *the database change*. A date is a date, not *next sprint*.
- **One ask, if there is one**, stated plainly with when it is needed.
- **Never in it:** credentials, hosts, personal data, another person's email, internal-only notes (a
  defect's root cause in the code, reviewer comments, estimates the reader was not given).
- Match the reader's language and register; keep it short enough to read on a phone.

Show the draft, then a one-line list of what it rests on (the owners you read) so the person can check
it.

## What next

- The person wants it sharper or shorter: redraft; never add points to fill.
- It revealed a decision nobody has recorded: it belongs under *Resolved* in `docs/open-questions.md`
  once made, or as an open question with a recommendation.
- A whole QA build to describe: **`/release-notes <build>`** where the fe-guides pack is installed.
- **In a flow** (`/book:flow`): `spec-says-x` → done; `guides-drift` → done; `qa-build` → done; `status-report` → done.
