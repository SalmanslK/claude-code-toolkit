# B0 · Pass B, stack-free — dimensions 2–12 (checks 16–161)

The Book's own Pass B: every correctness dimension in one file, written for no particular stack. `factory review-scope` loads it (`[review_scope.dimensions] B0`) unless the change is docs or requirements only. A stack pack replaces it with one file per dimension — the dotnet pack's `review-b1-architecture.md` … `review-b11-configuration.md` — and its own `[review_scope]` rows. The [method](review-method.md) holds the finding format, severity and the READY rule.

Work through the dimensions below in the order that matches what the diff
touches; read the diff, decide which can plausibly break, and press hardest
there. **Record every dimension you didn't press on as N/A in the
coverage summary ([review-method.md](review-method.md)) rather than leaving it unsaid.** Then
apply the stack checks (the stack pack's dimensions, B1 onwards, where one is installed).

## Principles

**Understand before judging.** Read the diff, then the surrounding code, then
trace the execution path. A finding raised from the diff alone is a guess.

**The project's architecture is the standard, not general best practice.**
Where the project's `CLAUDE.md`, its architecture guide or a plan in
`docs/plans/` has already decided something, that decision wins. A pattern is
not wrong merely because another pattern exists.

**Do not propose rewrites.** Review what is there. Structural change is a
finding only when it fixes a real defect or the architecture requires it.

**Distinguish a defect from a preference.** Correctness, security, data
integrity and architecture violations are findings. Everything else is a
suggestion, and suggestions do not go inline on a PR.

---

## B1 · Architecture & Design — checks 16–33

| # | Check | Apply it here |
|---|---|---|
| 16 | Architectural layer boundary violation | The layering the project's `CLAUDE.md` states. If an architecture test enforces it, check whether the suspected violation is one the test would already have caught — if so the concern is elsewhere |
| 17 | Incorrect dependency direction | Same as above, checked from the other end |
| 18 | Domain depending on infrastructure concerns | Business rules reaching for the database driver, the web framework, the file system or the clock directly |
| 19 | Business logic in API/endpoints | An endpoint, controller or route handler deciding business rules instead of dispatching and mapping the result |
| 20 | Business logic in the persistence layer | A repository or data-access method that does more than fetch/save is doing the handler's job |
| 21 | Business logic duplicated across layers | The same rule re-implemented in a validator and a domain method, silently able to drift |
| 22 | Incorrect responsibility assignment | Is this handler/service/repository doing what its name says, or has scope crept in? |
| 23 | SRP violation | A class or module with more than one reason to change |
| 24 | OCP violation | Only worth raising with a concrete extension the current design can't accommodate — not "could be more open" in the abstract |
| 25 | LSP violation | A derived type that narrows a contract its base promises |
| 26 | ISP violation | A consumer forced to depend on members it never uses |
| 27 | DIP violation | A high-level module depending on a concrete low-level one instead of an abstraction |
| 28 | Circular dependency | Between packages/projects or between classes within one |
| 29 | Excessive coupling | Changing one class forces edits across many unrelated ones |
| 30 | Inappropriate inheritance | Used for code reuse rather than a genuine is-a relationship |
| 31 | Missing composition where appropriate | Only where inheritance is visibly straining |
| 32 | Incorrect aggregate/entity boundaries | A write path that lets callers modify a child without going through the owner that guards its invariants |
| 33 | Inappropriate abstraction / premature generalization | An interface or base class with no second implementer in sight |

---

## B2 · Code Quality & Maintainability — checks 34–48, 161

| # | Check | Apply it here |
|---|---|---|
| 34 | Duplicated code | Especially business rules re-typed rather than shared |
| 35 | Unnecessary complexity | A simpler shape already exists elsewhere in the codebase for the same problem |
| 36 | Excessively complex method | Deep branching, many responsibilities in one function |
| 37 | Excessively complex class | Same, at class or module scope |
| 38 | Excessive nesting | Prefer early returns / guard clauses over pyramids |
| 39 | Poor naming | Names must say what the thing is, per the project's naming rules |
| 40 | Misleading naming | Name promises one thing, code does another |
| 41 | Unclear control flow | Hard to trace what runs when, especially across async/event boundaries |
| 42 | Magic numbers or strings | Unnamed literals carrying meaning; configuration read by raw key string where the project uses typed settings |
| 43 | Dead code | Unreachable branches, unused parameters, leftover scaffolding, commented-out code |
| 44 | Unnecessary variables | Intermediate locals that add no clarity |
| 45 | Unnecessary abstraction | An interface, wrapper, or layer that exists but adds no substitutability or testability |
| 46 | Inconsistent coding patterns | The change solves a problem differently from how the codebase already solves it, with no reason given |
| 47 | Poor separation of concerns | Grab-bag names (`Helper`, `Manager`, `Utils`, `Common`) are a symptom of unassigned responsibility — check the project's own banned-name list |
| 48 | Code difficult to safely modify or extend | Would a reasonable next change require touching many unrelated places? |
| 161 | Code the requirement did not ask for | An option, setting, parameter or extension point no criterion needs; a wrapper that only renames a library call; a "while I was here" change outside the Spec's scope. Name the criterion it serves, or it is a finding — the fix is to delete it, or to take it to its own tracked change |

---

## B3 · API & Contracts — checks 49–60

| # | Check | Apply it here |
|---|---|---|
| 49 | Incorrect HTTP method | GET for reads, POST for creation/actions, PUT/PATCH for updates, DELETE for removal — or the project's own convention |
| 50 | Incorrect HTTP status code | 201 on create, 204 vs 200 on update, 404 vs 403 (a resource outside the caller's scope often correctly answers 404) |
| 51 | Inconsistent API response contract | Enum, date and null serialisation matching what sibling endpoints already do — verify, don't assume |
| 52 | Inconsistent error contract | Failures should map to the same error shape other endpoints already use |
| 53 | Missing request validation | Every input the code trusts without a validator or guard |
| 54 | Incorrect request validation | Validation in the wrong layer is often *also* validation that's wrong — shape checks, checks that need the database, and domain invariants each belong where the project puts them |
| 55 | Returning unnecessary data | List/dropdown responses carrying detail-only fields |
| 56 | Exposing internal implementation details | Stack traces, internal ids not meant for the client, raw database or framework error messages |
| 57 | Exposing sensitive information | Password hashes, tokens, other tenants' or customers' data |
| 58 | Incorrect resource/route design | Nesting, pluralisation, and verbs-as-nouns consistent with sibling endpoints |
| 59 | Unbounded collection endpoint | Every list must page; a caller-chosen sort field goes through an explicit allow-list, never reflection or string-built SQL |
| 60 | Incorrect API compatibility/versioning behaviour | A changed response shape or removed field breaking a contract a consumer or integration guide relies on |

---

## B4 · Security — checks 61–80

| # | Check | Apply it here |
|---|---|---|
| 61 | SQL injection | Any raw SQL built by string concatenation or interpolation of caller input, in queries or migrations |
| 62 | Command injection | Any shell-out built from caller input |
| 63 | Path traversal | Any code building a file path from caller input |
| 64 | SSRF | Any outbound call built from a caller-supplied host or URL |
| 65 | Cross-site scripting | Caller-controlled text rendered unescaped into HTML, email templates included — unless the project records it as a decision |
| 66 | CSRF where applicable | Relevant where cookie-based authentication is in play |
| 67 | Insecure deserialization | Deserialising untrusted data into arbitrary types, or trusting a client-supplied type name |
| 68 | Unsafe file upload | Trust the bytes, not the file name or declared content type |
| 69 | Missing upload size/type restrictions | Every upload path needs bounds |
| 70 | Hardcoded secrets | Anything in a committed file that isn't a recognisable placeholder |
| 71 | Secrets exposed through source/configuration | Real values in tracked settings files, fixtures, scripts or CI config |
| 72 | Secrets exposed through logs/telemetry | Never log passwords, hashes, tokens, reset/invitation links, connection strings, customer-identifying data |
| 73 | Weak password handling | Hashing algorithm, complexity rules, comparison method (constant-time where relevant) |
| 74 | Incorrect credential/token handling | Refresh rotation, invalidation on password change or deactivation |
| 75 | Incorrect token validation | Issuer/audience/lifetime/signature checks all present; signing key not a placeholder |
| 76 | Broken authentication | A new code path that bypasses the project's authentication middleware or current-user resolution |
| 77 | Broken authorization | Is authorization default-deny here? Scrutinise every anonymous or opt-out marker. A new gated operation needs its permission granted where the project defines permissions *and* a test asserting it |
| 78 | IDOR/BOLA/resource ownership | Can the caller supply an id for a resource that isn't theirs and get it back — or change it? |
| 79 | Privilege escalation | Can a lower role reach a privileged action through a side path — a list filter, a bulk endpoint, a nested resource |
| 80 | Cross-tenant data access — **treat as CRITICAL by default** (multi-tenant systems) | Can a query return another tenant's rows? Is a global filter bypassed, and if so is scoping re-applied by hand? Is scoping applied on **writes as well as reads** — a scoped list with an unscoped fetch-for-update is an IDOR with a tidy front end |

---

## B5 · Data & Database — checks 81–98

| # | Check | Apply it here |
|---|---|---|
| 81 | N+1 query | Any loop that queries per iteration instead of a single set-based query |
| 82 | Unnecessary database query | A lookup the caller already had, or a second query re-hitting the same table for something the first returned |
| 83 | Duplicate database query | Same query run twice for two different checks that could share one result |
| 84 | Database query inside an avoidable loop | Same root cause as 81 — file once |
| 85 | Loading excessive data | Full rows or object graphs loaded where a projection would do |
| 86 | Filtering performed in application instead of database | Filtering, sorting or paging after materialising the result set |
| 87 | Missing database-level pagination | Hand-rolled paging, or paging in memory, where the project has a shared paging mechanism |
| 88 | Missing required index | Any new frequent filter/sort column with nothing backing it |
| 89 | Incorrect or ineffective index | A unique index that ignores tenant scoping or soft-deleted rows, so a deleted record holds its unique value forever |
| 90 | Inefficient join/query | A query shape that forces the database to do much more work than the result needs |
| 91 | Incorrect ORM tracking/session behaviour | Read paths paying for change tracking; a write path whose changes are never tracked and silently no-op on save |
| 92 | Excessive eager loading | Related data pulled that the query doesn't need |
| 93 | Inefficient projection | Mapping done in application code after a full load where the query could project |
| 94 | Incorrect transaction boundary | Does the unit of work match the business operation, not the code's convenience? |
| 95 | Missing transaction where atomicity is required | Two writes that must succeed together, committed separately |
| 96 | Missing concurrency protection | No optimistic concurrency token (or lock) on a row multiple actors can race to update |
| 97 | Missing database constraint/invariant | An invariant enforced only in code with nothing backing it at the schema level |
| 98 | Unsafe schema/migration change | Editing an already-applied migration; a destructive change without a data path; raw SQL in a migration that is not idempotent or not proven the way the project requires |

---

## B6 · Performance & Scalability — checks 99–110

| # | Check | Apply it here |
|---|---|---|
| 99 | Blocking operation on the request path | Blocking on async work, or a synchronous file/network call on a request thread |
| 100 | Sync-over-async | Same root cause as 99 |
| 101 | Unnecessary offloading to a thread/worker | Wrapping already-async work, or offloading CPU-light work that gains nothing |
| 102 | Excessive memory allocation | Large materialisations of data that could be streamed |
| 103 | Potential memory leak | Undisposed resources, handlers never unsubscribed, growing static collections (also *check 112/113*) |
| 104 | Repeated expensive computation | Recomputing something per-request that doesn't change per-request |
| 105 | Missing appropriate caching | Only worth raising with a concrete, credible hot path — not speculative |
| 106 | Incorrect caching strategy | **Cache invalidation** is the usual failure: does it happen, and does it happen *before or after* the commit it's invalidating? |
| 107 | Excessive network calls | Multiple round trips where one would do |
| 108 | Sequential independent I/O that should be parallelized | Independent awaits chained where they could run together |
| 109 | Excessive payload size | A response carrying fields no client needs (ties to *check 55*) |
| 110 | Operation does not scale with expected data volume | A list operation's query count should be **fixed**, not proportional to row count — if the project has a query-counting test pattern, a new list endpoint should use it |

**Raise a performance finding only where the impact is credible at realistic
volume** — this project's own scale, not a hypothetical.

---

## B7 · Async & Concurrency — checks 111–120

| # | Check | Apply it here |
|---|---|---|
| 111 | Race condition | Two requests that can interleave and leave inconsistent state |
| 112 | Unsafe shared mutable state | Static or global mutable state reachable from concurrent requests |
| 113 | Thread-unsafe collection/state | A non-concurrent collection touched from more than one request context |
| 114 | Incorrect locking | Lock scope too broad/narrow, or a lock around something that doesn't need one |
| 115 | Potential deadlock | Nested locks in inconsistent order, or blocking-on-async inside a lock |
| 116 | Fire-and-forget operation without controlled lifecycle | Work started with nothing owning its failure or shutdown; an external side effect (email, HTTP) fired from inside a transaction or event handler that can still roll back |
| 117 | Unobserved asynchronous failure | A task/promise started and not awaited, whose exception disappears |
| 118 | Cancellation ignored | A cancellation signal accepted and dropped, or replaced with "never cancel" in product code |
| 119 | Cancellation not propagated | A signal accepted by a handler but not passed to the data-access or HTTP call beneath it |
| 120 | Incorrect concurrent processing/duplicate execution | A block that a retry policy may run more than once, doing something that must happen once (cross-reference *check 12*, don't double-report the same root cause) |

---

## B8 · Error Handling & Resilience — checks 121–132

| # | Check | Apply it here |
|---|---|---|
| 121 | Exception swallowed | A catch that neither recovers nor reports — unless it matches a recorded, deliberate best-effort pattern in the project |
| 122 | Overly broad exception handling | Catching every exception where a narrower type was available and meaningful |
| 123 | Exception caught without meaningful recovery | A catch block that logs and rethrows the same thing, adding nothing |
| 124 | Original exception context lost | Rethrowing in a way that resets the stack, or wrapping without the inner exception |
| 125 | Generic/meaningless exception | A raw generic exception where a domain-specific error or an expected-failure result was called for |
| 126 | Sensitive information exposed through errors | Stack traces or internal messages reaching the client (ties to *check 56*) |
| 127 | Inconsistent exception-to-response mapping | Expected failures and faults handled the way the project separates them (result types vs exceptions, or its equivalent) |
| 128 | Missing centralized error handling | Code doing its own error-to-response translation instead of the project's central handler |
| 129 | Missing timeout for external operation | Any HTTP/SMTP/storage call with no bound |
| 130 | Incorrect retry strategy | Retrying a non-idempotent operation, or retrying indefinitely |
| 131 | Missing retry/backoff for transient failure | Only worth raising where the failure mode is realistic and the operation is safe to retry |
| 132 | External dependency failure not handled safely | A failed external call must not leave inconsistent local state — what happens to the already-committed row when the call after it fails? |

---

## B9 · Testing — checks 133–147

| # | Check | Apply it here |
|---|---|---|
| 133 | Missing test for core business behaviour | The rule the requirements name, not incidental code around it |
| 134 | Missing negative-path test | Invalid input, forbidden transition, wrong actor |
| 135 | Missing edge-case test | Boundary values, empty collections, first/last page |
| 136 | Missing validation test | Each validation rule exercised at least once |
| 137 | Missing authorization test | **Always qualifies** for security-critical logic — a new gated operation needs a test asserting who may and may not reach it |
| 138 | Missing isolation test | **Always qualifies** in a multi-tenant system — cross-tenant leakage is Critical, and an entity without a two-tenant test is unverified on the one thing that matters most |
| 139 | Missing integration test where integration behaviour matters | Query shape, filter interaction, transaction behaviour — none of this is provable by a unit test with the database mocked |
| 140 | Missing persistence/database test where database behaviour matters | Constraint, index, migration behaviour against the real database engine |
| 141 | Missing concurrency test where concurrency matters | Optimistic concurrency, idempotent retry — only where the change introduces one of these |
| 142 | Missing regression test for fixed defect | Reference the defect id in the test name or nearby, per the defect log's convention |
| 143 | Test verifies implementation instead of behaviour | Asserting a computed value against the constant that produced it proves the wiring, not the requirement's specified value |
| 144 | Test has weak or meaningless assertions | Asserting "no exception thrown" or a non-null result where the actual value matters |
| 145 | Test depends on fragile setup/state | Shared mutable fixtures, ordering-dependent tests |
| 146 | Test unnecessarily coupled to external services | A unit test that shouldn't need a database or network but does |
| 147 | Test suite does not adequately prove the requirement | Green tests that, read together, still leave a stated requirement unverified |

**Check the skip count, not the colour.** Tests that need a database or a
service often skip silently when it is missing, and a filter that matches
nothing runs nothing — a run that executed nothing looks identical to one that
passed. In a factory run, the run file records which tests prove each
criterion and that they ran; trust that evidence unless you can show it is
wrong.

---

## B10 · Observability & Operations — checks 148–155

| # | Check | Apply it here |
|---|---|---|
| 148 | Missing meaningful logging | A failure path (especially a swallowed exception, *check 121*) with nothing recorded |
| 149 | Incorrect log level | Expected/handled conditions logged as Error; real faults logged as Information |
| 150 | Sensitive data logged | Same list as *check 72* — passwords, hashes, tokens, reset/invitation links, connection strings, customer data |
| 151 | Insufficient diagnostic context | A log line with no id, no tenant, no correlating value — nothing to search on later |
| 152 | Missing structured logging | Interpolated strings where structured fields were available and would make the log queryable |
| 153 | Missing metrics for important operational behaviour | If the project has no metrics infrastructure decided, treat as **INFO**, not Medium/High, unless a plan committed to metrics for the touched area |
| 154 | Missing tracing/correlation for distributed operations | Same caveat as 153 |
| 155 | Failure cannot be diagnosed effectively in production | The combined effect of 148–152: if this specific failure happened in a shared environment right now, is there enough in the logs to find it? |

---

## B11 · Configuration & Dependencies — checks 156–160

| # | Check | Apply it here |
|---|---|---|
| 156 | Hardcoded environment-specific configuration | A safety-relevant behaviour gated only on an environment name, not also on an explicit setting; environment names spelled differently from what the deployment uses |
| 157 | Unsafe/default configuration | A placeholder that startup validation cannot recognise as a placeholder, so the app boots with a real-looking but wrong value |
| 158 | Configuration not validated at startup/use | A setting read ad hoc, bypassing the project's validated settings mechanism |
| 159 | Unnecessary or inappropriate dependency | Reinventing is a last resort; conversely, a new dependency for something the codebase already does in ten lines is also a finding. A licence-sensitive dependency needs whatever record the project requires before it is added |
| 160 | Dependency/version introduces known compatibility or security risk | Versions pinned where the project pins them. If CI already scans for vulnerable packages, only flag this here if the change is what *introduced* the vulnerable version |

---
