---
name: code-review
description: >
  Use to review a branch, diff or pull request for correctness, security, tests and fit with the
  project's rules. Reads the project's CLAUDE.md for standards; reports findings ranked by severity
  with file and line. Read-only; never edits code.
---

# Code review

1. **Scope.** Take the target from the user (branch, PR number, or "my changes"). Get the diff against
   the base branch: `git diff <base>...HEAD`. If it is empty, say so and stop.
2. **Rules.** Read the root `CLAUDE.md` and any nested one for the folders touched. Those rules are the
   standard; do not invent others.
3. **Review in two passes.**
   - *Correctness*: logic errors, unhandled nulls and errors, off-by-one, race conditions, wrong
     transactions, broken contracts with callers.
   - *Risk*: security (injection, authorization, secrets, logging of sensitive data), data loss,
     performance traps (N+1, unbounded queries), missing tests for new behaviour.
4. **Report** each finding as: severity (blocker / major / minor / nit), `file:line`, what is wrong,
   why it matters, a concrete fix. Quote the line. Group by severity, blockers first.
5. **Do not pad.** If a pass finds nothing, say "no findings". Never praise filler or restate the diff.

Never edit files, commit, or post comments unless the user then asks.
