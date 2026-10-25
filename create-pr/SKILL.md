---
name: create-pr
description: >
  Use to open a pull request for the current branch: checks the branch is pushed and clean, writes a
  title and description from the commits and diff, and opens the PR with the host's CLI.
---

# Create a pull request

1. **Checks.** `git status` clean; not on a protected branch; branch pushed (`git push -u origin HEAD`
   only if the user agrees). Base branch from the project's rules or the user; never guess `main`.
2. **Read** `git log <base>..HEAD --oneline` and `git diff <base>...HEAD --stat`.
3. **Write** the title (imperative, under 70 characters) and a description: *What changed*, *Why*,
   *How it was tested*, *Risks and rollback*, linked ticket ids. No AI attribution lines.
4. **Open it** with the host CLI the repo uses (`gh pr create`, `az repos pr create`, or the host's API
   through a credential the user stored; never ask for or print a token).
5. **Report** the PR URL and anything the user must do next (reviewers, checks pending).

Never force-push, merge, or approve. Stop and ask when the base or host is unclear.
