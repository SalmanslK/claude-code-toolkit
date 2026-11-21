# What to compare between code and documentation

**Shared by `book:check-docs` and `book:update-docs`.** Both skills walk the same
ground; they differ in what they do on arrival. `book:check-docs` reports a
mismatch without presuming which side is wrong. `book:update-docs` rewrites the
documentation to match, and stops where it cannot be sure the code is right.

Keeping one list means adding a concern here reaches both. Two copies drift, and
the one nobody updated silently stops checking.

**Prefer tracing one real path end to end over skimming ten.** A single flow
followed from endpoint to database finds more than a survey of every file.

---

## Architecture

Project references and dependency direction. The folder tree and class-placement
tables in `docs/architecture.md` §1–§2 — where a class *actually* lives against
where the guide says it goes. The request pipeline and its behaviours, the
interceptors, and the order they run in.

**These drift silently because nothing fails when they do.** No build breaks
because a document describes a folder that was renamed.

## Domain

Aggregates, value objects, invariants, enums and their values, domain events.

Check the vocabulary in `docs/system-overview.md` against real type names. **A
renamed concept surviving in the glossary is how two people end up meaning
different things** — and neither notices, because each is internally consistent.

## Database

Tables, columns, nullability, keys, **indexes and their filters**, unique
constraints and what they are scoped by, migrations against the model snapshot,
and whether `database-scripts/seed/` still matches the schema.

**Index filters are the ones that matter.** A unique index that forgets
`deleted_at IS NULL` or `tenant_id` is a live bug, not a documentation defect —
escalate it rather than writing it down.

## API

Route, method, request and response shapes, status codes, the permission each
endpoint requires, paging, filtering, sorting, error contracts. Compare against
the API surface tables in the feature plans, and a built module's FE guide in
`docs/fe-integration-guides/` — its error codes and messages, and whether each *Deviations*
row is still true and still explained. **A response-only change regenerates nothing
`check-fe-guides.py` can see**, so only this comparison finds a guide it left stale.

## Flows

Trace the real path:

```
endpoint → ISender → behaviours → handler → domain → repository
        → SaveChangesAsync → interceptors → domain events
```

**Follow the path the code takes, not the one the architecture implies.** The gap
between those two is where the interesting findings are.

## Cross-cutting behaviour

Soft delete, tenancy and tenant scoping, auditing, authorization, validation, rate
limiting, health probes.

Each is enforced centrally, so **a gap is invisible until it matters**. Check that
the central mechanism is applied to everything it claims to cover, not that it
exists.

## Status and state

Enums, allowed transitions, terminal states, and the rules guarding them.

## Configuration and deployment

`appsettings` keys against the options classes and their validators. The runbook
against the Compose files and the Dockerfile. Environment names — matched exactly,
and case-sensitive on Linux.

## Tests

`UnitTests` for domain rules, `ArchitectureTests` for the guardrails,
`IntegrationTests` for anything touching a database.

**Test names in this repository are sentences.** Read them — they state intended
behaviour more plainly than most comments, which makes them unusually good
evidence of intent.

## Diagrams

Every diagram in `docs/`. Verify the components exist, the relationships hold, the
order is right, the names match, and every Mermaid block parses.

**A deliberately simplified conceptual diagram is not a defect.** Say so rather
than replacing it with implementation detail.

---

## Numbers

**Measure them. Do not carry them forward.**

Test counts, feature counts, question counts and branch state are the
most-quoted and least-checked facts in this repository, and they have been wrong
more than once — including by arithmetic that looked reasonable. Run the suite and
read the total. Count the rows. Check `git log`.

**Where a tool prints the real number, take it from the tool, not a grep:**

| A doc states | The real number |
|---|---|
| Tests defined (`[Fact]`/`[Theory]` methods) | `python3 devtools/checks/test-trend.py` — its last line, the count on `origin/dev` today (`git fetch` first) |
| Routes and endpoint groups | `python3 devtools/checks/gen-api-contracts.py --check`; when it says up to date, the **N routes across M endpoint groups** line of `docs/api/api-contracts.md` is current |
| Modules | `git grep -c "^\[\[modules\]\]" devtools/factory/factory.toml` — the modules `book impact` maps |

No tool prints a run's **executed, passed or skipped** counts without running it — theories
expand and the integration tests may skip — so a doc quoting a run is checked against a run
(`dotnet test`, or `ci-local.sh`'s summary), as above. Question, defect and feature counts are
counted from their rows.

**A count you did not verify this pass is a count you must not write.** When the suite
cannot run — no database for them (the dotnet pack: Docker, or `[deploy] test_db_variable`), so the integration tests skip — the finding
is `could not check`, never the last known number.

---

## Where drift has actually happened

Not a list to pad a report with. These are the places this repository has been
bitten, or would be hurt most.

- **Tenancy and tenant scoping.** Every aggregate tenant-scoped, the architecture
  test's allow-list, unique indexes leading with `tenant_id`, the query filters,
  and the scoping marker on anything that belongs to one tenant
  (architecture, *Tenancy* (the architecture guide's tenancy section)). **A gap here is a
  cross-customer or cross-tenant data leak** — treat any finding as Critical until proven otherwise.
- **Soft delete versus inactive.** Two different things that look identical in the
  database. Conflating them has caused rework twice.
- **Authorization.** The `Permissions` catalogue and the seeded roles against
  `docs/plans/authorization.md` §2 (the project's plan),
  which is drawn from the FSD — no permissions matrix exists (CLAUDE.md *Layout*) — and the
  default-deny behaviour of a permission no role holds.
- **Migrations against the model snapshot.**
- **Feature plans versus what shipped**, especially anything still marked
  `[PROPOSED]` that has since been built or dropped.
- **Question numbering and counts** in `docs/open-questions.md` — every question in
  exactly one section, statuses matching placement, totals adding up.
- **The deployment runbook** against the actual Compose files and Dockerfile.
