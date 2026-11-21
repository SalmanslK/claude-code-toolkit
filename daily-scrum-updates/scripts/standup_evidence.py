#!/usr/bin/env python3
"""Evidence for the three standup/history skills: daily-scrum-updates, team-daily-activity,
backend-development-history. Read-only: it runs only read-only git commands, reads Claude Code
transcripts, and never writes a file. The skills keep the judgement (what to write); this does the
mechanics (which days, which commits, which PRs, who authored them, which sessions, which deploys).

Commands (all print structured text):
  status   --log scrum|team|history         where the log is, what it holds, which days are missing
  dates    --log scrum|team [SPEC]          which days a run covers, and what to do with each
  evidence --log scrum|team [SPEC]          dates + the evidence for every day that needs writing
  has-entry --log scrum|team DATE           re-check right before writing (concurrent runs)
  merges   [--since D] [--until D]          PR merges into the integration branch (history)
  pr-authors MERGE [PATH ...]               who authored one PR, by commit count (history)
  deploys  [--since ISO]                    the deployment ledger from deploy transcripts (history)

SPEC: (none) | today | yesterday | tomorrow | YYYY-MM-DD | MM-DD-YYYY | "Sep 8" | "September 8" |
      this week | last week | this month | backfill | backfill N | backfill A..B

Safeguards, each proved by a test in test_standup_evidence.py (S-numbers match the test names):
  S1  "Today" is UTC plus the configured offset (default +05:00, PKT) - never the machine's zone, never TZ=.
  S2  Commits are bucketed by their author date in that offset; 23:50 PKT stays on D, 00:11 goes to D+1.
  S3  Refs are --branches --remotes, never --all: refs/stash ("index on dev: ...") is not work.
  S4  The user's own commits: user.name or user.email, plus every alias the authors map gives the same name.
  S5  Only real PR merges count (Bitbucket "Merged in X (pull request #N)", GitHub "Merge pull request #N
      from ..."); branch refreshes ("Merge branch 'dev' into ...") are counted and ignored, never work.
  S6  A PR's author is the email with the most non-merge commits in M^1..M^2; a tie goes to the merge
      commit's %ae; the branch tip's author is never used. The merger (%ce) is reported separately.
  S7  Open or merged is judged as of the end of that day, with rev-list --first-parent on the
      integration branch, so a branch merged the next morning reads as open all day.
  S8  Each commit is placed: landed by PR #N, direct to the integration branch with no PR, or still open.
  S9  Non-working days and holidays are skipped unless there is evidence; an explicit date always runs.
  S10 Existing entries are authoritative: a date with a section is never regenerated; "## Week:" headings
      are not dates.
  S11 team: a section marked "_Provisional - as of HH:MM PKT_" is replaced by the next run covering it;
      today's new section is written provisional.
  S12 scrum: today is written only when there is evidence.
  S13 A future date has no evidence; nothing is gathered for it.
  S14 First run: the last 5 working days including today. An explicit date on a new file is that date only.
  S15 Date words: ISO, MM-DD-YYYY (an ambiguous one is said back), "Mon D" (a future one means last
      year), this/last week, this month, backfill N, backfill A..B, bare backfill (range announced).
  S16 Authors: unmapped emails are reported with the line to add, never mapped silently; every known dev
      with no activity is listed; with no map, the roster is every email with a commit in the 30 days before.
  S17 An output path inside the repository's working tree (or a worktree) is a BLOCK.
  S18 Read-only: git subcommands are checked against an allow-list; the script opens no file for writing.
  S19 Transcripts: slugs for the main repo and every worktree, project roots deduped, PKT bucketing;
      sidechain, meta, tool results, compact summaries and system reminders skipped; any cut is marked.
  S20 Deploy ledger: anchored on the Environment/Branch/Commit block; the nearest verdict line above it
      (12 lines) decides: "Deployment complete." (old), "Deployment complete - smoke passed." and "Deployed - ..."
      (factory deploy), and the assistant's relayed "Deployed to QA - ..."; "NOT deployed" and "Deploy FAILED"
      are not deploys; a block with no verdict, template echoes and line-numbered file reads are discarded;
      deduped on (env, commit) keeping the earliest; a host, port or path is never printed.
  S21 has-entry re-reads the file from disk, for the check right before a write.
  S22 Config: ~ and {project} expanded, projectNames honoured, --dir overrides for one run, the
      integration branch comes from config (deployment.integrationBranch), not a fixed "dev".
  S23 Build output (bin/, obj/, node_modules/, lock files) is left out of a commit's file counts.
"""
from __future__ import annotations

import argparse
import calendar
import datetime as dt
import io
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_CONFIG = Path.home() / ".claude" / "daily-scrum-updates" / "config.json"
DEFAULTS = {
    "directory": "~/.claude/daily-scrum-updates",
    "workingDays": ["Mon", "Tue", "Wed", "Thu", "Fri"],
    "holidays": [],
    "projectNames": {},
    "authors": None,
    "utcOffset": "+05:00",
    "deployment": {"integrationBranch": "dev", "mergeDeploysTo": None},
}
LOG_FILES = {
    "scrum": "{p}-Daily-Updates.md",
    "team": "{p}-Team-Daily-Activity.md",
    "history": "{p}-Backend-Development-History.md",
    "status": "{p}-Project-Status.md",
}
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTHS = {m.lower(): i for i, m in enumerate(calendar.month_name) if m}
MONTHS.update({m.lower(): i for i, m in enumerate(calendar.month_abbr) if m})
MONTHS["sept"] = 9
FIRST_RUN_DAYS = 5
PROVISIONAL_RE = re.compile(r"^_Provisional\b.*_\s*$")
DATE_HEADING_RE = re.compile(r"^## (\d{4}-\d{2}-\d{2})\s*$")
BITBUCKET_PR_RE = re.compile(r"^Merged in (?P<branch>\S+) \(pull request #(?P<num>\d+)\)")
GITHUB_PR_RE = re.compile(r"^Merge pull request #(?P<num>\d+) from (?P<branch>\S+)")
BUILD_PATH_RE = re.compile(r"(^|/)(bin|obj|node_modules)/|(^|/)(package-lock\.json|yarn\.lock|pnpm-lock\.yaml|"
                           r"packages\.lock\.json|poetry\.lock|Cargo\.lock|composer\.lock)$")
SYSTEM_REMINDER_RE = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)

# S18: the only git subcommands this script may run, and how each must be called.
READ_ONLY_GIT = {
    "log": None, "show": None, "rev-parse": None, "rev-list": None, "merge-base": None, "diff": None,
    "for-each-ref": None, "cat-file": None,
    "branch": {"-a", "-r", "--contains", "--list", "--format"},   # listing only
    "config": {"--get", "--get-all"},                              # reading only
    "worktree": {"list"},                                          # listing only
}


class GitError(RuntimeError):
    pass


