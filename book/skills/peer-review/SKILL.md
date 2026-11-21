---
name: peer-review
description: >
  Use when an open Bitbucket pull request needs reviewing — "/book:peer-review", "review PR #NN" — and
  the findings should be posted to it as inline comments after confirmation. Checks conformance to the
  FSD and our docs, then correctness. Never approves, merges, declines or edits a PR, and never prints
  the API token. Before a PR exists, use book:self-review. Formerly /review-pr.
---

Review the current pull request and **post the findings to it**.

> **`/book:self-review` and `/book:peer-review` are not the same thing.** `/book:self-review`
> reviews a branch locally before a PR exists and prints its verdict to the
> terminal. This one requires an open PR and writes to it. Use `/book:self-review`
> before opening; use this one after.

**Run it in a fresh session or a subagent, never in the session that wrote the change** (CLAUDE.md, Working with AI here).

**Arguments**

| | |
|---|---|
| *(none)* | Find the open PR whose source branch is the current branch |
| `pr=<id>` | Review that PR by number |
| `dry-run` | Do everything except post. Prints exactly what would be posted |

*The Book's command is `book`: `python devtools/book.py <command>` from the project's root. On a Book before v1.4.0, which has no `devtools/book.py`, run `python devtools/factory/factory.py <command>`; `book verify`, `init` and `upgrade` are `factory.py book verify` and so on there.*

---

## HARD LIMITS

**1. Never post without explicit confirmation.** Comments notify the whole
reviewer list, are attributed to the token's owner, and cannot be tidied away
cleanly on a 150-file diff. Present the findings, show the posting plan, and wait
for the user to say yes. `dry-run` is the only mode that skips the question,
because it skips the posting.

**2. Never approve, merge, decline, or edit the PR.** This skill posts comments
and nothing else. `POST .../approve`, `POST .../merge`, `POST .../decline` and any
`PUT` to the pull request are out of scope — refuse them even if asked mid-run,
and say that merging is the reviewer's decision, not the tool's.

**3. Post new top-level comments only.** `book pr` has no reply, edit or delete. It
can also **resolve** a comment (`pr resolve`) and **open** a PR (`pr open`): this skill
calls neither — resolving a thread, anyone's, is a person's step, and so is opening.

**Fixing one of your own is the person's step, in the Bitbucket UI** — the line runs
through *substance*, not ownership:

- **Withdrawing** one: only when the user asks; they delete it (it leaves a tombstone).
- **A cosmetic fix** — a rendering artifact, a typo, a wrong line reference, the
  finding itself unchanged: the user edits it in place (no tombstone, no second
  notification, replies stay attached). Name each comment and the fix in the report.
- **Never change what a finding says by editing.** Bitbucket shows no edit history,
  so a reviewer who already replied would be answering something that no longer
  exists. The user withdraws it; this skill posts the corrected finding as a new
  comment, and the report says so.
- **A reply** to a thread is the user's to post.

