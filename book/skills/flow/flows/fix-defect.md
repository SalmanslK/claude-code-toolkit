# fix-defect

**C1 · Defects and questions.** **Trigger:** a bug is confirmed.
**Packs:** none.

## Steps

1. `/book:raise defect` — the row the same day, its class, the FSD section it agrees with.
2. ✋ Check the fix against the FSD; if they disagree, stop and ask the module's owner.
3. Fix it, with a test that fails first.
4. ⏸ `/book:self-review` — in a fresh session or a subagent; until READY.
5. `/book:commit` — the D id in the message.
6. ✋ `/book:ship`.
7. After the merge: `after-merge` (the row closes; the next `/release-notes` lists it as fixed).

## Loops

- ⟲ step 4 until READY, at most 3 rounds.

## Done when

Merged, and the defect row is closed.