class Git:
    def __init__(self, repo: Path):
        self.repo = repo

    def run(self, *args: str, check: bool = True) -> subprocess.CompletedProcess:
        sub = args[0]
        if sub not in READ_ONLY_GIT:
            raise GitError(f"refused: git {sub} is not on the read-only allow-list")
        needs = READ_ONLY_GIT[sub]
        if needs is not None and not needs.intersection(args[1:]):
            raise GitError(f"refused: git {sub} only with one of {sorted(needs)}")
        env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
        p = subprocess.run(["git", "-c", "core.quotepath=off", "-C", str(self.repo), *args],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
        if check and p.returncode != 0:
            raise GitError(f"git {' '.join(args)}: {p.stderr.strip()}")
        return p

    def out(self, *args: str) -> str:
        return self.run(*args).stdout

    def ok(self, *args: str) -> bool:
        return self.run(*args, check=False).returncode == 0


# ----------------------------------------------------------------------------------------- time (S1, S2)

def parse_offset(text: str) -> dt.timezone:
    m = re.fullmatch(r"([+-])(\d{2}):?(\d{2})", text.strip())
    if not m:
        raise ValueError(f"utcOffset must look like +05:00, got {text!r}")
    delta = dt.timedelta(hours=int(m.group(2)), minutes=int(m.group(3)))
    return dt.timezone(delta if m.group(1) == "+" else -delta)


def offset_text(tz: dt.timezone) -> str:
    total = int(tz.utcoffset(None).total_seconds() // 60)
    sign = "+" if total >= 0 else "-"
    return f"{sign}{abs(total) // 60:02d}:{abs(total) % 60:02d}"


@dataclass
class Clock:
    now_utc: dt.datetime
    tz: dt.timezone

    @property
    def now(self) -> dt.datetime:
        return self.now_utc.astimezone(self.tz)

    @property
    def today(self) -> dt.date:
        return self.now.date()

    def local_date(self, iso: str) -> dt.date:
        stamp = dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=dt.timezone.utc)
        return stamp.astimezone(self.tz).date()

    def local_time(self, iso: str) -> str:
        stamp = dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=dt.timezone.utc)
        return stamp.astimezone(self.tz).strftime("%H:%M")

    def day_start(self, day: dt.date) -> str:
        return f"{day.isoformat()}T00:00:00{offset_text(self.tz)}"

    def day_end(self, day: dt.date) -> str:
        return f"{day.isoformat()}T23:59:59{offset_text(self.tz)}"


def parse_now(text: str | None) -> dt.datetime:
    if not text:
        return dt.datetime.now(dt.timezone.utc)
    stamp = dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
    return (stamp if stamp.tzinfo else stamp.replace(tzinfo=dt.timezone.utc)).astimezone(dt.timezone.utc)


# ----------------------------------------------------------------------------------------- config (S22, S17)

@dataclass
class Settings:
    repo: Path | None            # main working tree root, None outside git
    worktrees: list[Path]
    project: str
    directory: Path
    cfg: dict
    tz: dt.timezone
    notes: list[str] = field(default_factory=list)
    start: Path | None = None

    def file(self, log: str) -> Path:
        return self.directory / LOG_FILES[log].format(p=self.project)

    @property
    def integration(self) -> str:
        return (self.cfg.get("deployment") or {}).get("integrationBranch") or "dev"


def _norm(path: str | Path) -> str:
    return os.path.normcase(os.path.normpath(str(path))).rstrip("\\/")


def load_config(path: Path) -> dict:
    cfg = json.loads(json.dumps(DEFAULTS))
    if path.is_file():
        user = json.loads(path.read_text(encoding="utf-8"))
        for key, value in user.items():
            if key == "deployment" and isinstance(value, dict):
                cfg["deployment"].update(value)
            else:
                cfg[key] = value
    return cfg


