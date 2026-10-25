---
name: process-ticket
description: >
  Use when given a ticket or issue to implement: reads it, finds the affected code, proposes a short
  plan, implements on a branch with tests, and prepares it for review. Stops at each decision a person
  must make.
---

# Process a ticket

1. **Understand.** Read the ticket (the user pastes it, or give its id and use the tracker's CLI).
   Restate it in two sentences plus its acceptance criteria. If either is unclear, ask before coding.
2. **Locate.** Find the code the change touches (search, then read); list files and the callers at risk.
3. **Plan.** Propose 3-7 steps with the tests that will prove each. Wait for a yes on anything that
   changes a contract, schema or public behaviour.
4. **Branch.** `git checkout -b <type>/<ticket-id>-<slug>` from the base branch.
5. **Implement** test-first where the project has tests; keep the change as small as the ticket allows.
6. **Verify.** Run the project's build and tests; show the result honestly, including failures.
7. **Hand over.** Summarise what changed against each acceptance criterion; offer `commit` and
   `create-pr`. Do not merge or close the ticket.