**4. Never print, log or write the API token, even masked, nor ask for or accept one**
([CLAUDE.md, *Private settings*](CLAUDE.md#private-settings); [Credentials](#credentials)).

**5. Do not post a finding you have not verified in the code.** A false positive
on a PR costs a reviewer more than a missed finding, because it is public and
someone has to argue it down. If a concern survives only as a suspicion, put it in
the terminal review as a question, never onto the PR as a finding.

**6. Never edit the source under review.** This skill reviews and posts
comments — it never touches the code itself. A finding is something to
report, not something to fix from here.

---

## Credentials

**This session never holds the token.** Every Bitbucket call goes through
`python3 devtools/book.py pr …`, which reads your own stored credential
inside its own process and sends it only to Bitbucket — never to the terminal, a
file or this transcript (CLAUDE.md, *Private settings*; the guard refuses
`git credential fill` in a session). Its writes go in **your** name, and it refuses a
credential that is not a person's account.

| Need | Command |
|---|---|
| The PR for this branch, or `pr=<id>` | `book.py pr show` · `book.py pr show --number <id>` |
| Comments already on it (the dedupe key) | `book.py pr comments --number <id>` — top-level only, as `path:line` |
| Post the findings the person said yes to | `book.py pr post --number <id> --plan <file> --expect-head <head>` — `<file>` is a JSON list of `{"path", "line", "body"}` in plan order; `<head>` is the head commit recorded in Step 1. The tool refuses to post anything when the PR's head has moved ([Step 5](#step-5--post)) |
| One more inline comment, later | `book.py pr comment --number <id> --path <file> --line <n> --body-file <file> --expect-head <head>` — the same head check, for one comment |
| **Never, from this skill** | `book.py pr resolve`, `book.py pr open` — HARD LIMIT 3. `pr resolve` refuses without the author's confirmation flag, which this skill never passes |

The findings go in a file in the scratchpad — never inline in the command, where
newlines and quotes break. **If the tool reports no credential, say so and stop**
(HARD LIMIT 4).

---

## Process

### Step 1 — Resolve the PR

`book.py pr show --number <id>` with `pr=<id>`; without it, `book.py pr show`
finds the open PR whose source branch is the current branch. The tool reads the
repository from `origin`, never assumes it.

**Stop if there is no open PR.** Do not create one — opening a PR is the author's
decision. Say which branch was searched, and suggest `/book:self-review` instead, which
needs no PR.

**Stop if more than one matches.** List them and ask which.

Record the PR's **source and destination branches**, and its **head commit**. The
head commit matters: line numbers in inline comments refer to the file as the PR
currently stands, so a PR that moves under you invalidates them. `pr post` (and any
`pr comment`) passes it as `--expect-head`, so a comment from this review is never placed on a newer
head: if the tool says the head moved, stop, report what was posted, and review the new head.

### Step 2 — Establish context

Before reading the diff:

- Read the PR title and description for the intended purpose.
- `git fetch origin`, then
  `python3 devtools/book.py review-scope --range origin/<destination>...origin/<source>`.
  **Read only the review checklist files it prints** — the
  [method](references/review-method.md) and [Pass A](references/review-pass-a.md) always,
  and the Pass B dimensions the triage leaves applicable (all of them when a path is not
  placed). A `book:<skill>/<path>` file is in this plugin, read it at `${CLAUDE_SKILL_DIR}/../<skill>/<path>`; any other path is the project's, from its root. Place every path in the method's
  [scope-triage table](references/review-method.md#how-to-use-this-framework): it names the
  affected features, the dimensions to press and what to read.
- Read the plan section in `docs/plans/` for each affected feature, and the part
  of [`docs/architecture.md`](docs/architecture.md) the triage points at
  — not the whole guide. These reads are independent: make them together.
- Find a comparable existing implementation to compare against — this codebase has
  strong conventions, and the nearest sibling feature is usually the standard the
  PR should be held to.

If the description is thin, infer the purpose from the code rather than asking.

### Step 3 — Review, in two passes

```bash
git diff origin/<destination>...origin/<source> --stat
```

**Two passes, in this order: Pass A (requirements → code: what is missing?), then Pass B
(code → itself: what is wrong?).** Why the order, and why only Pass A finds an omission:
[Pass A](references/review-pass-a.md). **Pass A runs first on every review, however small
the diff, and is never skipped.**

#### Pass A — Conformance

Run [`references/review-pass-a.md`](references/review-pass-a.md) in full (checks 1–15): A1
requirements → code, **what is absent is a finding**; A2 code → our docs, **the FSD wins**;
A3 the docs the change invalidated. Its conformance table, passing rows included, goes in
the terminal review.

#### Pass B — Correctness

Work through the Pass B dimension files `review-scope` printed — the coverage
framework, not a checklist to paste anywhere: evaluate every dimension the diff can
plausibly touch, mark the rest N/A, and report only what has evidence
([Anti-noise rules](references/review-method.md#anti-noise-rules)). A dimension not loaded is still a row in the
coverage table.

**Review every changed file.** Do not stop at the first finding, and do not review
only the largest diff — the one-line change to a configuration file is exactly
where an authorization default flips.

**Tag every finding New or Pre-existing** — whether the diff created the
defect or merely touches, extends, or newly exposes one that was already
there. See
[How to use this framework, §4](references/review-method.md#how-to-use-this-framework).

Severity is assigned per [Severity](references/review-method.md#severity) — CRITICAL / HIGH / MEDIUM / LOW / INFO.

**Verify each finding before it becomes a finding**, per
[Before a finding is reported](references/review-method.md#before-a-finding-is-reported) — this codebase records
most of its deliberate oddities in
[Known trade-offs](docs/architecture.md#known-trade-offs).

### Step 4 — Show the plan and ask

Print the full review to the terminal first, then the posting plan:

```
Posting plan — PR #NN (feature/x → dev), head a1b2c3d

  Inline (7):
    🔴 src/…/CreateUserCommand.cs:106   Emails never sent outside Development
    🔴 src/…/CreateUserCommand.cs:97    Two commits outside a transaction
    …
  Terminal only — no honest anchor (1): a finding spanning files
  Skipped as already posted (2)

Post these to PR #NN? Nothing is written until you say yes.
```

**Wait for a yes.** "Looks good" about the *review* is not consent to *post* — ask
again if it is ambiguous.

**Every defect you know about appears in this plan, whatever its provenance.** A
finding you discussed with the user, raised in an earlier run, or read in a plan
still needs a severity, an anchor and a row here — see
[what already counts as a finding](references/review-method.md#before-either-pass--what-already-counts-as-a-finding).
The plan is the only place a reader can see the complete set, so anything absent
from it is a defect nobody has been told about. **Never write "already reported" in
a review; ask "reported to whom?"** — the audience here is the PR's author, who has
read none of your conversation.

### Step 5 — Post

**Inline comments only. Do not post a summary comment.** The
findings carry the review, and a summary alongside them restates on a thread what
the reader is about to read on the lines themselves.

**So every finding needs a line.** A finding with no obvious location is not
exempt — it is a finding whose anchor has not been thought about hard enough, and
there is nearly always an honest one:

| Looks location-less | Actually belongs on |
|---|---|
| "this logic has no test" | the logic, not the missing test file |
| "nothing runs this seed script" | the script |
| "a specified requirement is missing" | the command or DTO that should carry it |

Pin it where the author would make the change. Only when that genuinely does not
exist does the finding stay in the terminal review — and then say so out loud in
the report, rather than letting it disappear.

**The verdict, the counts and the conformance table go to the terminal**, not to
the PR. They are how the reviewer judges the review; the PR gets the work.

**One comment per finding.** Do not batch several findings into one inline comment;
they get resolved as a unit and the unaddressed ones disappear.

**Put nothing machine-readable in the body.** No hidden marker, no tracking id, no
tool signature. **Bitbucket escapes HTML comments rather than stripping them**, so
`<!-- anything -->` renders as visible text at the top of the comment — it looks
like a leaked template, and it makes a careful review read as generated output.

> **Check `content.html`, not `content.raw`, before trusting how anything renders.**
> The API returns both. GitHub's behaviour is not Bitbucket's, and the difference is
> invisible until a person opens the page.

Inline comments go on the **line in the new file**. If a finding is about deleted
code, or spans files, or genuinely has no honest anchor, it stays in the terminal
review — an inline comment pinned to an arbitrary line reads as a mistake.

**Two findings on one line is the case to handle at plan time, not post time.**
Either merge them into one comment or move one to the line it really belongs on.

**Only after the person's yes (HARD LIMIT 1)**, write the plan's inline findings, in the
plan's order, to a JSON file in the scratchpad — `[{"path": "src/…/CreateUserCommand.cs",
"line": 106, "body": "**🔴 CRITICAL — …**\n\n…"}, …]`, `path` as the diff spells it — and post
them with one call:

```bash
python3 devtools/book.py pr post --number <id> --plan <file> --expect-head <head>
```

The tool does the posting's mechanics, so none of it is done by hand:

- **Refuses the whole plan before reaching Bitbucket** when a finding is malformed, two share a
  `path:line`, a body holds an HTML comment (Bitbucket renders `<!-- … -->` as visible text) or
  what looks like a secret.
- **Checks the head once**, against `--expect-head`: moved, and nothing is posted.
- **Skips a finding this account already posted** — a top-level, undeleted comment of yours on
  the same `path:line` that opens with the same text (its first 80 characters, whitespace
  folded). That is this skill's work from an earlier run, and the key needs nothing added to
  the body. Replies and deleted comments never count: Bitbucket gives a reply the *same*
  `inline` block as its thread. Another reviewer's comment on the line does not block a
  finding; a finding you reworded since is posted as a new one — so a re-run keeps the wording.
- **Posts one comment per finding, in order, and stops at the first failure.** It never
  re-sends a failed POST: a 401 or 403 means the credential cannot write pull requests, and
  hammering it locks the account; a POST that got no answer may have landed.
- **Reads the comments back** and looks for every posted and skipped finding on its line, and
  for the failed one — it says whether that one landed after all.
- Prints `<n> posted, <n> skipped, <n> failed, <n> not attempted`, a line per finding with its
  comment `#id`, and the read-back; it exits non-zero on a failure or a finding missing on read-back.

On a failure, **stop and report** what it printed. Do not post the rest by hand. Once the
cause is fixed (or the person says to go on), run the same command again: it resumes, skipping
what is already there. What the API accepts and refuses is in
[`references/bitbucket-api.md`](references/bitbucket-api.md).

### Step 6 — Report

State plainly: the PR, how many comments were posted, how many were skipped as
duplicates — `pr post`'s counts, and the ids it printed — and the verdict. Include the
[coverage summary](references/review-method.md#coverage-summary) and the
conformance table. Give the PR URL. End with the method's
[verdict block](references/review-method.md#the-verdict-block--every-review-ends-with-it) — its verdict rule is the
one READY rule.

**Never claim to have posted something that failed**, and never report a verdict
in the report that differs from the one the findings support.

---

## Comment format

Inline comments are read in a narrow column beside the code. Keep them short —
the reasoning belongs in the terminal review, and the comment carries what the
author needs to act.

```markdown
**🔴 CRITICAL — two commits outside a transaction — New**

The first `SaveChangesAsync` commits the `User` on its own; EF wraps each call in
its own transaction. If token issuance or the second save fails, the user is
committed with no invitation — and, given the email guard above, no way to issue
one. The comment claiming both are committed together is the dangerous part.

**Fix:** wrap both in `IUnitOfWork.ExecuteInTransactionAsync` (CLAUDE.md: *"Two
saves that must succeed together…"*). The block is re-run safe as written.
```

Five elements, always: **severity, title, and New/Pre-existing tag**, **what
is wrong**, **why it matters**, **the evidence** (folded into the same
paragraph — the code beside the comment usually *is* the evidence), **what to
do**. Cite the project's own rule where one applies — the author is far more
likely to act on `CLAUDE.md` than on a general principle. Full field
definitions: [Finding format](references/review-method.md#finding-format).

The terminal review — never the PR ([Step 5](#step-5--post)) — carries the verdict, the
severity counts, the [coverage summary](references/review-method.md#coverage-summary), the findings that have no
single location, a one-line index of the inline ones, and **the conformance table from
Pass A, passing rows included** (its shape:
[A3](references/review-pass-a.md#a3--the-change-to-the-docs-it-invalidated)).

---

## Tone

The author is a colleague, and the comment outlives the conversation.

- Describe the defect, never the person. "This commits before the token is issued",
  not "you forgot".
- Say what is right as well as what is wrong. A review of a sound PR that lists
  only faults misrepresents it — the terminal review should name what was done well
  where it is genuinely notable, and skip generic praise entirely.
- Do not inflate severity to be heard ([Severity](references/review-method.md#severity)).
- Where the requirements or the architecture are ambiguous, say so and ask. Do not
  invent a requirement to justify a finding.

**The point is the maximum number of real defects with the minimum number of false
positives — not the maximum number of comments.**

---

## What next

- **Posted:** the author answers each comment or fixes it; review again after their new commits.
  This skill never approves, merges or declines.
- **Not posted:** the findings stay in the terminal; the person decides what to send.
- **A confirmed defect in merged code:** it gets a `docs/defects.md` row the day it is found
  (CLAUDE.md, Features).
- **In a flow** (`/book:flow`): `review-teammate-pr` → done.
