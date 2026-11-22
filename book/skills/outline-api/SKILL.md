---
name: outline-api
description: >
  Use when a module or screen is about to be built — "draft the API for Account Settings". Draws the API
  from the wireframes and the FSD (every endpoint, its request, response, errors and permission) into
  the plan's §6, and raises a question for what the FSD does not settle. Not for an API already built
  (api-contracts.md) or code against the FSD (book:fact-check). Formerly /api-contract-draft.
---

# /book:outline-api — the API a screen needs, before anyone builds it

**One question:** what does each screen of this module call, and with what? The answer is the
module's API contract — every endpoint, its request, its response, its errors and its permission —
drawn from the designer's wireframes and the FSD before the back end or the front end is written.

**The FSD decides; the wireframes find.** The designs show what each screen loads, submits and
displays, so no endpoint is missed. But a design is evidence, never a requirement
([Which document wins](docs/open-questions.md#which-document-wins)): a field, filter or
action a frame shows and the FSD does not specify becomes a **question**, not an endpoint.

**Where it goes:** the module's plan, **§6 API surface** — the template's *before it is built*
table, with the shapes beneath it. No new document. Once built, §6 becomes links to
`api-contracts.md` (generated) and the module's FE guide,
as the template says.

*The Book's command is `book`: `python devtools/book.py <command>` from the project's root.*

---

## Steps

### 1. Gather — read before drawing

1. **The FSD section** for the module — locate and print only its pages with
   `book fsd-page "<heading>" --print` ([reading the FSD](../fact-check/references/reading-the-fsd.md)):
   its field tables (type, required,
   limits, defaults), validation messages word for word, list columns, filters, sorts and search,
   and every action and its rule.
2. **The permissions** — the module's rows in
   authorization §2, drawn from the
   FSD. No permissions matrix exists (CLAUDE.md *Layout*): rows not yet there come from the FSD's
   permission sections, added as authorization §3
   says; where the FSD names none, it is a question.
3. **The wireframes** — the module's frames in the highest `requirements/wireframes/wireframes-V<n>/`.
   They are PDFs and a board is far too large to read whole: render the module's pages to images
   in the scratchpad (never inside the repository), crop each screen with Pillow, and read the
   crops. Note every list, form, dropdown, filter, button and detail panel, per screen.
4. **What already exists** — `api-conventions.md` (the dotnet pack)
   (paging envelope, errors, auth, tenant scoping, dropdowns), the existing routes in
   `api-contracts.md`, and the shared lookups. Reuse a lookup that exists; never draw a second one.
5. **The front end's own contract** — the module's rows in
   `fe-api-coverage.md`, which owns the endpoints the front
   end requires, found by their paths, not by reading the file:
   `git grep -n -i "/<module-route>" docs/api/fe-api-coverage.md` (each row carries the path).
   No hit: say "no front-end rows" — its §2 says whether any contract has arrived. Then
   `requirements/fe-api-contracts/` behind them: match their names and shapes where the FSD
   allows, and say where they differ.

### 2. Draw — screen by screen

For every screen, list what it calls, then merge into one endpoint list for the module:

| Screen element | Becomes |
|---|---|
| A list | `GET` with the paging envelope; each filter, sort and search the FSD names; the columns as the item shape |
| A form | `POST` (add) or `PUT` (edit) — the FSD's field table as the request: type, required, limits, defaults |
| A details view | `GET {id}` — every field shown, with audit fields as `createdById`/`createdBy` |
| A dropdown | An existing lookup, or a new one following the dropdown conventions |
| A delete, a status toggle, a state change | Its own route; its guard's FSD message as the error |

For each endpoint, write:

- **Method and path** in the module's existing style (`/api/v1/<module>…`).
- **Permission** — the exact permission from authorization §2. Default-deny: no permission, no endpoint.
- **Request and response** — fields, types, required, and the FSD section each comes from.
- **Errors** — status, error code and the FSD's message **verbatim** (missing full stops included).
- **Source** — the FSD section, and the wireframe frame that showed it.

### 3. Check — nothing missed, nothing invented

- **Every frame's element** has an endpoint, or a line saying why none is needed.
- **Every FSD rule** that reaches the API (validation, permission, guard, lock) is on an endpoint.
- **Every field has an FSD source.** A field only a design shows → a question in
  `open-questions.md`, with a recommendation; the contract leaves it out and names the question.
- **Tenant scoping** for every read and write, where the project is multi-tenant (`[book] scoping_word`), per
  `api-conventions.md` (the dotnet pack).

### 4. Write — and stop for agreement

1. Fill the plan's **§6 API surface**: the endpoint table, then the request and response shapes.
   Add the questions to `open-questions.md` and link them from §8.
2. Add the work to the plan's **Tasks**: one `BE` task per endpoint group, and one `FE` task to
   agree the contract with the front-end team.
3. **Report and stop.** Print the endpoint count per screen, the questions raised, and anything
   that differs from the front end's own contract. The contract is agreed with the front-end team
   and the module's owner before code — this skill drafts it, people agree it.

## Never

- **Put a field, filter or action in the contract that only a design shows** — it is a question.
- **Invent a permission** the FSD does not give.
- **Write the generated `api-contracts.md`**, or change anything under `requirements/`.
- **Draw a second lookup** for data an existing one serves.
- **Carry on past a source it could not read** (an FSD section, a wireframe) — say what was
  blocked and stop ([CLAUDE.md, *Blocked means stop*](CLAUDE.md#how-these-instructions-are-organised)).

## What next

- The contract agreed: `/book:impact` on the plan's FSD section, then build the plan's Tasks.
- Questions raised: they wait in `open-questions.md`; `/book:check-sources` before chasing one.
- **In a flow** (`/book:flow`): `new-feature` → `/book:impact`.
