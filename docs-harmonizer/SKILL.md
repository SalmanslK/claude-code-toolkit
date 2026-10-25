---
name: docs-harmonizer
description: >
  Use to bring a set of documents into one voice: removes duplication, resolves contradictions by
  naming the single owner of each fact, and aligns terminology. Reports first; edits only what the user
  approves.
---

# Harmonize documentation

1. **Inventory** every document in scope: path, purpose, last change. Decide the *owner* of each topic
   (one document per topic); other documents link to it instead of restating.
2. **Find duplication**: the same fact in two places. Keep it in the owner; replace the copy with a link.
3. **Find contradictions**: two documents that disagree. Never pick silently. Check the code or the
   latest requirement; if still unclear, list it as a question for a person.
4. **Align terminology**: build a glossary of terms in use, pick one name per concept, list every
   variant and where it occurs.
5. **Report** (before editing): duplicated facts, contradictions, term variants, each with `file:line`.
6. **Apply** only the changes the user approves, smallest first. Do not rewrite for style, and do not
   delete history that a link or anchor still needs.
