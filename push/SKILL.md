---
name: push
description: >
  Use to push the current branch safely: verifies the branch, runs the project's checks, and pushes
  without force. Refuses protected branches.
---

# Push

1. `git branch --show-current`. If it is a protected branch (per the project's rules, else `main`,
   `master`, `dev`, `develop`, `release*`), **stop** and suggest a feature branch.
2. `git status`: uncommitted changes → ask whether to commit first (use the `commit` skill).
3. Run the project's fast checks if it names them (`CLAUDE.md`, a `run-checks` script, or CI config).
   If they fail, show the failure and stop.
4. `git push -u origin HEAD`. Never `--force`; if the push is rejected, show why and ask. Never use
   `--no-verify`.
5. Report the branch, the commits pushed, and the remote URL.
