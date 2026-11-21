# qa-build

**F1 · Releases and status.** **Trigger:** before and after a QA build.
**Packs:** deploy, fe-guides.

## Steps

1. `/book:check-sources all`.
2. `/book:progress`.
3. `/book:fact-check` — on what changed since the last build.
4. `/book:check-permissions` — on the modules that changed since the last build.
5. `/book:check-docs`.
6. `/book:check-guides`.
7. ✋ `/book:release-notes` — features, fixed defects, known gaps, FE changes, what to test; the person approves them.
8. ✋ `/book:deploy QA`.
9. ✋ `/book:write-for` — QA, from the notes; the person sends it.

## Loops

- ⟲ steps 3–6: each gap is fixed (`fix-defect`) or listed as a known gap in the notes.

## Done when

QA is deployed and verified, and the notes are written and sent.
