# Running the phases with parallel agents

Phases 2–5 are too large for one context: about 65 docs and 37k lines. Fanning
out to subagents works, but only under these rules. Each rule comes from
something that went wrong without it.

## Ownership

- **One file, one writer at a time.** Before launching agents, give each one a
  **disjoint set of files** it may edit, and name them in its prompt. Two agents
  on the same file overwrite each other without warning.
- **Readers can overlap; writers cannot.** An auditor may grep the whole doc set
  for its own concepts, but it edits only its own files.
- **Anything outside an agent's area is reported, not fixed.** Have the agent
  list cross-area items as `file:line` plus the proposed text. The orchestrator
  applies them once the owning agent has finished.
- **Rules files** (CLAUDE.md, the skills) belong to one agent at a time, and only
  for edits the user has approved.

## Ids and anchors are allocated centrally

- **Question ids (Q<n>), defect ids (D<n>) and renamed anchors** are chosen by
  the orchestrator before any agent writes them. Parallel agents each picking
  "the next free number" is how D132 came to be used twice.
- **Give the full anchor for every new heading.** GitHub slug rules apply:
  lowercase; punctuation other than hyphens and spaces dropped; spaces become
  hyphens. Characters like `·`, `→`, `—` and `'` disappear, so `Q60 · What…`
  becomes `q60--what…`.

## Reuse auditors to apply their own findings

- **The auditor that found an issue applies the fix.** Send the list of approved
  finding ids to that auditor with SendMessage, rather than briefing a fresh
  agent. It still holds the file context and its evidence, so it re-verifies
  faster and more accurately.
- **Apply in two rounds.** SAFE findings first. Then, after the user has decided,
  the RECOMMENDED findings and the decisions. Wait for an agent to finish the
  first round before sending the second, so the two rounds never interleave on
  one file.

## Brief every agent the same way

Every prompt states:

- its **scope**: which files it may read and which it may edit
- **read-only or apply**
- **no commits** (the orchestrator commits once per phase)
- **use the Edit tool**, which keeps each file's line endings
- **re-verify each quoted current text before changing it**, and skip it and
  report if the text isn't there
- **annotate history rather than delete it**
- **never rename a heading**
- the **source-of-truth order**: FSD → answered Part 2 questions → approved
  plans and `architecture.md` → code
- for docs-to-docs skills: **never open `src/` to break a tie**. Hand the tie to
  code-doc-audit instead.
- a **report format**: per-finding applied or skipped with the reason, plus a
  link check on the files it touched

## Scratch files

- **Each agent gets its own script filename in the shared scratchpad**, for
  example `lc_<area>.py`. Agents writing the same `links.py` overwrote each
  other's copy partway through a run.
- **Never create scratch files inside the repo.** They end up in `git status`
  and can be committed by accident.
- **Prefer the bundled `scripts/linkcheck.py`** over a hand-written checker, so
  that link counts can be compared between runs.

## Verification agents

- **Checking claims against the code:** use one read-only Explore agent and give
  it a numbered list. Ask for `path:line` evidence and verbatim messages, and for
  "not found" plus what was searched when something is absent.
- **Sweeping questions or defects:** use a general-purpose agent, read-only.
  Point it at the scratchpad copies of the FSD text and comments
  (`fsd-live-doc.txt`, `fsd-comments-all.txt`) so it does not fetch them again.
- **Treat an agent's "UNSURE" as unresolved.** Route it to the skill that owns
  it; don't promote it to a finding.