def main_root(start: Path) -> tuple[Path | None, list[Path]]:
    probe = subprocess.run(["git", "-C", str(start), "rev-parse", "--path-format=absolute", "--git-common-dir"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
    if probe.returncode != 0:
        return None, []
    common = Path(probe.stdout.strip())
    root = common.parent if common.name == ".git" else Path(
        subprocess.run(["git", "-C", str(start), "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                       encoding="utf-8").stdout.strip())
    trees = []
    for line in Git(root).out("worktree", "list", "--porcelain").splitlines():
        if line.startswith("worktree "):
            trees.append(Path(line[len("worktree "):].strip()))
    return root, trees or [root]


def resolve_settings(repo_arg: str | None, config_path: Path, dir_override: str | None) -> Settings:
    cfg = load_config(config_path)
    start = Path(repo_arg or os.getcwd()).resolve()
    root, trees = main_root(start)
    notes = []
    if root is None:
        project = start.name
        notes.append("not inside a git repository: commit evidence is unavailable for this project")
    else:
        names = {_norm(s): v for k, v in (cfg.get("projectNames") or {}).items() for s in spellings(k)}
        project = next((names[_norm(s)] for s in spellings(root) | spellings(start) if _norm(s) in names),
                       root.name)
    raw = dir_override or cfg.get("directory") or DEFAULTS["directory"]
    directory = Path(os.path.expanduser(str(raw).replace("{project}", project)))
    return Settings(repo=root, worktrees=trees, project=project, directory=directory, cfg=cfg,
                    tz=parse_offset(cfg.get("utcOffset") or "+05:00"), notes=notes,
                    start=Path(os.path.normpath(repo_arg or os.getcwd())))


def inside_repo(settings: Settings) -> Path | None:
    """S17: the tree the output directory sits in, if it is inside the repository or a worktree."""
    targets = {_norm(s) for s in spellings(settings.directory.resolve())} | {_norm(settings.directory)}
    for tree in settings.worktrees or ([settings.repo] if settings.repo else []):
        for t in {_norm(s) for s in spellings(tree)}:
            if any(x == t or x.startswith(t + os.sep) for x in targets):
                return tree
    return None


# ----------------------------------------------------------------------------------------- log files (S10, S11, S21)

def read_entries(path: Path) -> dict[dt.date, str]:
    """date -> 'final' | 'provisional'. Only bare '## YYYY-MM-DD' headings are dates."""
    entries: dict[dt.date, str] = {}
    if not path.is_file():
        return entries
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        m = DATE_HEADING_RE.match(line)
        if not m:
            continue
        nxt = next((ln for ln in lines[i + 1:i + 4] if ln.strip()), "")
        entries[dt.date.fromisoformat(m.group(1))] = "provisional" if PROVISIONAL_RE.match(nxt.strip()) else "final"
    return entries


# ----------------------------------------------------------------------------------------- dates (S9, S13-S15)

@dataclass
class Day:
    date: dt.date
    explicit: bool
    working: bool
    existing: str | None
    future: bool


@dataclass
class Plan:
    mode: str
    days: list[Day]
    notes: list[str]
    announce: str | None = None


def is_working(day: dt.date, cfg: dict) -> bool:
    holidays = {str(h) for h in cfg.get("holidays") or []}
    return DAY_NAMES[day.weekday()] in (cfg.get("workingDays") or DEFAULTS["workingDays"]) and \
        day.isoformat() not in holidays


def span(a: dt.date, b: dt.date) -> list[dt.date]:
    return [a + dt.timedelta(days=i) for i in range((b - a).days + 1)] if b >= a else []


def working_days_back(end: dt.date, count: int, cfg: dict) -> list[dt.date]:
    out, day = [], end
    while len(out) < count and (end - day).days < 366:
        if is_working(day, cfg):
            out.append(day)
        day -= dt.timedelta(days=1)
    return sorted(out)


def parse_one_date(text: str, today: dt.date, notes: list[str]) -> dt.date | None:
    t = text.strip().lower().rstrip(".")
    if t == "today":
        return today
    if t == "yesterday":
        return today - dt.timedelta(days=1)
    if t == "tomorrow":
        return today + dt.timedelta(days=1)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", t):
        return dt.date.fromisoformat(t)
    m = re.fullmatch(r"(\d{1,2})-(\d{1,2})-(\d{4})", t)
    if m:
        month, day, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        value = dt.date(year, month, day)
        if month <= 12 and day <= 12 and month != day:
            notes.append(f"interpreted {text} as {value:%B} {value.day}, {value.year} (MM-DD-YYYY, US order)")
        return value
    m = re.fullmatch(r"([a-z]+)\.? (\d{1,2})(?:,? (\d{4}))?", t)
    if m and m.group(1) in MONTHS:
        if m.group(3):
            return dt.date(int(m.group(3)), MONTHS[m.group(1)], int(m.group(2)))
        value = dt.date(today.year, MONTHS[m.group(1)], int(m.group(2)))
        if value > today:
            value = value.replace(year=today.year - 1)
            notes.append(f"{text} is later than today this year: taken as {value.isoformat()}")
        return value
    return None


def plan_dates(spec: str, log: str, entries: dict[dt.date, str], clock: Clock, cfg: dict,
               earliest_evidence: dt.date | None = None) -> Plan:
    today = clock.today
    notes: list[str] = []
    spec = " ".join(spec.split()).lower()
    explicit = False
    announce = None

    if spec == "":
        if not entries:
            mode = "first run"
            dates = working_days_back(today, FIRST_RUN_DAYS, cfg)
            notes.append(f"first run: the last {FIRST_RUN_DAYS} working days including today")
        else:
            mode = "default (fill missing)"
            last = max(entries)
            start = last if entries[last] == "provisional" else last + dt.timedelta(days=1)
            dates = span(start, today)
            if not dates:
                notes.append(f"up to date: last entry {last.isoformat()}")
    elif spec in ("this week",):
        mode = spec
        dates = span(today - dt.timedelta(days=today.weekday()), today)
    elif spec == "last week":
        mode = spec
        monday = today - dt.timedelta(days=today.weekday() + 7)
        dates = span(monday, monday + dt.timedelta(days=6))
    elif spec == "this month":
        mode = spec
        dates = span(today.replace(day=1), today)
    elif spec.startswith("backfill"):
        mode = "backfill"
        rest = spec[len("backfill"):].strip()
        first = min(entries) if entries else None
        end = (first - dt.timedelta(days=1)) if first else today
        if re.fullmatch(r"\d+", rest):
            dates = working_days_back(end, int(rest), cfg)
        elif ".." in rest:
            a, b = (parse_one_date(x, today, notes) for x in rest.split("..", 1))
            if not a or not b:
                raise ValueError(f"cannot read the range {rest!r}")
            dates = span(a, b)
        elif rest == "":
            if earliest_evidence is None:
                dates = []
                notes.append("no evidence found before the earliest entry: nothing to backfill")
            else:
                dates = span(earliest_evidence, end)
        else:
            raise ValueError(f"cannot read backfill {rest!r}")
        if dates:
            announce = f"{dates[0].isoformat()}..{dates[-1].isoformat()} ({len(dates)} calendar days)"
    else:
        value = parse_one_date(spec, today, notes)
        if value is None:
            raise ValueError(f"cannot read the date {spec!r}")
        mode, dates, explicit = "explicit date", [value], True

    days = [Day(date=d, explicit=explicit, working=is_working(d, cfg), existing=entries.get(d), future=d > today)
            for d in dates]
    return Plan(mode=mode, days=days, notes=notes, announce=announce)


# ----------------------------------------------------------------------------------------- git evidence (S2-S8, S16, S23)

SEP, END = "\x1f", "\x1e"
LOG_FORMAT = "%x1e" + "%x1f".join(["%H", "%h", "%an", "%ae", "%cn", "%ce", "%aI", "%cI", "%P", "%D", "%s"])
DASH = "—"


@dataclass
class Commit:
    sha: str
    short: str
    an: str
    ae: str
    cn: str
    ce: str
    adate: str
    cdate: str
    parents: list[str]
    refs: str
    subject: str
    files: list[str] = field(default_factory=list)

    @property
    def is_merge(self) -> bool:
        return len(self.parents) > 1


def git_log(git: Git, *args: str, numstat: bool = False) -> list[Commit]:
    extra = ["--numstat"] if numstat else []
    text = git.out("log", f"--format={LOG_FORMAT}", *extra, *args)
    commits = []
    for chunk in text.split(END):
        lines = chunk.strip("\n").split("\n")
        parts = lines[0].split(SEP)
        if len(parts) != 11:
            continue
        files = [ln.split("\t", 2)[2] for ln in lines[1:] if ln.count("\t") >= 2]
        commits.append(Commit(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6], parts[7],
                              parts[8].split(), parts[9], parts[10], files))
    return commits


def pr_match(subject: str):
    """S5: (number, branch) for a real PR merge, else None."""
    m = BITBUCKET_PR_RE.match(subject)
    if m:
        return int(m.group("num")), m.group("branch")
    m = GITHUB_PR_RE.match(subject)
    if m:
        branch = m.group("branch")
        return int(m.group("num")), branch.split("/", 1)[1] if "/" in branch else branch
    return None


def integration_ref(git: Git, name: str) -> str | None:
    for ref in (f"refs/remotes/origin/{name}", f"refs/heads/{name}"):
        if git.ok("rev-parse", "--verify", "--quiet", ref):
            return ref
    return None


class Authors:
    def __init__(self, mapping: dict | None):
        self.mapping = {k.lower(): v for k, v in (mapping or {}).items()}
        self.order: list[str] = []
        for name in self.mapping.values():
            if name not in self.order:
                self.order.append(name)
        self.unmapped: dict[str, str] = {}

    @property
    def present(self) -> bool:
        return bool(self.mapping)

    def name(self, email: str, raw_name: str) -> str:
        found = self.mapping.get(email.lower())
        if found:
            return found
        self.unmapped.setdefault(email.lower(), raw_name)
        return raw_name

    def known(self, email: str) -> bool:
        return email.lower() in self.mapping


class Repo:
    def __init__(self, git: Git, settings: Settings, clock: Clock):
        self.git, self.s, self.clock = git, settings, clock
        self.int_ref = integration_ref(git, settings.integration)
        self._fp: set[str] | None = None
        self._eod: dict[dt.date, str | None] = {}

    def first_parent(self) -> set[str]:
        if self._fp is None:
            self._fp = set(self.git.out("rev-list", "--first-parent", self.int_ref).split()) if self.int_ref else set()
        return self._fp

    def int_at(self, day: dt.date) -> str | None:
        """S7: the integration branch's tip as of the end of `day`, first-parent only."""
        if not self.int_ref:
            return None
        if day not in self._eod:
            sha = self.git.out("rev-list", "-1", "--first-parent", f"--until={self.clock.day_end(day)}",
                               self.int_ref).strip()
            self._eod[day] = sha or None
        return self._eod[day]

    def authored(self, since: dt.date) -> list[Commit]:
        """S3 + S2: every non-merge commit on branches and remotes, bucketed later by author date."""
        return git_log(self.git, "--branches", "--remotes", "--no-merges",
                       f"--since={self.clock.day_start(since - dt.timedelta(days=1))}", numstat=True)

    def merges(self, since: dt.date, until: dt.date | None = None) -> list[Commit]:
        args = ["--branches", "--remotes", "--merges", f"--since={self.clock.day_start(since)}"]
        if until:
            args.append(f"--until={self.clock.day_end(until)}")
        return git_log(self.git, *args)

    def pr_authors(self, merge: Commit, paths: list[str] | None = None) -> dict:
        """S6: author by commit count inside the PR; tie -> the merge commit's %ae."""
        args = ["--no-merges", f"{merge.parents[0]}..{merge.parents[1]}"]
        if paths:
            args += ["--", *paths]
        inside = git_log(self.git, *args)
        counts: dict[str, int] = {}
        names: dict[str, str] = {}
        for c in inside:
            counts[c.ae.lower()] = counts.get(c.ae.lower(), 0) + 1
            names.setdefault(c.ae.lower(), c.an)
        ranked = sorted(counts.items(), key=lambda kv: -kv[1])
        author, tie = None, False
        if ranked:
            top = ranked[0][1]
            leaders = [e for e, n in ranked if n == top]
            tie = len(leaders) > 1
            author = merge.ae.lower() if merge.ae.lower() in leaders else leaders[0]
        return {"counts": ranked, "names": names, "author": author, "tie": tie, "total": len(inside),
                "subjects": [c.subject for c in inside]}

    def placement(self, c: Commit, day: dt.date) -> str:
        """S8 + S7: where the commit landed, and whether it was in the integration branch by end of day."""
        tip = self.int_at(day)
        by_eod = bool(tip) and self.git.ok("merge-base", "--is-ancestor", c.sha, tip)
        state = f"in {self.s.integration} by end of day" if by_eod else "not yet merged at end of day"
        if c.sha in self.first_parent():
            return f"direct to {self.s.integration}, no PR; {state}"
        if self.int_ref and self.git.ok("merge-base", "--is-ancestor", c.sha, self.int_ref):
            hits = git_log(self.git, "--merges", "--ancestry-path", f"{c.sha}..{self.int_ref}")
            prs = [h for h in hits if pr_match(h.subject)]
            if prs:
                num, branch = pr_match(prs[-1].subject)
                return f"branch {branch}, landed by PR #{num} on {self.clock.local_date(prs[-1].cdate)}; {state}"
            return f"in {self.s.integration} with no PR merge found; {state}"
        heads = self.git.out("branch", "-a", "--contains", c.sha, "--format=%(refname:short)").split()
        heads = sorted({h.removeprefix("origin/") for h in heads if h not in ("origin", "HEAD") and "HEAD" not in h})
        return f"open on {', '.join(heads) or 'no branch'}; {state}"

    def into(self, m: Commit) -> str:
        return self.s.integration if m.sha in self.first_parent() else "another branch"


def file_summary(files: list[str]) -> str:
    kept = [f for f in files if not BUILD_PATH_RE.search(f.replace("\\", "/"))]
    if not kept:
        return "files: none outside build output" if files else "files: 0"
    tops: dict[str, int] = {}
    for f in kept:
        top = f.split("/", 1)[0] if "/" in f else "(root)"
        tops[top] = tops.get(top, 0) + 1
    dropped = len(files) - len(kept)
    return f"files: {len(kept)} ({', '.join(f'{k} {v}' for k, v in sorted(tops.items()))})" + \
        (f", {dropped} build files left out" if dropped else "")


# ----------------------------------------------------------------------------------------- transcripts (S19, S20)

def slug(path: Path | str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "-", str(path))


def spellings(path: Path | str) -> set[str]:
    """Every spelling of a path a session may have started in: as given, normalised, and on Windows the
    long and the short (8.3) form."""
    p = os.path.normpath(str(path))
    out = {str(path), p}
    if os.name == "nt":
        import ctypes
        for fn in (ctypes.windll.kernel32.GetLongPathNameW, ctypes.windll.kernel32.GetShortPathNameW):
            buf = ctypes.create_unicode_buffer(1024)
            if fn(p, buf, 1024):
                out.add(buf.value)
    return out


_CWD_CACHE: dict[str, str | None] = {}


def folder_cwd(d: Path) -> str | None:
    """The working directory the first session in a transcript folder recorded (reads a few lines)."""
    key = str(d)
    if key not in _CWD_CACHE:
        _CWD_CACHE[key] = None
        for f in sorted(d.glob("*.jsonl"))[:3]:
            with f.open(encoding="utf-8", errors="replace") as handle:
                for _, line in zip(range(40), handle):
                    if '"cwd"' in line:
                        try:
                            _CWD_CACHE[key] = json.loads(line).get("cwd")
                        except json.JSONDecodeError:
                            continue
                        if _CWD_CACHE[key]:
                            return _CWD_CACHE[key]
    return _CWD_CACHE[key]


def project_roots(explicit: list[str] | None) -> list[Path]:
    if explicit:
        cands = [Path(p) for p in explicit]
    else:
        cands = []
        if os.environ.get("CLAUDE_CONFIG_DIR"):
            cands.append(Path(os.environ["CLAUDE_CONFIG_DIR"]) / "projects")
        cands.append(Path.home() / ".claude" / "projects")
    seen, out = set(), []
    for c in cands:
        if c.is_dir():
            key = _norm(c.resolve())
            if key not in seen:
                seen.add(key)
                out.append(c)
    return out


def transcript_files(settings: Settings, roots: list[Path]) -> tuple[list[Path], list[str]]:
    trees = list(settings.worktrees or ([settings.repo] if settings.repo else []))
    if settings.start:
        trees.append(settings.start)
    # Claude Code names the folder after the path the session started in; git may print another
    # spelling of it (short 8.3 names, forward slashes), so slug every spelling.
    slugs = {slug(s).lower() for t in trees for s in spellings(t)}
    wanted = {_norm(s) for t in trees for s in spellings(t)}
    found, seen, dirs = [], set(), []
    for root in roots:
        for d in sorted(p for p in root.iterdir() if p.is_dir()):
            # The folder name is a lossy slug; when it does not match, the cwd its sessions record decides.
            if d.name.lower() not in slugs and not (folder_cwd(d) and
                                                    {_norm(s) for s in spellings(folder_cwd(d))} & wanted):
                continue
            dirs.append(d.name)
            for f in sorted(d.glob("*.jsonl")):
                key = _norm(f.resolve())
                if key not in seen:
                    seen.add(key)
                    found.append(f)
    return found, sorted(set(dirs))


def cut(text: str, limit: int) -> str:
    text = " ".join(text.split())
    if limit and len(text) > limit:
        return text[:limit] + f" ... [cut: {len(text) - limit} more chars]"
    return text


def prompt_text(o: dict) -> str | None:
    if o.get("type") != "user" or o.get("isSidechain") or o.get("isMeta") or o.get("isCompactSummary") \
            or o.get("isVisibleInTranscriptOnly"):
        return None
    msg = o.get("message")
    if not isinstance(msg, dict):
        return None
    content = msg.get("content")
    if isinstance(content, list):
        if any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
            return None
        content = "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    if not isinstance(content, str):
        return None
    content = SYSTEM_REMINDER_RE.sub("", content).strip()
    m = re.search(r"<command-name>(.*?)</command-name>", content, re.S)
    if m:
        args = re.search(r"<command-args>(.*?)</command-args>", content, re.S)
        return f"{m.group(1).strip()} {args.group(1).strip() if args else ''}".strip()
    if not content or content.startswith("<") or content.startswith("Caveat:") \
            or content.startswith("[Request interrupted"):
        return None
    return content


def assistant_text(o: dict) -> str | None:
    if o.get("type") != "assistant" or o.get("isSidechain") or o.get("isApiErrorMessage"):
        return None
    msg = o.get("message")
    content = msg.get("content") if isinstance(msg, dict) else None
    if isinstance(content, str):
        return content.strip() or None
    if isinstance(content, list):
        text = "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text").strip()
        return text or None
    return None


@dataclass
class SessionDay:
    session: str
    title: str = ""
    first: str = ""
    last: str = ""
    branches: set = field(default_factory=set)
    prompts: list = field(default_factory=list)
    final: str = ""


def sessions_by_day(files: list[Path], days: set[dt.date], clock: Clock) -> dict[dt.date, list[SessionDay]]:
    out: dict[dt.date, list[SessionDay]] = {d: [] for d in days}
    if not days:
        return out
    lo = min(days)
    earliest_utc = dt.datetime.combine(lo, dt.time(), clock.tz).astimezone(dt.timezone.utc)
    prefixes = set()     # a cheap pre-filter only; the parsed timestamp decides the day
    for d in days:
        for delta in (-1, 0, 1):
            prefixes.add(f'"{(d + dt.timedelta(days=delta)).isoformat()}T')
    seen_uuid: set[str] = set()       # a resumed or forked session copies its parent's lines: count each once
    for f in sorted(files, key=lambda p: p.stat().st_mtime if p.exists() else 0):
        try:
            if dt.datetime.fromtimestamp(f.stat().st_mtime, dt.timezone.utc) < earliest_utc:
                continue
        except OSError:
            continue
        per: dict[dt.date, SessionDay] = {}
        title = ""
        with f.open(encoding="utf-8", errors="replace") as handle:
            for line in handle:
                titled = '"ai-title"' in line
                if not titled and not any(p in line for p in prefixes):
                    continue
                try:
                    o = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if o.get("type") == "ai-title":
                    title = o.get("aiTitle") or title
                    continue
                stamp = o.get("timestamp")
                if not stamp:
                    continue
                day = clock.local_date(stamp)
                if day not in days:
                    continue
                p, a = prompt_text(o), assistant_text(o)
                if p is None and a is None:
                    continue
                if o.get("uuid"):
                    if o["uuid"] in seen_uuid:
                        continue
                    seen_uuid.add(o["uuid"])
                sd = per.setdefault(day, SessionDay(session=f.stem[:8]))
                t = clock.local_time(stamp)
                sd.first = sd.first or t
                sd.last = t
                if o.get("gitBranch"):
                    sd.branches.add(o["gitBranch"])
                if p and p not in sd.prompts:
                    sd.prompts.append(p)
                if a:
                    sd.final = a
        for day, sd in per.items():
            sd.title = title
            if sd.prompts or sd.final:
                out[day].append(sd)
    for d in out:
        out[d].sort(key=lambda s: s.first)
    return out


def earliest_transcript_day(files: list[Path], clock: Clock) -> dt.date | None:
    best = None
    for f in files:
        with f.open(encoding="utf-8", errors="replace") as handle:
            for line in handle:
                m = re.search(r'"timestamp":\s*"([^"]+)"', line)
                if m:
                    d = clock.local_date(m.group(1))
                    best = d if best is None or d < best else best
                    break
    return best


# S20 ------------------------------------------------------------------------------------------------------
# The Environment/Branch/Commit block is the stable part of every deploy report, old and new; the verdict line
# above it varies (and the assistant often relays it in its own words, with a code fence in between), so the
# block anchors the match and the nearest verdict line above it, within a few lines, decides what it was.
VERDICT_RE = re.compile(
    r"(?:Reverted to (?P<rev>[0-9a-f]{7,40}) after the smoke failed\. )?"
    r"(?P<v>NOT deployed\b[^\n]*|Deploy FAILED\b[^\n]*|Deployment complete(?: — smoke passed)?\.?"
    r"|Deployed(?: to [A-Z]+)? — [^\n]*)")
ENV_LINE_RE = re.compile(r"^[ \t>*`]*Environment:[ \t]*(?P<v>[^\s`*]*)", re.M)
FIELD_RE = {k: re.compile(rf"^[ \t>*`]*{k}:[ \t]*(?P<v>[^\s`*]*)", re.M) for k in ("Branch", "Commit")}
LOOKBACK_LINES = 12


def classify(first: str, rev: str | None) -> str | None:
    """None when the report says nothing was deployed."""
    if first.startswith(("NOT deployed", "Deploy FAILED")):
        return None
    if first.rstrip(".") == "Deployment complete":
        return "complete (older report wording)"
    if first.startswith("Deployment complete"):
        return "smoke passed"
    low = first.lower()
    if "smoke passed in part" in low:
        verdict = "smoke passed IN PART"
    elif "failed" in low:
        verdict = "smoke FAILED"
    elif "did not run" in low:
        verdict = "smoke did not run"
    elif "skipped" in low:
        verdict = "smoke skipped"
    else:
        verdict = "deployed"
    return verdict + (f"; reverted to {rev[:12]}" if rev else "")


def ledger_from_text(text: str) -> list[dict]:
    rows = []
    for env in ENV_LINE_RE.finditer(text):
        after = "\n".join(text[env.end():].split("\n")[1:5])            # Branch and Commit follow within 4 lines
        found = {k: (r.search(after).group("v") if r.search(after) else "") for k, r in FIELD_RE.items()}
        first, rev = None, None
        above = text[:env.start()].split("\n")
        for line in reversed(above[-LOOKBACK_LINES:]):
            if FIELD_RE["Commit"].match(line):                            # the previous block: no verdict of ours
                break
            v = VERDICT_RE.search(line)
            if v:
                first, rev = v.group("v").strip(" *`"), v.group("rev")
                break
        rows.append({"first": first, "rev": rev, "env": env.group("v"),
                     "branch": found["Branch"], "commit": found["Commit"]})
    return rows


def is_echo(row: dict) -> bool:
    """A template or example, not a run. A missing Branch line is allowed (hand-relayed reports omit it)."""
    return not re.fullmatch(r"[A-Z]+", row["env"] or "") or any(ch in (row["branch"] or "") for ch in "{}<>$") \
        or not re.fullmatch(r"[0-9a-f]{7,40}", row["commit"] or "")


def message_strings(o: dict) -> list[str]:
    msg = o.get("message")
    if not isinstance(msg, dict) or o.get("type") not in ("user", "assistant"):
        return []
    content = msg.get("content")
    out = []
    if isinstance(content, str) and o.get("type") == "assistant":
        out.append(content)
    elif isinstance(content, list):
        for b in content:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "text" and o.get("type") == "assistant":
                out.append(b.get("text", ""))
            elif b.get("type") == "tool_result":
                inner = b.get("content")
                if isinstance(inner, str):
                    out.append(inner)
                elif isinstance(inner, list):
                    out += [x.get("text", "") for x in inner if isinstance(x, dict) and x.get("type") == "text"]
    return out


def deploy_ledger(files: list[Path], clock: Clock, since: str | None = None) -> tuple[list[dict], dict]:
    since_dt = dt.datetime.fromisoformat(since.replace("Z", "+00:00")) if since else None
    if since_dt and since_dt.tzinfo is None:
        since_dt = since_dt.replace(tzinfo=dt.timezone.utc)
    rows, stats = {}, {"hits": 0, "echoes": 0, "not_deployed": 0, "no_verdict": 0, "candidates": []}
    for f in files:
        if since_dt:
            try:
                if dt.datetime.fromtimestamp(f.stat().st_mtime, dt.timezone.utc) < since_dt:
                    continue
            except OSError:
                continue
        with f.open(encoding="utf-8", errors="replace") as handle:
            for line in handle:
                if "Environment:" not in line or "eploy" not in line:
                    continue
                try:
                    o = json.loads(line)
                except json.JSONDecodeError:
                    continue
                stamp = o.get("timestamp")
                if not stamp:
                    continue
                when = dt.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
                if since_dt and when <= since_dt:
                    continue
                for text in message_strings(o):
                    for row in ledger_from_text(text):
                        stats["hits"] += 1
                        if is_echo(row):
                            stats["echoes"] += 1
                            continue
                        if not row["first"]:
                            stats["no_verdict"] += 1
                            stats["candidates"].append(dict(row, date=clock.local_date(stamp),
                                                            time=clock.local_time(stamp), session=f.stem[:8]))
                            continue
                        verdict = classify(row["first"], row["rev"])
                        if verdict is None:
                            stats["not_deployed"] += 1
                            continue
                        key = (row["env"], row["commit"][:7])
                        row.update(stamp=stamp, date=clock.local_date(stamp), time=clock.local_time(stamp),
                                   session=f.stem[:8], verdict=verdict)
                        if key not in rows or stamp < rows[key]["stamp"]:
                            rows[key] = row
    return sorted(rows.values(), key=lambda r: r["stamp"]), stats


# ----------------------------------------------------------------------------------------- printing

def header(settings: Settings, clock: Clock, log: str | None, out) -> None:
    print(f"PROJECT {settings.project}", file=out)
    print(f"NOW {clock.now.strftime('%Y-%m-%d %H:%M')} (UTC{offset_text(clock.tz)}; {DAY_NAMES[clock.today.weekday()]})",
          file=out)
    if log:
        logs = ["history", "status"] if log == "history" else [log]
        for name in logs:
            path = settings.file(name)
            print(f"FILE {name}: {path} ({'exists' if path.is_file() else 'not created yet'})", file=out)
    for note in settings.notes:
        print(f"NOTE {note}", file=out)


def block_if_inside(settings: Settings, out) -> bool:
    tree = inside_repo(settings)
    if tree:
        print(f"BLOCK the output directory {settings.directory} is inside the working tree {tree}. "
              "Stop and tell the user; do not write there, do not gitignore it.", file=out)
        return True
    return False


def own_identity(git: Git, authors: Authors) -> tuple[set[str], set[str]]:
    name = git.run("config", "--get", "user.name", check=False).stdout.strip()
    email = git.run("config", "--get", "user.email", check=False).stdout.strip().lower()
    emails = {email} if email else set()
    display = authors.mapping.get(email)
    if display:
        emails |= {e for e, n in authors.mapping.items() if n == display}
    names = {name.casefold()} if name else set()
    return emails, names


def is_own(c: Commit, emails: set[str], names: set[str]) -> bool:
    return c.ae.lower() in emails or c.an.casefold() in names


def decide(day: Day, log: str, has_evidence: bool, today: dt.date) -> str:
    if day.future:
        return "FUTURE - no evidence exists; write only a plan the user stated inline, marked as planned"
    if day.existing == "final":
        return "EXISTS - authoritative; do not regenerate (show it; amend only if the user says so)"
    if not has_evidence:
        if not day.working and not day.explicit:
            return "SKIP - non-working day, no evidence"
        if day.date == today:
            return "SKIP - no evidence yet today"
        return "NO EVIDENCE - record the gap visibly, never skip silently" if log == "scrum" else \
            "NO EVIDENCE - write the date with every known dev under _No activity:_"
    if day.existing == "provisional":
        return "REPLACE the provisional section" + (" (still provisional: today)" if day.date == today else
                                                    " (day is over: drop the marker)")
    if log == "team" and day.date == today:
        return "WRITE (provisional: today is not over)"
    return "WRITE"


def print_plan(plan: Plan, out) -> None:
    print(f"MODE {plan.mode}", file=out)
    if plan.announce:
        print(f"ANNOUNCE before writing anything: backfill range {plan.announce}", file=out)
    for n in plan.notes:
        print(f"NOTE {n}", file=out)


def evidence(args, settings: Settings, clock: Clock, out) -> int:
    log = args.log
    header(settings, clock, log, out)
    if block_if_inside(settings, out):
        return 2
    path = settings.file(log)
    entries = read_entries(path)
    authors = Authors(settings.cfg.get("authors"))
    git = Git(settings.repo) if settings.repo else None
    roots = project_roots(args.projects_dir)
    tfiles, tdirs = transcript_files(settings, roots) if log == "scrum" else ([], [])
    repo = Repo(git, settings, clock) if git else None
    own_emails, own_names = own_identity(git, authors) if git else (set(), set())

    spec = " ".join(args.spec)
    earliest = None
    if spec.strip().lower() == "backfill":
        cands = []
        if git:
            fmt = git.out("log", "--branches", "--remotes", "--no-merges", "--reverse", "--format=%aI%x1f%ae%x1f%an")
            for ln in fmt.splitlines():
                iso, ae, an = (ln.split(SEP) + ["", "", ""])[:3]
                if log == "team" or ae.lower() in own_emails or an.casefold() in own_names:
                    cands.append(clock.local_date(iso))
                    break
        if log == "scrum":
            t = earliest_transcript_day(tfiles, clock)
            if t:
                cands.append(t)
        earliest = min(cands) if cands else None
    plan = plan_dates(spec, log, entries, clock, settings.cfg, earliest)
    print_plan(plan, out)
    if log == "scrum":
        print("TRANSCRIPTS " + (", ".join(tdirs) + f" ({len(tfiles)} files)" if tdirs else
                                "unavailable for this repository path: session evidence cannot be used"), file=out)
    if repo and not repo.int_ref:
        print(f"NOTE no {settings.integration} branch found: merged/open state cannot be judged", file=out)
    if args.dates_only:
        for d in plan.days:
            flags = [DAY_NAMES[d.date.weekday()], "working" if d.working else "non-working"]
            if d.existing:
                flags.append(f"entry {d.existing}")
            if d.future:
                flags.append("future")
            print(f"DATE {d.date.isoformat()} {' · '.join(flags)}", file=out)
        return 0

    gather = [d for d in plan.days if not d.future and d.existing != "final"]
    commits: list[Commit] = []
    merges: list[Commit] = []
    if repo and gather:
        lo = min(d.date for d in gather)
        commits = repo.authored(lo if authors.present or log == "scrum" else lo - dt.timedelta(days=31))
        merges = repo.merges(lo - dt.timedelta(days=1))
    sessions = sessions_by_day(tfiles, {d.date for d in gather}, clock) if log == "scrum" else {}

    for day in plan.days:
        print("", file=out)
        tag = f"{DAY_NAMES[day.date.weekday()]}, {'working' if day.working else 'non-working'}"
        if day.date not in {g.date for g in gather}:
            print(f"=== {day.date.isoformat()} ({tag}) -> {decide(day, log, True, clock.today)}", file=out)
            continue
        own = [c for c in commits if clock.local_date(c.adate) == day.date]
        prs, refreshes = [], 0
        for m in merges:
            if clock.local_date(m.cdate) != day.date:
                continue
            if pr_match(m.subject):
                prs.append(m)
            else:
                refreshes += 1
        if log == "scrum":
            own = [c for c in own if is_own(c, own_emails, own_names)]
            sess = sessions.get(day.date, [])
            has = bool(own or prs or sess)
        else:
            sess = []
            has = bool(own or prs)
        action = decide(day, log, has, clock.today)
        print(f"=== {day.date.isoformat()} ({tag}) -> {action}", file=out)
        if action.startswith(("SKIP", "NO EVIDENCE")):
            continue
        if "provisional" in action and day.date == clock.today:
            zone = "PKT" if offset_text(clock.tz) == "+05:00" else f"UTC{offset_text(clock.tz)}"
            print(f"MARKER first line: _Provisional {DASH} as of {clock.now.strftime('%H:%M')} {zone}_", file=out)
        if log == "scrum":
            print_scrum_day(repo, day.date, own, prs, refreshes, sess, own_emails, own_names, authors, args, out)
        else:
            print_team_day(repo, day.date, own, prs, refreshes, authors, settings, commits, out)
    if authors.unmapped:
        print("", file=out)
        for email, name in sorted(authors.unmapped.items()):
            print(f'UNMAPPED {name} <{email}> -> suggest adding "{email}": "<Display Name>" to authors (do not edit it yourself)',
                  file=out)
    return 0


def print_pr(repo: Repo, m: Commit, authors: Authors, out, own: tuple | None = None) -> dict:
    num, branch = pr_match(m.subject)
    info = repo.pr_authors(m)
    author_email = info["author"] or m.ae.lower()
    author = authors.name(author_email, info["names"].get(author_email, m.an))
    merger = authors.name(m.ce, m.cn)
    top = info["counts"][0][1] if info["counts"] else 0
    same = author_email == m.ae.lower() or (authors.known(m.ae) and authors.mapping[m.ae.lower()] == author)
    agree = "agrees" if same else f"disagrees (%ae {m.ae}) - the count wins"
    line = (f"  PR #{num} {branch} -> {repo.into(m)} at {repo.clock.local_time(m.cdate)}: author {author} "
            f"({top}/{info['total']} commits{', TIE - weigh which side carries the feature' if info['tie'] else ''}; "
            f"%ae {agree}); merged by {merger}")
    print(line, file=out)
    body = repo.git.out("show", "-s", "--format=%b", m.sha).strip().splitlines()
    title = next((b.strip() for b in body if b.strip()), "")
    if title:
        print(f"    title: {cut(title, 200)}", file=out)
    stat = repo.git.out("diff", "--shortstat", m.parents[0], m.sha).strip()
    if stat:
        print(f"    change: {stat}", file=out)
    if own is not None:
        emails, names = own
        mine = sum(n for e, n in info["counts"] if e in emails)
        merged_by_me = m.ce.lower() in emails or m.cn.casefold() in names
        role = ("author" if mine and author_email in emails else "co-author" if mine else "") + \
               ("+merger" if merged_by_me else "")
        role = role.lstrip("+") or "unknown - you neither wrote it nor merged it; ask before choosing a verb"
        print(f"    your role: {role} (your commits in it: {mine}/{info['total']})", file=out)
    return {"num": num, "branch": branch, "author_email": author_email, "author": author, "merger": merger,
            "merger_email": m.ce.lower()}


def print_scrum_day(repo, day, own, prs, refreshes, sessions, emails, names, authors, args, out) -> None:
    print(f"COMMITS (yours, non-merge, by author date): {len(own)}", file=out)
    for c in sorted(own, key=lambda c: c.adate):
        print(f"  {c.short} {repo.clock.local_time(c.adate)} {c.subject}", file=out)
        print(f"    {repo.placement(c, day)}; {file_summary(c.files)}", file=out)
    print(f"PR MERGES that day (any author - each is worth a bullet): {len(prs)}", file=out)
    for m in sorted(prs, key=lambda m: m.cdate):
        print_pr(repo, m, authors, out, own=(emails, names))
    print(f"BRANCH REFRESHES ignored (not work): {refreshes}", file=out)
    print(f"SESSIONS: {len(sessions)}", file=out)
    limit_p = 0 if args.full else args.prompt_chars
    max_prompts = 10 ** 6 if args.full else args.max_prompts
    for s in sessions:
        print(f"  [{s.session}] {s.first}-{s.last} branch {', '.join(sorted(s.branches)) or '-'}"
              + (f" title: {cut(s.title, 120)}" if s.title else ""), file=out)
        for p in s.prompts[:max_prompts]:
            print(f"    > {cut(p, limit_p)}", file=out)
        if len(s.prompts) > max_prompts:
            print(f"    > [cut: {len(s.prompts) - max_prompts} more prompts; rerun with --full]", file=out)
        if s.final:
            print(f"    < {cut(s.final, 0 if args.full else args.final_chars)}", file=out)


def print_team_day(repo, day, own, prs, refreshes, authors: Authors, settings, all_commits, out) -> None:
    people: dict[str, dict] = {}

    def person(name):
        return people.setdefault(name, {"commits": [], "prs": [], "merged": []})

    for c in sorted(own, key=lambda c: c.adate):
        person(authors.name(c.ae, c.an))["commits"].append(c)
    infos = []
    for m in sorted(prs, key=lambda m: m.cdate):
        buf = io.StringIO()
        info = print_pr(repo, m, authors, buf)
        info["text"] = buf.getvalue().rstrip("\n")
        infos.append(info)
        person(info["author"])["prs"].append(info)
        if info["merger_email"] != info["author_email"] and authors.known(info["merger_email"]):
            person(info["merger"])["merged"].append(info)
    if authors.present:
        roster = list(authors.order)
    else:
        window = [c for c in all_commits if day - dt.timedelta(days=30) <= repo.clock.local_date(c.adate) < day]
        roster = sorted({authors.name(c.ae, c.an) for c in window} | set(people))
        print("NOTE no authors map: roster built from every email with a commit in the 30 days before; "
              "seed the authors map", file=out)
    order = [n for n in roster if n in people] + sorted(n for n in people if n not in roster)
    for name in order:
        p = people[name]
        print(f"DEV {name}", file=out)
        for info in p["merged"]:
            print(f"  REVIEWED AND MERGED PR #{info['num']} by {info['author']} ({info['branch']})", file=out)
        for info in p["prs"]:
            print("  HEADLINE " + info["text"].strip(), file=out)
        for c in p["commits"]:
            print(f"  COMMIT {c.short} {repo.clock.local_time(c.adate)} {c.subject}", file=out)
            print(f"    {repo.placement(c, day)}; {file_summary(c.files)}", file=out)
    idle = [n for n in roster if n not in people]
    print(f"NO ACTIVITY: {', '.join(idle) if idle else DASH}", file=out)
    print(f"BRANCH REFRESHES ignored (not work): {refreshes}", file=out)


# ----------------------------------------------------------------------------------------- other commands

def cmd_status(args, settings: Settings, clock: Clock, out) -> int:
    header(settings, clock, args.log, out)
    blocked = block_if_inside(settings, out)
    if args.log == "history":
        path = settings.file("history")
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            scan = next((ln for ln in text.splitlines() if ln.startswith("**Scan state:**")), "none")
            modules = len(re.findall(r"^### ", text.split("## Detailed History", 1)[-1].split("\n## ", 1)[0], re.M))
            gaps = len(re.findall(r"^- \[ \]", text, re.M))
            print(f"SCAN STATE {scan}", file=out)
            print(f"MODULES {modules}", file=out)
            print(f"OPEN GAPS {gaps}", file=out)
        tfiles, tdirs = transcript_files(settings, project_roots(args.projects_dir))
        print("TRANSCRIPTS " + (f"{', '.join(tdirs)} ({len(tfiles)} files)" if tdirs else "none for this path"), file=out)
        print(f"INTEGRATION BRANCH {settings.integration}; mergeDeploysTo "
              f"{(settings.cfg.get('deployment') or {}).get('mergeDeploysTo')}", file=out)
        return 2 if blocked else 0
    entries = read_entries(settings.file(args.log))
    print(f"ENTRIES {len(entries)}", file=out)
    if entries:
        last = max(entries)
        missing = [d for d in span(last + dt.timedelta(days=1), clock.today) if is_working(d, settings.cfg)]
        print(f"LAST {last.isoformat()} ({(clock.today - last).days} calendar days ago, "
              f"{len(missing)} working days missing)", file=out)
        print("MISSING (not yet checked for evidence) " + (", ".join(d.isoformat() for d in missing) or "none"),
              file=out)
        prov = [d.isoformat() for d, k in entries.items() if k == "provisional"]
        if prov:
            print(f"PROVISIONAL {', '.join(sorted(prov))}", file=out)
    if args.log == "scrum":
        tfiles, tdirs = transcript_files(settings, project_roots(args.projects_dir))
        print("TRANSCRIPTS " + (f"{', '.join(tdirs)} ({len(tfiles)} files)" if tdirs else
                                "unavailable: every run will rely on Git alone"), file=out)
    if args.log == "team":
        authors = Authors(settings.cfg.get("authors"))
        print(f"KNOWN DEVS {', '.join(authors.order) if authors.present else 'none - the authors map is not set'}",
              file=out)
        if settings.repo:
            for c in git_log(Git(settings.repo), "--branches", "--remotes", "--no-merges",
                             f"--since={clock.day_start(clock.today - dt.timedelta(days=30))}"):
                authors.name(c.ae, c.an)
            for email, name in sorted(authors.unmapped.items()):
                print(f"UNMAPPED {name} <{email}>", file=out)
    return 2 if blocked else 0


def cmd_has_entry(args, settings: Settings, clock: Clock, out) -> int:
    day = dt.date.fromisoformat(args.date)
    state = read_entries(settings.file(args.log)).get(day)
    print({None: "ABSENT", "final": "EXISTS", "provisional": "PROVISIONAL"}[state], file=out)
    return 0


def cmd_merges(args, settings: Settings, clock: Clock, out) -> int:
    header(settings, clock, None, out)
    repo = Repo(Git(settings.repo), settings, clock)
    if not repo.int_ref:
        print(f"NOTE no {settings.integration} branch found", file=out)
        return 1
    since = dt.date.fromisoformat(args.since) if args.since else None
    until = dt.date.fromisoformat(args.until) if args.until else None
    authors = Authors(settings.cfg.get("authors"))
    margs = ["--merges", "--first-parent", repo.int_ref, "--reverse"]
    if since:
        margs.append(f"--since={clock.day_start(since)}")
    if until:
        margs.append(f"--until={clock.day_end(until)}")
    for m in git_log(repo.git, *margs):
        if not pr_match(m.subject):
            continue
        print(f"{clock.local_date(m.cdate).isoformat()} {m.short}", end="", file=out)
        print_pr(repo, m, authors, out)
    return 0


def cmd_pr_authors(args, settings: Settings, clock: Clock, out) -> int:
    repo = Repo(Git(settings.repo), settings, clock)
    m = git_log(repo.git, "-1", args.merge)[0]
    if not m.is_merge:
        print(f"NOTE {m.short} is not a merge commit", file=out)
        return 1
    authors = Authors(settings.cfg.get("authors"))
    info = repo.pr_authors(m, args.paths or None)
    total = info["total"] or 1
    print(f"PR {m.subject}", file=out)
    print(f"MERGED {clock.local_date(m.cdate).isoformat()} by {authors.name(m.ce, m.cn)}"
          + (f"; scoped to {' '.join(args.paths)}" if args.paths else ""), file=out)
    for email, n in info["counts"]:
        share = 100 * n / total
        print(f"  {authors.name(email, info['names'][email])}: {n}/{info['total']} ({share:.0f}%)"
              f"{' - listed (>=20%)' if share >= 20 else ''}", file=out)
    if info["author"]:
        print(f"AUTHOR {authors.name(info['author'], info['names'].get(info['author'], m.an))}"
              f"{' (tie: %ae decided)' if info['tie'] else ''}", file=out)
    return 0


def cmd_deploys(args, settings: Settings, clock: Clock, out) -> int:
    header(settings, clock, None, out)
    files, dirs = transcript_files(settings, project_roots(args.projects_dir))
    if not dirs:
        print("LEDGER EMPTY no transcripts for this repository path (machine-local evidence)", file=out)
        return 0
    rows, stats = deploy_ledger(files, clock, args.since)
    print(f"SCANNED {len(files)} transcripts in {', '.join(dirs)}; {stats['hits']} Environment blocks: "
          f"{stats['echoes']} template echoes, {stats['not_deployed']} NOT deployed / Deploy FAILED, "
          f"{stats['no_verdict']} with no verdict line above - all discarded; {len(rows)} deploys after dedupe",
          file=out)
    for r in rows:
        print(f"DEPLOY {r['date'].isoformat()} {r['time']} {r['env']} {r['branch'] or '-'} {r['commit']} | "
              f"{r['verdict']} | session {r['session']}", file=out)
    for c in stats["candidates"]:
        print(f"CANDIDATE {c['date'].isoformat()} {c['time']} {c['env']} {c['branch'] or '-'} {c['commit']} | "
              f"no verdict line above it - read session {c['session']} before using it; Inferred at best", file=out)
    if rows:
        print(f"WATERMARK transcripts<={rows[-1]['stamp']}", file=out)
    return 0


# ----------------------------------------------------------------------------------------- entry point

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--repo", help="repository path (default: the current directory)")
    p.add_argument("--config", default=str(DEFAULT_CONFIG))
    p.add_argument("--dir", help="one-off output directory for this run (not persisted)")
    p.add_argument("--now", help="pretend it is this UTC instant (tests)")
    p.add_argument("--projects-dir", action="append", help="Claude Code projects folder (repeatable)")
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("evidence", "dates"):
        s = sub.add_parser(name)
        s.add_argument("--log", choices=["scrum", "team"], required=True)
        s.add_argument("--full", action="store_true", help="no caps on transcript text")
        s.add_argument("--prompt-chars", type=int, default=400)
        s.add_argument("--final-chars", type=int, default=700)
        s.add_argument("--max-prompts", type=int, default=12)
        s.add_argument("spec", nargs="*")
    s = sub.add_parser("status")
    s.add_argument("--log", choices=["scrum", "team", "history"], required=True)
    s = sub.add_parser("has-entry")
    s.add_argument("--log", choices=["scrum", "team"], required=True)
    s.add_argument("date")
    s = sub.add_parser("merges")
    s.add_argument("--since")
    s.add_argument("--until")
    s = sub.add_parser("pr-authors")
    s.add_argument("merge")
    s.add_argument("paths", nargs="*")
    s = sub.add_parser("deploys")
    s.add_argument("--since", help="only transcript lines after this ISO instant (the scan watermark)")
    return p


def main(argv: list[str] | None = None, out=None) -> int:
    out = out or sys.stdout
    if hasattr(out, "reconfigure"):
        try:
            out.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    args = build_parser().parse_args(argv)
    settings = resolve_settings(args.repo, Path(args.config), args.dir)
    clock = Clock(parse_now(args.now), settings.tz)
    try:
        if args.command in ("evidence", "dates"):
            args.dates_only = args.command == "dates"
            return evidence(args, settings, clock, out)
        if args.command == "status":
            return cmd_status(args, settings, clock, out)
        if args.command == "has-entry":
            return cmd_has_entry(args, settings, clock, out)
        if settings.repo is None:
            print("NOTE not inside a git repository", file=out)
            return 1
        return {"merges": cmd_merges, "pr-authors": cmd_pr_authors, "deploys": cmd_deploys}[args.command](
            args, settings, clock, out)
    except (GitError, ValueError) as exc:
        print(f"ERROR {exc}", file=out)
        return 1


if __name__ == "__main__":
    sys.exit(main())
