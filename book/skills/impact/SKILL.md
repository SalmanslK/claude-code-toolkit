---
name: impact
description: >
  Use when asked what a change reaches — "what does this branch touch", "what does this FSD change land
  on". Lists the modules, requirement ids, tests to run, FE guides, plans and generated docs to update,
  and the risk tier. Changes no code. Not for a review (book:self-review) or an audit (book:fact-check).
  Formerly /change-impact.
allowed-tools: Read, Grep, Glob, Bash(python3 devtools/book.py impact*), Bash(python3 devtools/factory/factory.py impact*), Bash(python devtools/book.py impact*), Bash(python devtools/factory/factory.py impact*), Bash(git diff*), Bash(git log*), Bash(git status*)
---

# Impact analyzer

Answers one question: **what does this change reach?** The deterministic part is
`book impact`; this skill adds what a path map cannot see. It changes no code.

*The Book's command is `book`: `python devtools/book.py <command>` from the project's root. On a Book before v1.4.0, which has no `devtools/book.py`, run `python devtools/factory/factory.py <command>`; `book verify`, `init` and `upgrade` are `factory.py book verify` and so on there.*

## Input — one of

- **The current branch** (default): everything that differs from `origin/dev`,
  committed or not.
- **Paths** the change will touch, before any code exists.
- **An FSD section** (for an FSD revision or a curveball): `python3 devtools/book.py impact
  --block "<section name or page>"` prints only that section's block of
  `docs/Audit/spec-traceability.md` (written by `/book:fact-check`; never read the whole file). Take the
  code paths its rows cite, and analyse those paths. A section with no rows is unbuilt —
  say so, and name the plan that would own it from [`docs/project.md`](docs/project.md).

## Steps

1. **Run the map.** `python3 devtools/book.py impact [paths…]`. It gives
   the modules (from `factory.toml`), each module's integration-test filter, FE guide
   and plan, the cross-cutting paths no module owns, the requirement ids the
   traceability matrix ties to the changed files, and the generated docs to regenerate.
2. **Add what the map cannot see** — each only if the change reaches it:
   - **Callers in other modules.** A delete guard, a lookup, a shared handler another
     module calls into: a grep for the type name under `src/`. Each caller's module joins the list — its tests run too
     ([`tests/CLAUDE.md`](tests/CLAUDE.md#choosing-what-to-run)).
   - **The FE contract.** An endpoint, request or response DTO, permission or error
     message changed: the module's guide, `api-conventions.md` (the dotnet pack)
     if the rule is global, `fe-api-coverage.md`,
     and the Postman `JOURNEY` (`src/<Name>.API/CLAUDE.md` (the dotnet pack)).
   - **Permissions.** The permission catalogue (`Permissions`), the `Role` aggregate or a command's permission:
     `plans/authorization.md` (the project's plan) and `GET /auth/me`.
   - **Schema.** A migration: the ERD, the idempotent-script proof
     (`src/<Name>.Persistence/CLAUDE.md` (the dotnet pack)),
     and any seed script in `database-scripts/seed/`.
   - **QA.** The requirement ids' rows in
     [`qa-artifact-test-suite.md`](docs/qa-artifact-test-suite.md).
   - **Open items.** Open `D`/`Q` rows in [`defects.md`](docs/defects.md) and
     [`open-questions.md`](docs/open-questions.md) naming the same module or ids.
3. **Take the tier from the tool**: `python3 devtools/book.py impact --ci [paths…]`
   prints `tier=` — `full`, `modules`, `build` or `checks`, what `ci-local.sh` runs
   (local CI tiers) — and `reason=`, the path or
   module that set it. Report both as printed; never work a tier out by hand.
   **If `book impact` fails**, say so and stop — a map that did not run is not an empty one.

## Output — this shape, always

```
Impact — <branch or paths or FSD section>
Tier: <full|modules|build|checks> — <the reason book impact --ci printed>

Modules: <name> (tests: <filter>) …
Cross-cutting: <paths>, so the whole integration suite runs | none
Requirement ids: <FSD-…-R…> …
Callers outside these modules: <module — type — why> | none found

Run:    <the dotnet test commands, with filters>
Update: <each doc or guide, and why>
Regenerate: <generated docs>
Open items touching it: <D/Q ids> | none
Unknown: <what could not be determined, and how to find out>
```

Say **"none"** rather than leaving a line out — an absent line reads as not checked.

## What next

- Before a PR: `/book:self-review`, then `sh devtools/checks/ci-local.sh` at the tier above.
- An FSD section with no rows: the plan that would own it, or a new plan from the template.
- Requirement ids in doubt: `/book:fact-check` on the module.
- **In a flow** (`/book:flow`): `new-fsd-revision` → `/book:sync-sources`; `answers-arrived` → `/book:check-guides`; `new-feature` → `/book:raise`.
