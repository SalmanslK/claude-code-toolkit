# Review checklist — the method

What to look for, and how hard to press. Owned by
[`../SKILL.md`](../SKILL.md) — **add a new concern here, not to either skill
body.** Shared with [`/book:self-review`](../../self-review/SKILL.md), which runs
this same framework locally against a branch instead of an open PR — the same
sharing pattern `book:check-docs` and `book:update-docs` already use for
`comparison-checklist.md`.

The checklist is in parts, so a review loads only what its change can touch: this **method**,
[Pass A](review-pass-a.md) (always), and one file per Pass B dimension, listed under
[Pass B](#pass-b--correctness--dimensions-212-checks-16161). **`book review-scope` names the
parts a change needs** — this file and Pass A always, and every Pass B file when it cannot place a
path. A dimension not loaded is still a row in the [coverage table](#coverage-summary).

Together the parts are the **internal coverage framework**: 161 named checks across 12
review dimensions. It is not a form to fill in and not a source of findings by
itself — **a check earns a finding only when the diff gives evidence for it.**
Work through every applicable dimension on every review; report only what the
evidence supports.

---

## How to use this framework

**1. Scope first.** Read the diff's shape — which projects, which layers,
what kind of change (endpoint, migration, background job, config) — before
opening the checklist. That tells you which of the 12 dimensions can
plausibly apply. A DTO rename touches Code Quality and API & Contracts; it
does not touch Async & Concurrency or database migrations. **Record a
dimension as N/A explicitly rather than silently skipping it** — "N/A: no
async code in this diff" tells the next reader it was considered, not missed.
See [Coverage summary](#coverage-summary).

Classify by path — `git diff --name-only` — before reading any changed file. A
path or diff that matches several rows presses every row's dimensions; a
dimension is N/A only when every matching row lists it so. Markdown under
`.claude/` (skills, agents) is *Tooling*, read like *Docs* — at its changed
sections:

| The diff touches | Press hardest on | Read | Normally N/A |
|---|---|---|---|
| Product code under `src/` | Pass A in full; the B dimensions of the layers touched | Each changed file in full, its nearest sibling, the plan's section for it | — |
| An endpoint, request/response DTO or permission | B3 API, B4 Security; A3 (FE guide, `api-contracts.md`, Postman `JOURNEY`) | the API project's `CLAUDE.md` (the dotnet pack: `src/<Name>.API/CLAUDE.md`, `<Name>` being the project's own name — find it with Glob `src/*.API/CLAUDE.md`) | — |
| A migration | B5 Data; the idempotent-script proof | The migration's `.cs` in full; `Persistence/CLAUDE.md` (the dotnet pack) | — |
| Tests only | B9 Testing; whether each test proves the behaviour its name claims | The tests and the code they exercise | B1–B8 unless the tests reveal a product defect |
| Docs only (`docs/`, other `*.md`) | A2, A3: does each changed statement match the code and the FSD, in the doc that owns it | The changed sections; their owner per *Where knowledge lives* (the project's `CLAUDE.md`) | B1–B11 — say so in the coverage table |
| Tooling (`devtools/`, `.claude/`, `.githooks/`, CI) | B2, B4 (secrets, what it can reach), B10, B11; whether the tool's own tests cover the change | The changed files in full; the tool's tests | A1 unless it changes what ships; B1, B3, B5 — they check the .NET layers, endpoints and EF Core, which tooling does not hold (a tool that generates them, such as `gen-api-contracts`, is still Tooling) |
| A `CLAUDE.md` (root or nested) | As *Tooling*: B4, B11 — they are rules the guard and checks enforce; and A2 against the docs that own each topic | The changed sections | — |
| `requirements/**` | Only that the read-only rule held: a new snapshot file; a tracker's current copy replaced with its predecessor added under `backup/`; a `read-me.txt` link, *Last checked* line, or standing rule that a recorded decision changed — never an edit to an existing snapshot or backup | The diff | Everything else — the client's content is not ours to review |
| `database-scripts/`, `scripts/` | B5 Data (seed scripts idempotent; fixes dated, never schema), B10; `scripts/backup-database.sh` must not move (cron calls it by absolute path) | The changed scripts in full | — |
| Root build and deploy config — `Directory.Packages.props`, `compose*.yaml`, `Dockerfile`, `appsettings*.json`, `bitbucket-pipelines.yml` | B4 Security, B11 Configuration; licences and the `REPLACE` placeholder rule | The changed files in full | — |
| Generated files — `docs/api/api-contracts.md`, `docs/database-erd.md`, a migration's `.Designer.cs`, the model snapshot | Only that they were regenerated with their source | The diff, never the whole file | Everything else — review the source they came from |

`book review-scope` applies this table to the change's paths; its rows are `[[review_scope.rows]]`
in `devtools/factory/factory.toml`, held to this table by a test, so a row changes in both.

**Pass A still runs on every diff.** On one with no product code, A1 reduces
to checking that what the changed text says about a requirement matches the
FSD.

**2. Evaluate every applicable check mentally.** For each dimension the diff
touches, run down its checks below. Most resolve instantly — "no state
transition here", "no external call here" — and leave nothing behind. That is
the correct, common outcome. **Evaluating 161 checks does not mean producing
161 findings; it means not missing the one that matters because nobody
looked.**

**3. A check becomes a finding only with evidence.** Point at the line, the
test that's missing, the migration that isn't idempotent, the requirement
sentence nothing in the diff satisfies. "This might not scale" with nothing
behind it is not a finding — it is a hunch, and a hunch goes in the terminal
review as a question, never onto a PR or into a verdict as a defect.

**4. Tag every finding New or Pre-existing.** A defect the diff introduces and
a defect the diff merely touches, extends, or newly exposes are both worth
reporting, but they are not the same claim:

- **New** — the diff itself created this defect. Did not exist on the base
  branch.
- **Pre-existing** — the code already had this defect; the diff walks past it,
  extends it, calls it from a new place, or makes it reachable in a way it
  wasn't before. Report it, but don't describe it as something this PR did.

Check `git diff <base>...<head>` for whether the offending line is `+` or
context before deciding. Don't blame the PR for a line it didn't touch; don't
excuse the PR from a defect on a line it added because "the pattern already
existed elsewhere."

**5. Report only what survives.** See [Anti-noise rules](#anti-noise-rules)
and [Before a finding is reported](#before-a-finding-is-reported).

---

## Anti-noise rules

These aren't style preferences — violating them is a defect in the review
itself, not a matter of taste:

- **Never manufacture a finding to justify having run the framework.** A
  clean dimension is a legitimate, reportable result: "Security: evaluated,
  no findings" is worth more than an invented Low.
- **Never report a check just because it appears in the tables below.**
  Applicability first, evidence second, report third.
- **Never report the same root cause twice under two dimensions.** A missing
  transaction around two related saves is one finding, not a Data & Database
  finding *and* an Error Handling finding. File it once, under whichever
  dimension the fix actually belongs to, and fold the secondary angle into
  that finding's "why it matters" rather than opening a second entry.
- **Never flag a theoretical vulnerability with no credible execution path.**
  If exploiting it requires a caller that cannot exist given the endpoint's
  auth, the DTO's shape, or the platform, say why it isn't reachable and move
  on — don't report it "to be safe."
- **Never recommend a rewrite because another architecture is possible.**
  Structural change is a finding only when it fixes evidence of an actual
  defect, or the project's own rules (`CLAUDE.md`, `docs/architecture.md`, a
  plan in `docs/plans/`) require it.
- **Never recommend introducing a new abstraction, interface, or layer as
  part of a fix unless the defect itself requires it.** The same restraint
  that applies to reviewing existing code (*check 33*) applies to the fix you
  propose for it.
- **Never treat a stylistic preference as a defect.** If the codebase has no
  established convention on it, it isn't reportable at any severity.
- **Never demand a test that adds no confidence.** A test that re-asserts the
  framework, or duplicates an existing test with different data, is not a
  gap.
- **Never inflate or deflate severity to make a point.** See
  [Severity](#severity) — a Medium reported as Critical costs the next real
  Critical its urgency; a Critical softened to read comfortably is worse than
  skipping the review.

---

## Finding format

Every reported finding — inline, terminal, or written report — carries:

| Field | |
|---|---|
| **Severity** | CRITICAL / HIGH / MEDIUM / LOW / INFO — see [Severity](#severity) |
| **Title** | One line naming the defect, not the file |
| **Location** | Exact file path and line, or the honest anchor when there is no single line (see [book:peer-review's Step 5](../SKILL.md#step-5--post)) |
| **New or Pre-existing** | Per [How to use this framework, §4](#how-to-use-this-framework) |
| **What's wrong** | The defect, stated plainly |
| **Why it matters** | The concrete failure it causes — an input, a sequence, a load — never "could be an issue" |
| **Evidence** | The line, the test result, the doc citation, or the trace that supports the claim. This is what separates a finding from a suspicion |
| **Recommendation** | What to change, in one or two sentences — not a rewritten implementation |

Inline PR comments compress *what's wrong / why it matters / evidence* into
one short paragraph (see [Comment format](../SKILL.md#comment-format)) because
the code sits right beside the comment and is itself the evidence. A terminal
or written report keeps the fields separate since there's no code column
beside it.

---

## Severity

| | Means | Examples |
|---|---|---|
| 🔴 **CRITICAL** | Must be fixed before merge | Security vulnerability, data corruption or loss, cross-tenant data access, authorization bypass, production-breaking correctness |
| 🟠 **HIGH** | Should be fixed before merge | Significant business-logic defect, transaction/concurrency bug, major architecture violation, serious performance/scalability issue, critical missing test coverage |
| 🟡 **MEDIUM** | Address, need not block | Real maintainability cost, resilience gap, design smell, thin test coverage, meaningful performance concern below Critical/High scale |
| 🔵 **LOW** | Minor | Small inconsistency, limited-impact quality issue |
| 💡 **INFO** | Not a defect | Useful observation — terminal/report only, **never posted inline on a PR** |

**Do not inflate.** A Medium reported as Critical costs the next real
Critical its urgency. **Do not deflate either** — a security finding softened
to fit a comfortable review is worse than not reviewing.

### The verdict block — every review ends with it

`/book:self-review` and `/book:peer-review` (in its report) both end with this
block, in this exact shape, so a person reads every review the same way — one
line per finding, the severities above, and how sure you are:

```
Verdict: READY | NOT READY
Findings:
- [CRITICAL|HIGH|MEDIUM|LOW|INFO] [high|medium|low] path:line — what is wrong, and why
What is sound: one or two lines.
```

- **NOT READY** when any CRITICAL or HIGH finding is held with high or medium confidence.
  **This is the one READY rule**: `/book:self-review`'s *Branch Readiness* line and `/book:peer-review`'s
  verdict both follow it, and `/book:commit` and `book pr open` act on what it decides.
- A **low**-confidence finding is advisory: never a reason for NOT READY. Low confidence means the
  evidence points at a defect without settling it; a suspicion with no evidence is not a finding at
  all, but a question in the terminal review ([Before a finding is reported](#before-a-finding-is-reported)).
- No findings: `Findings:` then `- none`. The full write-up of each finding stays above the block.

### Conformance findings specifically

Pass A produces a kind of finding the table above doesn't obviously cover:

| Situation | Severity |
|---|---|
| A specified requirement central to the feature is absent | 🟠 **HIGH** — the feature is not finished, whatever the code quality |
| A specified requirement is absent and **nothing owns it** — the deferral names a plan or phase that does not exist | 🟡 **MEDIUM**, anchored on whatever should have carried the requirement |
| A specified requirement is absent with a **real** owner and landing place | **Not a finding.** It is a decision |
| A doc the PR invalidated was not updated in the PR | 🟡 **MEDIUM** — 🟠 **HIGH** for a `fe-integration-guides/` file, which another team acts on |
| Code and a doc contradict, and the FSD does not settle it | 🟡 **MEDIUM**, phrased as a question — do not pick a side quietly |

**And do not let a clean Pass A go unsaid.** "Not a finding" is still a
result and belongs in the conformance table.

---

## Coverage summary

Every review — terminal or written; never a PR comment — closes with
one line per dimension, covering whichever dimensions actually applied:

```markdown
### Coverage

| Dimension | Result |
|---|---|
| Requirements & Business Logic | Evaluated — 1 finding |
| Architecture & Design | Evaluated — clean |
| Code Quality & Maintainability | Evaluated — 2 findings |
| API & Contracts | N/A — no API surface changed |
| Security | Evaluated — clean |
| Data & Database | Evaluated — 1 finding |
| Performance & Scalability | N/A — no query or loop changes |
| Async & Concurrency | N/A — no async code touched |
| Error Handling & Resilience | Evaluated — clean |
| Testing | Evaluated — 1 finding |
| Observability & Operations | Evaluated — clean |
| Configuration & Dependencies | N/A — no config or package changes |
```

This is a **summary**, not the 161-item list — never paste the full framework
into a report or a PR comment (only into this file). Its purpose is letting
the next reader tell "checked and clean" apart from "not applicable" apart
from "never looked" — the same reason Pass A's conformance table records
passing sections rather than only failing ones.

---

## Before either pass — what already counts as a finding

**Knowing about a defect is not reporting it.** Both passes below assume
findings come from reading the diff. A defect you already knew about before
the review started never travels that path, so it is silently exempt from
every rule here — and those are the ones most likely to be dropped, because
familiarity reads as resolution.

So before Pass A, list what you already know is wrong with this code from any
source: earlier conversation with the user, a previous run, a `docs/plans/`
entry, a note in `docs/project.md`. **Each one is a candidate finding and has
to earn a severity, an anchor, and a New/Pre-existing tag exactly like a
fresh one.**

Three phrases to distrust in your own reasoning:

| You are about to think | What is actually true |
|---|---|
| *"already reported"* | Reported **to whom?** The audience is the PR's author or the branch's owner, not the person you've been talking to |
| *"already known"* | Known to you. The author has not read your conversation |
| *"already on the list"* | A list the author cannot see is not a report |

**And a finding mentioned inside another comment has not been reported.** An
aside at the end of a comment about something else — *"the underlying
inconsistency is already on the list"* — makes the issue feel handled while
leaving it invisible. It gets its own comment, on its own line, or it does
not exist.

---

## Pass B — Correctness — Dimensions 2–12 (checks 16–161)

Work through the dimensions below in the order that matches what the diff
touches; read the diff, decide which can plausibly break, and press hardest
there. **Record every dimension you didn't press on as N/A in the
[Coverage summary](#coverage-summary) rather than leaving it unsaid.**

Without a stack pack the dimensions are one stack-free file, `review-b-core.md` (B0, checks 16–161). A stack pack may split them into one file per dimension in its place (the dotnet pack's `review-b1-architecture.md` … `review-b11-configuration.md`; a pack's files that stop at check 160 lack 161, *Code the requirement did not ask for*: apply it from B2 in `review-b-core.md`, beside this file). `[review_scope.dimensions]` in `factory.toml` names the files this Book has.

### Principles

**Understand before judging.** Read the diff, then the surrounding code, then
trace the execution path. A finding raised from the diff alone is a guess.

**The project's architecture is the standard, not general best practice.**
Where `CLAUDE.md`,
`docs/architecture.md` or a plan in
`docs/plans/` has already decided something, that decision wins. A pattern is
not wrong merely because another pattern exists. **A change to product or test
code: read `src/CLAUDE.md`, the code rules, before
reviewing it** — it loads by itself only when a file under `src/` is opened, and
a review from a diff may open none.

**Do not propose rewrites.** Review what is there. Structural change is a
finding only when it fixes a real defect or the architecture requires it.

**Distinguish a defect from a preference.** Correctness, security, data
integrity and architecture violations are findings. Everything else is a
suggestion, and suggestions do not go inline on a PR.

---

## Before a finding is reported

Verify each one:

- Is the path actually reachable?
- Is it already handled — middleware, a global filter, an interceptor, an
  architecture test, an existing abstraction?
- Is it intentional per a plan, or recorded under
  *Known trade-offs* (the project's `docs/architecture.md`)?
- Does the concern apply to *this* code path, or to one that only looks like
  it?
- Have you tagged it **New** or **Pre-existing** per
  [How to use this framework, §4](#how-to-use-this-framework)?

If it survives only as a suspicion, it goes in the terminal review as a
question — never as a finding, inline or otherwise.

**If nothing meaningful is found, say so explicitly.** A review that
manufactures findings to look thorough teaches people to skim the next one.
