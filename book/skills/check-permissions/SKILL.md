---
name: check-permissions
description: >
  Use to check who may do what: FSD role rules changed, a module added, before a QA build. Sets the
  FSD's role rules against authorization §2 and the code; reports gaps. Writes nothing.
argument-hint: "[module | branch | all]"
allowed-tools: Read, Grep, Glob, Bash(git diff*), Bash(git log*), Bash(git grep*), Bash(git ls-files*), Bash(git branch*), Bash(factory fsd-page*), Bash(pdftotext *), Bash(python "${CLAUDE_SKILL_DIR}/scripts/permission_map.py"*), Bash(python3 "${CLAUDE_SKILL_DIR}/scripts/permission_map.py"*)
---

# /book:check-permissions [module | branch | all] — who may do what, three ways

**Who may do what** lives in three places, and they drift apart:

1. **The FSD** — the role rules: which role may list, view, create, edit, delete, change status, approve.
   **It wins every conflict** ([which document wins](docs/open-questions.md#which-document-wins)).
2. **`docs/plans/authorization.md` §2** — the permission catalogue drawn from it, the *Not
   permission-gated* list, the *Rules that are not permissions*, and §4's recorded gaps.
3. **The code** — the catalogue (`Permissions.cs` in the dotnet pack), the permission each request
   declares, what each route therefore needs (`docs/api/api-contracts.md`, generated), the seeded roles,
   and the handlers that enforce target rules.

**No permissions matrix exists, and this skill does not make one** ([CLAUDE.md, *Layout*](CLAUDE.md#layout)):
the FSD stays the only owner of who may do what. The role × action view you build is part of the
report, never a file. **You write nothing**: each gap becomes a defect, a question or a §2 fix only
when the person approves it.

Roles are data in the Book: only the Administrator is seeded, and every other role is created through
the role API. So "role X may delete" is checked as **"a permission exists for delete, gates the delete
route, and the FSD's roles can be given it"** — not as a seeded grant.

## Scope — decide it first

| Asked about | Scope |
|---|---|
| A module | Its FSD section, its §2 row, its routes |
| A branch or "this change" | `git diff --name-only <base>`: the modules whose requests, endpoints or catalogue changed |
| `all`, or before a QA build | Every module the FSD gates |

Say the scope in the report's first line.

## 1. The mechanical half — run the script

```
python3 "${CLAUDE_SKILL_DIR}/scripts/permission_map.py"
```

It reads §2, the code's catalogue and the contracts, and prints: the catalogue differences (§2 against
the code), permissions declared by no route and routes declaring an unknown one, the module → action →
routes map, and the routes **no permission gates** (any signed-in user) and the anonymous ones. Its
counts are checked against the contracts' own count line; a **MISMATCH** means read the contracts by
hand. **BLOCKED** (no plan, no catalogue) stops the skill there: say what is missing. A stack without
generated contracts gets the catalogue comparison only; say the route checks were not made.

Cite its lines; do not re-derive them by reading.

## 2. The judgement half — the FSD

For each module in scope, locate its permission and role sections with
`factory fsd-page "<heading>" --print` ([reading the FSD](../fact-check/references/reading-the-fsd.md)) and
read them. Note every action the FSD names and **which roles may do it**, with the section number and
heading. Where the FSD is silent on an action the code gates, that is a question, not a finding against
the code.

Then check, and record each failure as a finding:

| # | Check | Severity when it fails |
|---|---|---|
| P1 | Every action the FSD restricts has a catalogue permission and **gates its route** | **Critical** if the route is open to every signed-in user; High if the permission is missing |
| P2 | Every route open to any signed-in user (section 4) is one the FSD lets every user do, and is on §2's *Not permission-gated* list — own account, own session, reference lists, name-and-id dropdowns | **Critical** when it returns or changes someone else's data |
| P3 | Every anonymous route (section 5) is one the FSD opens to the public (sign-in, reset, health, docs) | Critical |
| P4 | **Granularity:** where the FSD lets one role do an action and not another, the two sides are separate permissions. One permission covering both cannot express the rule | High |
| P5 | Every permission traces to an FSD action. One the FSD does not give is invented ([`/book:outline-api`](../outline-api/SKILL.md) forbids it) | Medium |
| P6 | Every rule that depends on the **target** ("may not edit an administrator", "only their own business unit") is in §2's *Rules that are not permissions*, and its error code is enforced in a handler (`git grep` the code) | High |
| P7 | §2 matches the code's catalogue (script section 1), and every catalogue permission gates a route (section 2) | Low (doc drift) / Medium (dead permission) |
| P8 | Every contradiction already known is in §4 with a question in `open-questions.md` | Low |
| P9 | Every permission in scope has a holder and a non-holder test (authorization §3, step 4): `git grep` the tests for it. Every request on the open allow-list (`RequestPermissionCoverageTests`) has a reason | Medium |
| P10 | A role the project seeds beyond the Administrator, or a default role the FSD names, holds exactly what the FSD grants it | High |

**Never settle a P-finding by assuming.** If the FSD and the code disagree and the FSD is ambiguous, it
is a question for the BA. Report it so; do not pick a side.

## The report

```
Scope: <module | branch | all> — FSD V<n>, plan §2, code at <commit>
Script: <counts line>; <BLOCKED / MISMATCH / clean>

| Role ↓ / Action → | list | view | create | edit | delete | setstatus | … |   ← per module, from the FSD
| <role>            | ✓ §4.2 | … |

| # | Check | Severity | FSD (section, heading) | §2 | Code (file:line or route) | What to do |
```

What to do is one of: **defect** (the code is wrong against a clear FSD rule), **question** (the FSD is
silent or contradicts itself), **§2 fix** (the plan is wrong against the code and the FSD), or **test**
(the rule holds but nothing proves it). End with the counts by severity and "nothing written".

## What next

- **A defect or a question the person approves:** `/book:raise defect` or `/book:raise question`, one at
  a time; a contradiction also gets its §4 row.
- **A §2 fix:** on a docs branch ([docs/CLAUDE.md, *Which branch a doc change goes on*](docs/CLAUDE.md#which-branch-a-doc-change-goes-on));
  the code changes only through a defect.
- **Missing tests:** with the module's next change, or as a task in its plan.
- **In a flow** (`/book:flow`): `docs-health` → `/book:trim`; `qa-build` → `/book:check-docs`.
