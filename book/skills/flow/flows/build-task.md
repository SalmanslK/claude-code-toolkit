# build-task

**B2 · Features.** **Trigger:** one task from an approved plan to an open PR.
**Packs:** none.

## Steps

1. Read the task in the plan; write the code and the tests that prove it.
2. ⏸ `/book:self-review` — in a fresh session or a subagent; fix and review again until READY.
3. `/book:commit` — only the reviewed work: the fingerprint must match.
4. ✋ `/book:ship` — local CI and the description; the PR when the person asks.
5. After the merge: `after-merge`.

## Loops

- ⟲ step 2 until READY, at most 3 rounds.

## Done when

The PR is merged and the task is Built.
