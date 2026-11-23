# Bitbucket — what the PR tool sends, and what Bitbucket does with it

Every call goes through `python3 devtools/book.py pr …`
(`devtools/factory/bitbucket.py` does the HTTP).
The token is read inside that process and never reaches this session — see
[Credentials](../SKILL.md#credentials). This file is what the API accepts and refuses, so a
finding is anchored where it will render.

---

## Existing comments — read them before posting

`pr comments --number <id>` lists the PR's **top-level** inline comments as `path:line`,
plus a count of general ones. It already drops `"deleted": true` comments (a removed
comment should not silently come back) and **replies** — a reply carries the same `inline`
block as the comment it answers, so counting it would make its line look occupied and the
next run would drop a real finding there.

**Key on that `path:line`.** Nothing machine-readable goes in a body: Bitbucket **escapes
HTML comments rather than stripping them**, so a hidden marker renders as visible text.
`pr post` reads the same list itself and keys on `path:line` **plus** the comment's author
(this account) and the first 80 characters of its text, whitespace folded.

---

## An inline comment

`pr comment --number <id> --path <file> --line <n> --body-file <file> --expect-head <sha>` sends
`{"content": {"raw": …}, "inline": {"path": …, "to": n}}`. With `--expect-head` it first reads the
PR and posts only while its head is still that commit (7 or more characters in common —
Bitbucket gives the head as 12); otherwise it posts nothing and says the head moved.

| Field | Means |
|---|---|
| `path` | Repository-relative, forward slashes, **as the diff spells it**. A path outside the diff is either refused (`400`) or accepted and rendered detached from any line — never rely on it |
| `to` | The line in the **new** version — what a finding on added or changed code wants |

A finding about a line the PR **deleted** has no `to` line; it stays in the terminal review.

## A review's findings

`pr post --number <id> --plan <file> --expect-head <sha>` sends the same request once per finding of
a JSON list of `{"path", "line", "body"}`, in order. It checks the head once before the first, skips a
finding this account already has on that line with the same opening, stops at the first failure
without re-sending it, then reads the comments back and reconciles them against the plan
([Step 5](../SKILL.md#step-5--post)).

**Check `content.html`, not `content.raw`,** when in doubt about how something renders — the
API returns both, and GitHub's rendering is not Bitbucket's.

> **Severity emoji reach Bitbucket fine and kill a Windows console.** Printing a body through
> Python on a cp1252 console raises `UnicodeEncodeError` for 🔴. The tool reconfigures its own
> output; anything else that echoes a body needs `PYTHONIOENCODING=utf-8`. The failure is in
> the *reporting*, after the write — it can strand a run that already posted.

---

## What must never be called

The tool makes three writes — open a PR (`pr open`, only when the person asks), post a
comment (`pr comment`, or one per finding with `pr post`) and resolve a comment (`pr resolve`).
`/book:peer-review` makes only the second: it never opens a PR and never resolves a thread, anyone's — `pr resolve` refuses
without the author's confirmation flag, which only `/book:ship` passes. These sit one word away
on the same resource, and no skill makes them:

```
POST   /pullrequests/<id>/approve      ← approving is a person's decision
POST   /pullrequests/<id>/merge        ← never
POST   /pullrequests/<id>/decline      ← never
PUT    /pullrequests/<id>              ← edits title, description, reviewers
PUT    /pullrequests/<id>/comments/<n> ← edits a comment, possibly someone else's
DELETE /pullrequests/<id>/comments/<n> ← deletes one
POST   /pullrequests/<id>/comments/<n>/resolve ← `pr resolve`: never from /book:peer-review
```

---

## Failures worth recognising

| The tool reports | Almost always |
|---|---|
| no Bitbucket token | No credential for bitbucket.org in git's store — the person stores one; never paste it here |
| not a person's account | The stored credential is a repository or workspace access token, which acts as a bot — the PR would not be theirs |
| `401` | The credential is revoked or expired |
| `403` | It lacks `pull request: write` — reading worked, so this surfaces only at the first post |
| `404` on a PR that exists | Wrong workspace or slug — check what `origin` says |
| `400` on an inline comment | `path` not in the diff |
| `429` | Rate limited. **Stop.** Report what was posted; do not retry in a loop |
| "may have been created" | The POST timed out after sending. **Look before posting again** — it may have landed |

**On any failure, stop and report what had already been posted** — `pr post` stops by itself and
prints it. Its skip key makes a re-run resume rather than duplicate; an account locked out by retries is not recoverable.
