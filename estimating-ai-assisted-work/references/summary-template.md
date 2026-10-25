<!--
SUMMARY TEMPLATE (shareable one-document comparison of scopes). Copy to `<Project>-Summary-<YYYY-MM-DD>.md`, replace every {{...}},
delete these comments, then run: python scripts/make_summary_pdf.py <file>.md
Rules:
- Plain words; a manager should follow it without the estimate file.
- Hours are the likely (median) build hours only. Do NOT show the 80% bid or any buffered figure in the summary (the user wants minimum hours here); buffers, blockers and ambiguities go in the pointers at the bottom, and the bid stays in the estimate files. Never show a sum of minimums.
- Show only the columns that were priced (for example Backend only, with a line saying web is not priced yet and why).
- Put a blank line between every bold lead-in and the list under it (the PDF script also repairs this).
- Keep scope names identical across every table (e.g. Lean / Full SOW / Complete).
- Use 2 to 4 scopes. Typical set: Lean (smallest version that proves the idea), Full (the requirements document as written, minimum versions), Complete (the wider vision, if one was priced).
- Items the document makes conditional ("where supported", "if authorised", "where agreed") are add-ons, listed under "Not in the figure".
- Every number must trace to an estimate file. If scopes were priced on different calibration (H), say so in "The figures".
- The "Files" section is for the .md only; the PDF leaves it out.
-->

# {{Project}}: Scope Comparison and MVP Overview

**Date:** {{YYYY-MM-DD}} | **Basis:** {{source document and version}} | Ballpark for planning, not a commitment.

## Purpose

This document compares the {{N}} scopes proposed for {{Project}}:

- **{{Scope A}}, {{hours}} hours:** {{one line}}.
- **{{Scope B}}, {{hours}} hours:** {{one line}}.
- **{{Scope C}}, {{likely}} hours:** {{one line}}.

{{One sentence per scope on what it proves or delivers.}}

**Scope note:** these are estimates for different scopes and are not directly comparable implementation plans. The hours are build hours only (coding, testing, fixing), with no buffers; {{exclusions: design, discovery, project management, hosting set-up, UAT support, documentation}} are excluded. The figures are medians: about half of similar work runs over them, and the 80% bid is in the estimate files. {{If a team-size cap was used: without the cap the figures would be <scope> <uncapped hours>h, ...}} Confirm the baseline and phase boundaries with {{client}}. {{Smallest scope}} is smaller than {{Full}} and should be agreed as a first phase if it is to replace or precede the full commitment.

## The figures

| Scope | {{Columns priced, e.g. Backend}} build hours (likely) |
|---|---|
| **{{Scope A}}** | **{{}}h** |
| **{{Scope B}}** | **{{}}h** |
| **{{Scope C}}** | **{{}}h** |

- **Why not lower:** adding up the best case of every task gives {{}}h ({{Scope B}}) and {{}}h ({{Scope A}}). That needs every task to go perfectly, which almost never happens, so it is not used.
- **People needed for the {{N}} build weeks in the document:** about {{}} developers for {{Scope B}}, about {{}} for {{Scope A}}.
- **Unit cost:** {{calibration set and H per scope; if scopes differ, give the same-basis comparison}}.

## 1. {{Scope A}}: {{hours}} hours

{{One line: the smallest version that still demonstrates the idea.}}

- **{{Capability}}:** {{plain-words description}}.

**Excluded from {{Scope A}}**

- {{Item left out}}.

**Expected outcome:** {{what a user can do}}.

## 2. {{Scope B}}: {{hours}} hours

{{One line: everything listed in the requirements document, delivered as ...}}

- **{{Capability}}:** {{plain-words description}}.

**Not in the {{hours}}h (priced as add-ons):** {{each conditional or optional item with its likely hours, or "not priced until the rule exists"}}.

**Expected outcome:** {{...}}.

## 3. {{Scope C}}: {{likely}} hours

{{One line: the broader platform, delivered in stages; overlaps with Scope B where applicable.}}

**Phase 1: {{Name}} ({{hours}}h)**

- **{{Capability}}:** {{...}}.

**Beyond the priced phases: not yet priced**

- **{{Capability}}:** {{...}}.

**Expected outcome:** {{...}}

| Phase | Likely hours | In {{Scope B}}? |
|---|---|---|
| {{Phase}} | {{}}h | {{Mostly / Partly / A small part / No, and what is missing}} |
| **Total priced** | **{{}}h** | {{Scope B}} is about {{}}h |

## 4. Side-by-side comparison

| Capability | {{Scope A}} ({{}}h) | {{Scope B}} ({{}}h) | {{Scope C}} ({{}}h) |
|---|---|---|---|
| {{Capability}} | {{Not included / Basic / Included / ...}} | {{}} | {{}} |

## 5. What the MVP will likely cover

The {{Scope A}} MVP is expected to support this basic journey:

1. {{Step}}.

**MVP outcome:** {{one sentence}}.

{{One paragraph on what the next scope adds, and one on what the largest scope adds.}}

## 6. Key scope and planning considerations

- **{{Smaller scope}} is not equivalent to {{Full}}.** {{What it omits and what the client must agree}}.
- **Confirm what the estimates include.** {{Same baseline, assumptions, integrations, testing and deployment across scopes}}.
- **Separate priced and unpriced scope.** {{List}}.
- **Validate integration behaviour.** {{Read-only versus two-way, and the risk difference}}.
- **Define the MVP acceptance criteria.** Agree the screens, data fields, role rules, integrations and end-to-end journeys that must work before acceptance.

## Work breakdown

Likely build hours per work item. "—" means the item is not in that version. Rows are rounded, so a column can differ from its total by 1h.

| Work item | {{Scope B}} | {{Scope A}} |
|---|---|---|
| **Backend** | | |
| {{Item in plain words}} | {{}}h | {{}}h or — |
| **Backend total** | **{{}}h** | **{{}}h** |
| **Web** | | |
| {{Screens in plain words}} | {{}}h | {{}}h or — |
| **Web total** | **{{}}h** | **{{}}h** |
| **Build total** | **{{}}h** | **{{}}h** |

## Pointers for awareness (risks to the hours)

Blockers, assumptions and ambiguities that are NOT in the hours above. Each line says what is unknown and what it could add. Order by size.

1. **{{Blocker}}.** {{What is unknown, what it could add in hours, what closes it}}.

## Summary

- **{{Scope A}} ({{}}h):** {{one line}}.
- **{{Scope B}} ({{}}h):** {{one line}}.
- **{{Scope C}} ({{likely}}h):** {{one line}}.

## Files

Details are in `{{output folder}}`:
- `{{Scope B estimate file}}`
- `{{Scope A estimate file}}`
