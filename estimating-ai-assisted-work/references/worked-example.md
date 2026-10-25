# Worked example — one team's real numbers (for shape only)

**Do not price another team from these hours.** Measure that team's H and use the ratios. This file shows how the method behaved on a real project and what its outputs looked like.

## The team and its measurement (Tier A)

- **Product:** a multi-tenant B2B operations platform. .NET Web API, PostgreSQL, Clean Architecture and CQRS.
- **Team:** 3–4 backend developers, AI-first (agents write most first drafts and tests).
- **Window:** 6 weeks.
- **`measure_velocity.py` output:** 83 active developer-days × 8h × 1.15 ≈ **764h**; 11% fix commits.
- **Delivered in the window:** about **30 modules**, the platform foundation (tenancy, auditing, auth, file storage, deployment, CI) and 500+ defect fixes.
- **Result: H ≈ 25h per module, rework included.**
- **Measured class costs:**
  - Simple CRUD modules: 1–2 active days (12–24h, about 0.5–1.0 H).
  - Workflow modules with state and cross-module rules: 4–7 active days (32–56h, about 1.3–2.2 H).

## The same team's reference catalogue (two weeks later, 90 developer-days)

`module_catalogue.py` was run over 18 finished modules. The first module built was measured separately as first of its kind. Three modules started within 14 days of the window's end were left out, and so were the infrastructure slices.

| Measure | Value |
|---|---|
| K, CRUD (6 modules) | 1.09 hours per size point |
| K, workflow (10 modules) | 1.68 hours per size point |
| First-of-kind factor F | 2.8 (one module) |
| Platform share α, inside K | 0.42 |
| Spread σ of actual ÷ predicted | 0.34 |
| Single module min / max (P20 / P80) | 0.75 × E / 1.37 × E |
| 80% bid factor, n = 4 / 8 / 16 | 1.14 / 1.10 / 1.07 |
| Spec-to-code factor c | 1.1 (4 plans; 0.96 and 1.62 for the two written before their code) |

**How K × S compared with the ratio table on the same 18 modules, each predicted from the other 17:**

| | Ratio midpoint × H | K × S |
|---|---|---|
| Median error, one module | 30% | 27% |
| Median error, a random 8-module phase | 15% | 9% |
| Predicted total ÷ actual total | 0.93 | 1.00 |

- **One module:** the gain is small. Size explains part of the difference between modules; the rest is noise from requirement changes and from who built the module.
- **A phase:** the gain is larger, because K is fitted to what the team actually spent.
- **Velocity over time:** the team's errors showed no clear trend across the build (correlation −0.23 without the first module), so treating K as a constant held.

**A CRUD module priced with it.** The plan lists 10 endpoints, 2 entities, 12 rules and 4 links:
- S_spec = 20, so S = 1.1 × 20 = 22.
- E = 1.09 × 22 ≈ 24h, reported as 18–33h (24h).
- The closest finished module, at 28.4h for 25.5 points, scales to 24h, so the two agree.

## What went wrong first, and the fix

- **The mistake:** the first estimate of the next phase started from conventional hours with an AI discount. It came to **1,692h BE**, more than 2× the entire measured previous phase.
- **The fix:** rebuilt as ratio × H, it came to **736h BE**, which the team accepted.
- **Buffers:** trimmed from 382h to 324h, only on known-pattern items; external and novel-design buffers were kept.

## Priced rows (H = 25)

These rows were priced **before** the fixed rules (midpoints, quarter points, composite sums) existed, so some of them break those rules. **Copy the shape of the *Current rules* column, not the *As delivered* one.**

| Item | Class and position under current rules | BE as delivered | BE current rules | BE buffer | Mobile | Mobile buffer |
|---|---|---|---|---|---|---|
| Customer portal: new external users + company-level data scoping | New scoping dimension, midpoint 3.25 H | 80 | 81 | 40 | — | — |
| Accounting integration | Two-way integration, upper quarter 3.625 H: no integration foundation in the codebase | 100 (4.0 H, the range's end: not allowed) | 91 | 60 | — | — |
| Legacy data migration (7 domains) | Migration, midpoint 3.25 H | 80 | 81 | 60 | — | — |
| Offline sync, 1–2 workflows | Offline, 3.0 H BE + 5.5 H mobile | 80 | 75 | 40 | 140 → 138 | 70 |
| Notifications with an outbox and scheduler | **Composite**: outbox and its sender (cross-cutting, midpoint 0.75 H) + scheduler (cross-cutting, lower quarter 0.625 H: a mature job-scheduler library) + notification records and preferences (CRUD, midpoint 0.75 H) | 56 (one "workflow, upper" class: 2.24 H, above the range) | 53 | 16 | 24 | 8 |
| 4–5 reports on an existing framework | Read-only aggregates: a count range is priced at the lower number, 4 × 0.4 H | 40 | 40 | 10 | — | — |
| Additional roles from a permissions matrix | CRUD, lower quarter 0.625 H: the role and permission framework exists | 12 (0.48 H, below the range) | 16 | 4 | 4 | 2 |
| Field operations mobile app, 4 workflows | Greenfield mobile: inside the 8–12 H check (9.6 H) | 24 | 24 | 4 | 240 | 80 |

## A sub-feature-level estimate (separate mobile product, same H)

Company, users, invitations, roles and an activity log: 27 sub-features.
- **134h BE + 57h buffer; 121h mobile + 49h buffer.**
- **Conditional implied work:** 48h BE + 12h mobile, for a tenancy retrofit, migration of existing users, email infrastructure and release testing.
- **Per-row figures:**
  - Typical row: 2–8h BE (0.08–0.3 H).
  - Cascade "delete company": 12h.
  - Undefined role permissions: 12h + 12h, with 8h + 8h buffer.

## A small backlog test (same H)

Health records (CRUD with multiple attachments), a breed-registry lookup (read-only external) and a KPI dashboard (3 KPIs):
- **96h BE + 62h buffer; 40h mobile + 25h buffer.**
